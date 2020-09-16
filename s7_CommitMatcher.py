import os
import sys
import csv
from astextractor import ASTExtractor
from properties import dataFolderPath, ASTExtractorPath, ASTExtractorPropertiesPathDetailed
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from treehelpers import ted_scores, find_additions_deletions
from texthelpers import set_max_int_for_csv, execute_model, model_exists, create_model, load_model
from xmlhelpers import user_code_to_ast
from s3_extract_commit_asts import get_difference_between_asts

class CommitMatcher:
	def __init__(self):
		set_max_int_for_csv()
		lines = []
		with open(os.path.join(dataFolderPath, "rev_add_del_asts.csv"), 'r', encoding='utf-8') as infile:
			headers = {header: h for h, header in enumerate(next(infile).strip().split('\t'))}
			for l, row in enumerate(csv.reader(infile, dialect='excel', delimiter='\t')):
				if len(row) > len(headers):
					row = row[1:]
				lines.append(row)

		self.messages = [line[headers['message']] for line in lines]
		self.methods_before = [line[headers['code_before']] for line in lines]
		self.methods_after = [line[headers['code_after']] for line in lines]
		self.methods_before_ast = [line[headers['code_before_ast']] for line in lines]
		self.methods_after_ast = [line[headers['code_after_ast']] for line in lines]
		self.code_deletions = [line[headers['code_deletions']] for line in lines]
		self.code_additions = [line[headers['code_additions']] for line in lines]
		self.code_deletions_ast = [line[headers['code_deletions_ast']] for line in lines]
		self.code_additions_ast = [line[headers['code_additions_ast']] for line in lines]

		self.ast_extractor = ASTExtractor(ASTExtractorPath, ASTExtractorPropertiesPathDetailed)
		if not model_exists('tfidf_comments'):
			create_model('tfidf_comments', self.messages)
		self.comment_vectorizer = load_model('tfidf_comments')
		self.comment_tfidf_model = execute_model(self.comment_vectorizer, self.messages)

	def message_score(self, message):
		try:
			comment_tfidf_model_doc = execute_model(self.comment_vectorizer, [message])
			message_score = cosine_similarity(self.comment_tfidf_model, comment_tfidf_model_doc)
			return [m[0] for m in message_score]
		except:
			sys.exit("There was an error with message score!")

	def code_before_score(self, code_before):
		try:
			code_before_ast = user_code_to_ast(self.ast_extractor, code_before)
			befores = []
			befores.append(code_before_ast)
			for ast in self.methods_before_ast:
				befores.append(ast)
			sc = ted_scores(befores, 0)
			return sc[1:]
		except:
			sys.exit("There was an error with code before score!")

	def code_after_score(self, code_after):
		try:
			code_after_ast = user_code_to_ast(self.ast_extractor, code_after)
			afters = []
			afters.append(code_after_ast)
			for ast in self.methods_after_ast:
				afters.append(ast)
			sc = ted_scores(afters, 0)
			return sc[1:]
		except:
			sys.exit("There was an error with code after score!")

	def code_deletions_score(self, code_deletions, code_before, code_after):
		try:
			if(code_deletions != None):
				code_deletions_ast = user_code_to_ast(self.ast_extractor, code_deletions)
				deletions = []
				deletions.append(code_deletions_ast)
				for ast in self.code_deletions_ast:
					deletions.append(ast)
				sc = ted_scores(deletions, 0)
				return sc[1:]
			elif(code_before!=None and code_after!=None):
				deletions, additions = find_additions_deletions(code_before, code_after)
				code_before_ast = user_code_to_ast(self.ast_extractor, code_before)
				code_after_ast = user_code_to_ast(self.ast_extractor, code_after)
				_, code_deletions_ast = get_difference_between_asts(code_before_ast, code_after_ast, additions!='', deletions!='')

				deletions = []
				deletions.append(code_deletions_ast)
				for ast in self.code_deletions_ast:
					deletions.append(ast)
				sc = ted_scores(deletions, 0)
				return sc[1:]
			else:
				sys.exit("You must provide either code deletions or code before and code after!")
		except:
			sys.exit("There was an error with code deletions score!")

	def code_additions_score(self, code_additions, code_before, code_after):
		try:
			if(code_additions != None):
				code_additions_ast = user_code_to_ast(self.ast_extractor, code_additions)
				additions = []
				additions.append(code_additions_ast)
				for ast in self.code_additions_ast:
					additions.append(ast)
				sc = ted_scores(additions, 0)
				return sc[1:]
			elif(code_before!=None and code_after!=None):
				deletions, additions = find_additions_deletions(code_before, code_after)
				code_before_ast = user_code_to_ast(self.ast_extractor, code_before)
				code_after_ast = user_code_to_ast(self.ast_extractor, code_after)
				code_additions_ast, _ = get_difference_between_asts(code_before_ast, code_after_ast, additions!='', deletions!='')

				additions = []
				additions.append(code_additions_ast)
				for ast in self.code_additions_ast:
					additions.append(ast)
				sc = ted_scores(additions, 0)
				return sc[1:]
			else:
				sys.exit("You must provide either code additions or code before and code after!")
		except:
			sys.exit("There was an error with code additions score!")

	def search(self, message=None, code_before=None, code_after=None, code_deletions=None, code_additions=None, score_by={'message': False, 'code_before': False, 'code_after': False, 'code_deletions': False, 'code_additions': False}):
		results = []
		scores = [0 for m in self.messages]
		counter = 0

		if(score_by.get('message')):
			if(message!=None):
				message_score = self.message_score(message)
				scores = [sum(values) for values in zip(scores, message_score)]
				counter += 1
			else:
				sys.exit("You must provide a message!")
		if(score_by.get('code_before')):
			if(code_before!=None):
				code_before_score = self.code_before_score(code_before)
				scores = [sum(values) for values in zip(scores, code_before_score)]
				counter += 1
			else:
				sys.exit("You must provide the code before!")
		if(score_by.get('code_after')):
			if(code_after != None):
				code_after_score = self.code_after_score(code_after)
				scores = [sum(values) for values in zip(scores, code_after_score)]
				counter += 1
			else:
				sys.exit("You must provide the code after!")
		if(score_by.get('code_deletions')):
			code_deletions_score = self.code_deletions_score(code_deletions, code_before, code_after)
			scores = [sum(values) for values in zip(scores, code_deletions_score)]
			counter += 1
		if(score_by.get('code_additions')):
			code_additions_score = self.code_additions_score(code_additions, code_before, code_after)
			scores = [sum(values) for values in zip(scores, code_additions_score)]
			counter += 1
		if(counter != 0):
			scores = [(value/counter) for value in scores]

		for ind, m in enumerate(self.messages):
			results.append((m, self.methods_before[ind], self.methods_after[ind], self.code_deletions[ind], self.code_additions[ind], scores[ind]))
		results.sort(key=lambda rs: rs[5], reverse=True)

		return results
