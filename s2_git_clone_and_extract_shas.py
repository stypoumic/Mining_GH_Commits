import os
import subprocess
from pydriller.domain.commit import ModificationType
from pydriller import RepositoryMining, GitRepository
from properties import cloneFolderPath, gitExecutablePath


def get_number_of_modified_lines(thecode):
	addeletions = [1 if line.startswith("+") or line.startswith("-") else 0 for line in thecode.splitlines()[1:]]
	return sum(addeletions)

def process_repo(repo_address):
	repo_name = '_'.join(repo_address.split('/')[-2:])
	print("\nProcessing repo " + repo_name)

	# Set paths
	git_repo_path = os.path.join(cloneFolderPath, repo_name)
	sha_path = os.path.join(cloneFolderPath + "shas_files/", repo_name + "_shas.csv")

	if not os.path.exists(git_repo_path):
		print("Downloading...")
		# Download repo
		p = subprocess.Popen([gitExecutablePath, 'clone', repo_address, git_repo_path], stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		while True:
			line = p.stdout.readline()
			if line == b'':
				break
		print("Done!")

	# Get repo commits
	total = GitRepository(git_repo_path).total_commits()
	print("Processing " + str(total) + " commits...")
	repomining = RepositoryMining(git_repo_path, only_modifications_with_file_types=['.java'])
	with open(sha_path, 'w') as outfile:
		for commit in repomining.traverse_commits():
			if commit.in_main_branch:
				if len(commit.modifications) == 1: # if it is single-file commit
					modification = commit.modifications[0]
					if modification.change_type == ModificationType.MODIFY: # if it is modified (not added or deleted)
						sha = commit.hash
						code_diff = "\n".join(modification.diff.splitlines())
						if get_number_of_modified_lines(code_diff) <= 100:
							outfile.write(sha + "\n")

	print("Done!")

with open("repos3000Java.csv") as infile:
	lines = infile.readlines()
repos = [line.split(';') for line in lines]
if not os.path.exists(cloneFolderPath + "shas_files/"):
	os.makedirs(cloneFolderPath + "shas_files/")
for repo in repos:
    if int(repo[3])<2500:
    	try:
    	    process_repo(repo[0])
    	except:
    	    print("Error 404")
