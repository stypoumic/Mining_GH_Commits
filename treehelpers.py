import re
import sys
import string
import traceback
from PyGram import Profile
import xml.etree.ElementTree as ET
from difflib import Differ


def ast_to_node_tree(ast, keep_labels = False):
	from tree import Node, split_tree
	def get_node_tree_from_xml(root):
		currentnode = Node(str(root.tag.title()))
		text = root.attrib.get('name', root.text)
		if keep_labels and text != None and len(text.strip()) > 0:
			split_camel_case = lambda x: [m.group(0).lower() for m in re.finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', x)]
			text = text.translate({ord(c): ' ' for c in string.punctuation})
			tokens = [split_camel_case(t) for t in text.split()]
			tokens = [item for sublist in tokens for item in sublist if len(item) > 0]
			if len(tokens) > 0:
				currentnode.addkid(Node("~".join(tokens)))
		children = list(elem for elem in root)
		if len(children) > 0:
			for elem in children:
				currentnode.addkid(get_node_tree_from_xml(elem))
		return split_tree(currentnode) if keep_labels else currentnode

	try:
		if ast != -1 and ast != "-1":
			tree = ET.fromstring("<ROOT>" + ast + "</ROOT>")
			btree = get_node_tree_from_xml(tree)

			return btree
		else:
			return -1
	except:
		return -1
		print("Could not convert the following ast to node tree:\n")
		print(ast + "\n")
		print("Exiting...\n")
		sys.exit(traceback.format_exc())



def ted_score(a, b, algorithm):
	if algorithm == "pqgrams-with-content":
		return ted_score_pq(a, b, False)
	elif algorithm == "pqgrams":
		return ted_score_pq(a, b, True)


def ted_scores(X, i):
	return [ted_score(X[i], cs, "pqgrams-with-content") for cs in X]

def ted_score_pq(a, b, use_only_structure = True):
	a, b = ast_to_node_tree(a, not use_only_structure), ast_to_node_tree(b, not use_only_structure)
	try:
		if len(str(a)) < 3 or len(str(b)) < 3:
			return 0
		
		ted = Profile(a).edit_distance(Profile(b))
		# Normalize according to "Nikolaus Augsten and Michael H. Bhlen. 2013. Similarity Joins in Relational Database Systems (1st. ed.)"
		return 1 - ted
	except:
		return 0
		def print_tree(tree, pr = ""):
			print(pr + tree.label)
			pr += "  "
			for child in tree.children:
				print_tree(child, pr)

		print("Could not compute the tree edit distance between the following trees:\n")
		print("TREE 1:\n")
		print_tree(a)
		print("\nTREE 2:\n")
		print_tree(b)
		print("\nExiting...\n")
		sys.exit(traceback.format_exc())


def find_additions_deletions(code_before, code_after):
	d = Differ()
	differences = list(
		d.compare(code_before.splitlines(1), code_after.splitlines(1)))
	deletions = ''
	additions = ''
	for d in differences:
		if(d[0] == '+'):
			additions += d[1:-1]
		elif(d[0] == '-'):
			deletions += d[1:-1]
	return deletions, additions


