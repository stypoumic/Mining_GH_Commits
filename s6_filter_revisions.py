import os
import csv
import pandas as pd
from properties import dataFolderPath
from texthelpers import num_lines_in_file, message_passes_filter, set_max_int_for_csv, split_code_patch
set_max_int_for_csv()

numlines = num_lines_in_file(os.path.join(dataFolderPath, "revisions.csv"), is_csv = True)

lines = []
print("Filtering (" + str(numlines) + " commits)")
with open(os.path.join(dataFolderPath, "revisions.csv"), 'r', encoding='utf-8') as infile:
	final_path = os.path.join(dataFolderPath, "rev_add_del_asts.csv")
	headers = {header: h for h, header in enumerate(next(infile).strip().split('\t'))}

	start = False
	for l, row in enumerate(csv.reader(infile, dialect='excel', delimiter='\t')):
		if len(row) > len(headers): row = row[1:]

		sha = row[headers['sha']].strip()
		filename = row[headers['filename']].strip('.b')
		message = row[headers['message']].strip('.b')
		if message_passes_filter(message):# and ("fix" in message or "bug" in message or "resolve" in message):
			code_diff = row[headers['code_diff']].strip('.b')
			code_additions_ast = row[headers['code_additions_ast']].strip('.b')
			code_deletions_ast = row[headers['code_deletions_ast']].strip('.b')

			method_code_before = row[headers['method_code_before']].strip('.b')
			method_code_after = row[headers['method_code_after']].strip('.b')
			method_code_before_ast = row[headers['method_code_before_ast']].strip('.b')
			method_code_after_ast = row[headers['method_code_after_ast']].strip('.b')

			_, _, code_additions, code_deletions = split_code_patch(code_diff)

			check = lambda x, y: x != -1 and x != "-1" and y != -1 and y != "-1"

			if (check(method_code_before, method_code_before_ast) and check(method_code_after, method_code_after_ast)) and \
										(check(code_additions, code_additions_ast) or check(code_deletions, code_deletions_ast)):
				if len(method_code_before.splitlines()) <= 15 and len(method_code_after.splitlines()) <= 15:
					res = [sha, filename, message, code_diff, method_code_before, method_code_after, method_code_before_ast, method_code_after_ast, \
									code_additions, code_deletions, code_additions_ast, code_deletions_ast]
					df = pd.DataFrame.from_records([res], columns=["sha", "filename", "message", "code_diff", "code_before", "code_after", "code_before_ast", "code_after_ast", \
																	"code_additions", "code_deletions", "code_additions_ast", "code_deletions_ast"])
					df = df.set_index("sha", drop = True)
					if start == False:
						df.to_csv(final_path, sep='\t', encoding='utf-8')
						start = True
					else:
						df.to_csv(final_path, sep='\t', encoding='utf-8', header=None, mode="a")

		l += 1
		if l % max(int(numlines / 100), 1) == 0:
			print("%d%%" % (100 * l / numlines))
