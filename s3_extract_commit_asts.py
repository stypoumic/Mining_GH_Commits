import os
import sys
import traceback
import pandas as pd
from astextractor import ASTExtractor
from pydriller import RepositoryMining
from properties import cloneFolderPath, ASTExtractorPath, ASTExtractorPropertiesPathDetailed, ASTExtractorPropertiesPath
from xmlhelpers import get_lowest_common_ancestor, ast_to_xml_tree, get_node_ancestors, \
		find_difference_inserted, find_difference_inserted_deleted, code_to_ast, xml_to_str

def get_difference_between_trees(tree1, tree2, has_inserts, has_deletes, return_also_place = False):
	inserts, deletes = [], []
	if has_inserts and has_deletes:
		for a, b in find_difference_inserted_deleted(tree1, tree2):
			if a == "insert": inserts.append(b)
			elif a == "delete": deletes.append(b)
		return inserts, deletes
	elif has_inserts:
		inserts = list(find_difference_inserted(tree1, tree2, return_also_place))
		if return_also_place:
			deletes = [i for i, _ in inserts]
			inserts = [i for _, i in inserts]
		return inserts, deletes
	elif has_deletes:
		deletes = list(find_difference_inserted(tree2, tree1, return_also_place))
		if return_also_place:
			inserts = [i for i, _ in deletes]
			deletes = [i for _, i in deletes]
		return inserts, deletes
	else:
		print("Error calling function get_difference_between_trees.")
		print("At least one of has_inserts and has_deletes must be True.")
		print("Exiting...\n")
		sys.exit(traceback.format_exc())

def get_difference_between_asts(ast1, ast2, has_additions, has_deletions):
	tree1 = ast_to_xml_tree(ast1)
	tree2 = ast_to_xml_tree(ast2)
	inserts, deletes = get_difference_between_trees(tree1, tree2, has_additions, has_deletions)
	if has_additions and has_deletions:
		inserts = get_lowest_common_ancestor(tree2, inserts, True)
		deletes = get_lowest_common_ancestor(tree1, deletes, True)
	return xml_to_str(inserts), xml_to_str(deletes)

def get_method(tree1, tree1nodes):
	node_ancestors = get_node_ancestors(tree1, get_lowest_common_ancestor(tree1, tree1nodes))
	if node_ancestors != None:
		for ancestor in node_ancestors:              # If there are nested methods, node_ancestors makes sure
			if ancestor.tag == "MethodDeclaration":  # we get the outer one. Getting the inner one requires
				return ancestor                      # changing node_ancestors to reversed(node_ancestors)

def get_methods(node):
	def _find_rec(node, element):
		if node.tag == element:
			yield node
		else:
			for el in node.getchildren():
				yield from _find_rec(el, element)
	return _find_rec(node, "MethodDeclaration")

def get_methods_between_asts(code1, code2, ast1, ast2, has_additions, has_deletions):
	tree1 = ast_to_xml_tree(ast1)
	tree2 = ast_to_xml_tree(ast2)
	inserts, deletes = get_difference_between_trees(tree1, tree2, has_additions, has_deletions, True)

	method1 = get_method(tree1, deletes)
	method2 = get_method(tree2, inserts)

	if method1 != None and method2 != None:
		method1_index = [method for method in get_methods(tree1)].index(method1)
		method2_index = [method for method in get_methods(tree2)].index(method2)

		code1_ast = code_to_ast(ast_extractor2, code1)
		code1_tree = ast_to_xml_tree(code1_ast)
		methods1 = [method for method in get_methods(code1_tree)]

		code2_ast = code_to_ast(ast_extractor2, code2)
		code2_tree = ast_to_xml_tree(code2_ast)
		methods2 = [method for method in get_methods(code2_tree)]

		if len(methods1) == len(methods2) and method1_index >=0 and method1_index < len(methods1) and method2_index >=0 and method2_index < len(methods2):
			method1_code = methods1[method1_index]
			method2_code = methods2[method2_index]
			return method1_code.text, method2_code.text, xml_to_str(method1), xml_to_str(method2)
		else:
			return None, None, None, None
	else:
		return None, None, None, None

if __name__ == "__main__":
	ast_extractor = ASTExtractor(ASTExtractorPath, ASTExtractorPropertiesPathDetailed)
	ast_extractor2 = ASTExtractor(ASTExtractorPath, ASTExtractorPropertiesPath)

	if not os.path.exists(cloneFolderPath + "commits_files/"):
		os.makedirs(cloneFolderPath + "commits_files/")
	repo_shas = [repo_sha for repo_sha in os.listdir(cloneFolderPath + "shas_files/") if repo_sha.endswith("shas.csv")]
	for repo_sha in repo_shas:
		repo_name = repo_sha[:-9]
		print("\nProcessing repo " + repo_name)

		git_repo_path = os.path.join(cloneFolderPath, repo_name)
		sha_path = os.path.join(cloneFolderPath + "shas_files/", repo_sha)
		commits_path = os.path.join(cloneFolderPath + "commits_files/", repo_name + "_commits.csv")
		

		with open(sha_path) as infile:
			shas = [line.strip() for line in infile if line]
		repomining = RepositoryMining(git_repo_path, only_commits=shas)

		print("Processing " + str(len(shas)) + " commits...")
		start = False
		for c, commit in enumerate(repomining.traverse_commits()):
			modification = commit.modifications[0]

			sha = commit.hash
			filename = modification.new_path
			message = commit.msg
			code_diff = "\n".join(modification.diff.splitlines()).encode('ascii', 'ignore').decode()
			code_before = "\n".join(modification.source_code_before.splitlines()).encode('ascii', 'ignore').decode()
			code_after = "\n".join(modification.source_code.splitlines()).encode('ascii', 'ignore').decode()

			code_before_ast = code_to_ast(ast_extractor, code_before)
			code_after_ast = code_to_ast(ast_extractor, code_after)

			code_additions_ast, code_deletions_ast = -1, -1

			has_additions = any(line.lstrip().startswith("+") for line in code_diff.splitlines())
			has_deletions = any(line.lstrip().startswith("-") for line in code_diff.splitlines())

			try:
				method_code_before, method_code_after, method_code_before_ast, method_code_after_ast = \
									get_methods_between_asts(code_before, code_after, code_before_ast, code_after_ast, has_additions, has_deletions)
				if method_code_before != None:
					code_additions_ast, code_deletions_ast = get_difference_between_asts(method_code_before_ast, method_code_after_ast, has_additions, has_deletions)
			except:
				print("Could not parse commit " + sha + " of repo " + repo_name + " with the following patch:\n")
				print(code_diff + "\n")
				continue
				sys.exit(traceback.format_exc())

			if method_code_before != None:
				res = ['\\x'+sha, filename, message, code_diff, code_additions_ast, code_deletions_ast, method_code_before, method_code_after, method_code_before_ast, method_code_after_ast]
				df = pd.DataFrame.from_records([res], columns=["sha", "filename", "message", "code_diff", "code_additions_ast", "code_deletions_ast", \
													"method_code_before", "method_code_after", "method_code_before_ast", "method_code_after_ast"])
				df = df.set_index("sha", drop = True)
				if start == False:
					df.to_csv(commits_path, sep='\t', encoding='utf-8')
					start = True
				else:
					df.to_csv(commits_path, sep='\t', encoding='utf-8', header=None, mode="a")
			if c % max(int(len(shas) / 100), 1) == 0:
				print("%d%%" % (100 * c / len(shas)))

		print("Done!")

	ast_extractor.close()
	ast_extractor2.close()
