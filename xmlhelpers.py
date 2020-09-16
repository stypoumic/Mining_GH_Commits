import sys
import csv
import gzip
import traceback
import edit_distance
from apted.helpers import Tree
from apted import APTED, Config
import xml.etree.ElementTree as ET
from astextractor import ASTExtractor
from texthelpers import process_text
from properties import ASTExtractorPath, ASTExtractorPropertiesPath

def code_to_ast(ast_extractor, code):
	"""
	Extracts the Abstract Syntax Tree (AST) from the given source code.

	:param ast_extractor: an instance of the ast_extractor tool.
	:param code: the code of which the AST is extracted in string format.
	:returns: the Abstract Syntax Tree in string format.
	"""
	try:
		ast = ast_extractor.parse_string(code)
		final_ast = ast.splitlines()
		for block in reversed([l for l, line in enumerate(final_ast[1:]) if len(line) - len(line.lstrip(' ')) == 0 and line.startswith("</") and not line.startswith("</CompilationUnit")]):
			# closing at final_ast[block+1]
			opening = None
			for i in range(block + 1, 0, -1):
				if final_ast[i].lstrip().startswith("<" + final_ast[block+1].split("</")[1].split(">")[0] + ">"):
					opening = i
					break
			if opening:
				final_ast[opening:block + 2] = ["".join(n.rstrip() for n in final_ast[opening:block + 2])]
		return "\n".join(final_ast)
	except:
		print("Could not parse the following code:\n")
		print(code + "\n")
		print("Exiting...\n")
		sys.exit(traceback.format_exc())

def user_code_to_ast(ast_extractor, code):
	"""
	Extracts the Abstract Syntax Tree (AST) from the given source code.

	:param ast_extractor: an instance of the ast_extractor tool.
	:param code: the code of which the AST is extracted in string format.
	:returns: the Abstract Syntax Tree in string format.
	"""
	try:
		ast = ast_extractor.parse_string(code)
		final_ast = ast.splitlines()
		for block in reversed([l for l, line in enumerate(final_ast[1:]) if len(line) - len(line.lstrip(' ')) == 0 and line.startswith("</") and not line.startswith("</CompilationUnit")]):
			# closing at final_ast[block+1]
			opening = None
			for i in range(block + 1, 0, -1):
				if final_ast[i].lstrip().startswith("<" + final_ast[block+1].split("</")[1].split(">")[0] + ">"):
					opening = i
					break
			if opening:
				final_ast[opening:block + 2] = ["".join(n.rstrip() for n in final_ast[opening:block + 2])]
		myast = "\n".join(final_ast)
		myast = ast
		if not ast.lstrip().startswith("<CompilationUnit>"):
			ast = ast_extractor.parse_string("class SampleClass{\n" + code + "\n}\n")
			myast = "\n".join(ast.split("\n")[3:-3])
			if not myast.lstrip().startswith("<MethodDeclaration>"):
				ast = ast_extractor.parse_string("class SampleClass{\nvoid SampleMethod(){\n" + code + "\n}\n\n}\n")
				ast = "\n".join(ast.split("\n")[6:-4])
				myast = ast
		return myast
	except:
		print("Could not parse the following code:\n")
		print(code + "\n")
		print("Exiting...\n")
		sys.exit(traceback.format_exc())

def xml_to_str(final_xml):
	"""
	Pretty prints an XML fragment of type xml.etree.ElementTree to string format.

	:param final_xml: the XML fragment in list of nodes (xml.etree.ElementTree.Element) or full tree (xml.etree.ElementTree).
	:returns: the XML in string format without leading spaces.
	"""
	if final_xml == -1:
		return -1
	else:
		if type(final_xml) == list:
			final_xml = "<ROOT>\n" + " ".join(ET.tostring(d, encoding='unicode') for d in final_xml) + "</ROOT>"
		else:
			final_xml = "<ROOT>\n" + ET.tostring(final_xml, encoding='unicode') + "</ROOT>"
		final_ast = final_xml.splitlines()[1:-1]
		if len(final_ast) == 0:
			return -1
		elif len(final_ast) == 1:
			lead_spaces = len(final_ast[0]) - len(final_ast[0].lstrip(' '))
		else:
			lead_spaces = min(len(line) - len(line.lstrip(' ')) for line in final_ast[1:])
		return "\n".join(line[lead_spaces:] if l > 0 else line for l, line in enumerate(final_ast))

def are_equal(tree1, tree2):
	"""
	Checks if two xml trees of type xml.etree.ElementTree are equal recursively.

	:param tree1: the first tree.
	:param tree2: the second tree.
	:returns: True if the trees are equal, or False otherwise.
	"""
	if tree1.tag == tree2.tag:
		if tree1.text.strip() == tree2.text.strip():
			if tree1.text.strip():
				return True
			children1 = [child1 for child1 in tree1]
			children2 = [child2 for child2 in tree2]
			if len(children1) == len(children2):
				return all(are_equal(c1, c2) for c1, c2 in zip(children1, children2))
	return False

def have_equal_ids(node1, node2):
	"""
	Checks if two xml nodes of type xml.etree.ElementTree.Element have equal ids.

	:param node1: the first node.
	:param node2: the second node.
	:returns: True if the nodes are equal, or False otherwise.
	"""
	return str(node1).split("' at ")[-1][:-1] == str(node2).split("' at ")[-1][:-1]

def get_lowest_common_ancestor(root, nodes, return_furthest_for_one_node = False):
	"""
	return_furthest_for_one_node controls what happens if there is only one node.
	If it is True, it returns the furthest ancestor, otherwise it returns the node itself.
	"""
	if len(nodes) == 0:
		return -1
	elif len(nodes) == 1:
		previous_ancestor = nodes[0]
		if return_furthest_for_one_node:
			ancestors = get_node_ancestors(root, nodes[0])
			while len(ancestors) > 0:
				ancestor = ancestors.pop()
				if len([child for child in ancestor]) != 1:
					return previous_ancestor
				previous_ancestor = ancestor
		return previous_ancestor
	else:
		ancestor_lists = [get_node_ancestors(root, node) + [node] for node in nodes]
		ancestor_lists_sorted = sorted(ancestor_lists, key=len)
		smaller_ancestor_list, rest_of_ancestor_lists = ancestor_lists_sorted[0], ancestor_lists_sorted[1:]
		for i, elem in enumerate(smaller_ancestor_list):
			if not all(have_equal_ids(elem, ancestor_list[i]) for ancestor_list in rest_of_ancestor_lists):
				return smaller_ancestor_list[i-1]
		return smaller_ancestor_list[-1]

def ast_to_xml_tree(ast):
	"""
	Converts an Abstract Syntax Tree to an XML tree object.

	:param ast: the Abstract Syntax Tree to be converted in string format.
	:returns: the XML tree object as an xml.etree.ElementTree.
	"""
	try:
		tree = ET.fromstring(ast)
		return tree
	except:
		print("Could not parse the following AST:\n")
		print(ast + "\n")
		print("Exiting...\n")
		sys.exit(traceback.format_exc())

def get_node_ancestors(tree, node):
	"""
	Returns all the ancestors of the given XML node in the given tree.

	:param tree: the XML tree object as an xml.etree.ElementTree.
	:param node: the XML node as an xml.etree.ElementTree.Element.
	:returns: a list containing all ancestors (type xml.etree.ElementTree.Element) of the node in the tree.
	"""
	def getanc(parent, node, acc):
		if parent == node:
			return acc
		else:
			for child in parent:
				newacc = acc[:]
				newacc.append(parent)
				res = getanc(child, node, newacc)
				if res is not None:
					return res
			return None
	return getanc(tree, node, [])

def find_difference_inserted(tree1, tree2, return_also_place = False):
	"""
	Returns the difference between two XML trees. Warning: This method is not a full
	diff XML implementation. The first tree (tree1) must always be smaller than the
	second (tree2) and any nodes appearing in tree1 must also be present in tree2.
	Practically, the method returns the nodes that are present in tree2 but are not
	present in tree1.

	:param tree1: the first (smaller) tree as an xml.etree.ElementTree.
	:param tree2: the second (larger) tree as an xml.etree.ElementTree.
	:param return_also_place: controls whether to return also the place of each change in tree1 (parent node).
	:returns: a generator containing all nodes that have been added to tree2 (and are not present in tree1).
	"""
	children1 = [child1 for child1 in tree1]
	children2 = [child2 for child2 in tree2]
	if len(children1) == len(children2):
		for c1, c2 in zip(children1, children2):
			yield from find_difference_inserted(c1, c2, return_also_place)
	else:
		i, j = 0, 0
		while i < len(children1) and j < len(children2):
			if are_equal(children1[i], children2[j]):
				i += 1
				j += 1
			else:
				yield (tree1, children2[j]) if return_also_place else children2[j]
				j += 1
		while j < len(children2):
			yield (tree1, children2[j]) if return_also_place else children2[j]
			j += 1

def find_difference_inserted_deleted(tree1, tree2):
	"""
	Returns the difference between two XML trees. Practically, the method returns tuples,
	containing edit distance action (first element of tuple) and XML node (second element
	of tuple). Inserted nodes ("insert") appear only in tree2 and deleted nodes ("delete")
	appear only in tree1.

	:param tree1: the first tree as an xml.etree.ElementTree.
	:param tree2: the second tree as an xml.etree.ElementTree.
	:returns: a generator containing tuples of all nodes that are different between tree1 and tree2.
	"""
	children1 = [child1 for child1 in tree1]
	children2 = [child2 for child2 in tree2]
	for tag, i1, i2, j1, j2 in edit_distance.SequenceMatcher(children1, children2, are_equal).get_opcodes():
		if tag == "insert":
			for c in children2[j1:j2]: yield ("insert", c)
		elif tag == "delete":
			for c in children1[i1:i2]: yield ("delete", c)
		elif tag == "replace":
			if len(children1[i1:i2]) == len(children2[j1:j2]):
				for c1, c2 in zip(children1[i1:i2], children2[j1:j2]):
					if c1.tag == c2.tag and c1.text == c2.text:
						yield from find_difference_inserted_deleted(c1, c2)
					else:
						yield ("delete", c1)
						yield ("insert", c2)
			else:
				for c in children1[i1:i2]: yield ("delete", c)
				for c in children2[j1:j2]: yield ("insert", c)
