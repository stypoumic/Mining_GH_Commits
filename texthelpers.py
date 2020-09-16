import os
import re
import sys
import csv
import pickle
import string
from difflib import Differ, SequenceMatcher
import nltk
#nltk.download('punkt')
from nltk import word_tokenize
from properties import dataFolderPath
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from lxml import etree
from collections import Counter

def camel_case_split(identifier):
	matches = re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
	return [m.group(0).lower() for m in matches]

def process_text(text, stem = True, removestopwords = True, splitcamelcase = True):
	text = text.translate({ord(c): ' ' for c in string.punctuation})
	tokens = word_tokenize(text)
	if splitcamelcase:
		tokens = [camel_case_split(t) for t in tokens]
		tokens = [item for sublist in tokens for item in sublist]

	if removestopwords:
		tokens = [t for t in tokens if t not in stopwords.words('english')]

	if stem:
		stemmer = PorterStemmer()
		tokens = [stemmer.stem(t) for t in tokens]

	return tokens

def cos_sim(X, i, j = None):
	if j != None:
		return cosine_similarity(X[i], X[j])[0][0]
	return cosine_similarity(X[i], X)[0]

def create_model(model_name, texts):
	vectorizer = TfidfVectorizer(tokenizer=process_text, max_df=0.5, min_df=10, lowercase=True)
	tfidf_model = vectorizer.fit(texts)
	pickle.dump(vectorizer, open(os.path.join(dataFolderPath, model_name + ".pkl"),"wb"))

def model_exists(model_name):
	return os.path.exists(os.path.join(dataFolderPath, model_name + ".pkl"))

def load_model(model_name):
	return pickle.load(open(os.path.join(dataFolderPath, model_name + ".pkl"), 'rb'))

def execute_model(vectorizer, texts):
	return vectorizer.transform(texts)

def message_passes_filter(message):
	"""
	Functions as a filter for commit messages.
	Returns true if the message passes the filter or false otherwise.
	"""
	exact_matches = ["Archive notification", "DEPRECATED"]
	filtered_out_by_token = ["merge", "[", "typo", "javadoc", "icon", "license", "readme", "icon", "image", \
													"version", "dependen", "contributing", "changelog", "https://github.com", \
													"bump", "moving project", "move project", "pom", "travis", "jdk", "jenkins", "data dump", "#"]
	if len(message) < 10 or len(message.split()) < 3: # Drop very small commit messages
		return False
	elif len(message) > 200: # Drop very large commit messages
		return False
	elif any(message == exact_match for exact_match in exact_matches): # Drop commits with exactly the exact_matches messages
		return False
	elif any(token in message.lower() for token in filtered_out_by_token): # Drop commits that contain any term(s) in filtered_out_by_token
		return False
	else:
		return True

def set_max_int_for_csv():
	#----The csv file might contain very huge fields, therefore increase the field_size_limit----
	maxInt = sys.maxsize

	while True:
		# decrease the maxInt value by factor 10
		# as long as the OverflowError occurs.

		try:
			csv.field_size_limit(maxInt)
			break
		except OverflowError:
			maxInt = int(maxInt/10)

def num_lines_in_file(filename, is_csv = False, is_csv_gz = False):
	if is_csv:
		with open(filename, 'r', encoding='utf-8') as infile:
			for l in enumerate(csv.reader(infile, dialect='excel', delimiter='\t')):
				pass
	elif is_csv_gz:
		with gzip.open(filename, 'rt', encoding='utf-8') as infile:
			for l in enumerate(infile):
				pass
	else:
		with open(filename, 'r', encoding='utf-8') as infile:
			for l in enumerate(infile):
				pass
	return l[0] + 1

def split_code_patch(codepatch):
	try:
		code_before, code_after, code_additions, code_deletions = [], [], [], []
		for line in codepatch.splitlines():
			line = line.rstrip()
			if len(line.split("@@")) > 2:
				code_before.append(line.split("@@")[2][1:])
				code_after.append(line.split("@@")[2][1:])
			else:
				if line.startswith("+"):
					code_additions.append(line[1:])
					code_after.append(line[1:])
				elif line.startswith("-"):
					code_deletions.append(line[1:])
					code_before.append(line[1:])
				else:
					code_before.append(line[1:])
					code_after.append(line[1:])
		return "\n".join(code_before), "\n".join(code_after), "\n".join(code_additions), "\n".join(code_deletions)
	except:
		print("Could not split the following code patch:\n")
		print(codepatch + "\n")
		print("Exiting...\n")
		sys.exit(traceback.format_exc())

