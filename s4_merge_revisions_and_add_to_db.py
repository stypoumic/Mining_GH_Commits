import os
import pandas as pd
import psycopg2
from properties import cloneFolderPath ,user,password,host,port,database
from texthelpers import  set_max_int_for_csv
set_max_int_for_csv()

cloneFolderPath  = cloneFolderPath  + "commits_files/"

repo_commits = [repo_commit for repo_commit in os.listdir(cloneFolderPath ) if repo_commit.endswith("commits.csv")]

#Two seperate revision files are created because of size constraints while copying data in postgresql
start = False
for c, repo_commit in enumerate(repo_commits[1:1000]):
	commits_path = os.path.join(cloneFolderPath, repo_commit)
	final_path = os.path.join(cloneFolderPath, "merged_revisions_A.csv")

	df = pd.read_csv(commits_path, sep='\t', encoding='utf-8')
	df = df.set_index("sha", drop = True)
	if start == False:
		df.to_csv(final_path, sep='\t', encoding='utf-8')
		start = True
	else:
		df.to_csv(final_path, sep='\t', encoding='utf-8', header=None, mode="a")
	c += 1
	if c % max(int(len(repo_commits) / 100), 1) == 0:
		print("%d%%" % (100 * c / len(repo_commits)))
print("Done!")

start = False
for c, repo_commit in enumerate(repo_commits[1000:]):
	commits_path = os.path.join(cloneFolderPath, repo_commit)
	final_path = os.path.join(cloneFolderPath, "merged_revisions_B.csv")

	df = pd.read_csv(commits_path, sep='\t', encoding='utf-8')
	df = df.set_index("sha", drop = True)
	if start == False:
		df.to_csv(final_path, sep='\t', encoding='utf-8')
		start = True
	else:
		df.to_csv(final_path, sep='\t', encoding='utf-8', header=None, mode="a")
	c += 1
	if c % max(int(len(repo_commits) / 100), 1) == 0:
		print("%d%%" % (100 * c / len(repo_commits)))
print("Done!")


#connect to db
conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
cur = conn.cursor()
conn.autocommit = True

#create table
sql1 ="""create table file_revision
(
  sha                     sha1_git not null ,
  filename                text not null,
  message                 text,
  code_diff               text,
  code_additions_ast      text,
  code_deletions_ast      text,
  method_code_before      text,
  method_code_after       text,
  method_code_before_ast  text,
  method_code_after_ast   text
);"""
cur.execute(sql1)


#copy data from revisions_A.csv
sql2 ="""copy file_revision(sha, filename, message, code_diff, code_additions_ast, code_deletions_ast,method_code_before
,method_code_after,method_code_before_ast,method_code_after_ast) 
from 'path/to/merged_revisions_A.csv' delimiter '\t' csv header ;"""
cur.execute(sql2)

#copy data from revisions_B.csv
sql3 ="""copy file_revision (sha, filename, message, code_diff, code_additions_ast, code_deletions_ast,method_code_before
,method_code_after,method_code_before_ast,method_code_after_ast) 
from 'path/to/merged_revisions_B.csv' delimiter '\t' csv header ;"""
cur.execute(sql3)


#close connection
conn.close()
