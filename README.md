# MiningGHCommits

This repository contains a methodology for mining GitHub Commits in order to provide recommendations for source code fixes.

### Research Overview
The introduction of online code hosting services has greatly supported agile software development. In the context of this collaborative paradigm, source code components are successively evolving by applying series of code changes in the form of commits.Our methodology focuses on exploring the potential of mining commits from GitHub in order to extract source code changes that can indicate useful code edits, or even drive bug fixing automation.We compare GitHub commits by using a similarity scheme that allows computing the similarity between commit messages and between blocks of code. Using this similarity scheme, we build a system that allows searching for similar commits and recommending source code changes and/or messages in different scenarios. Upon assessing our approach, we argue that it can be effective for identifying similarities in source code, therefore it can provide useful recommendations to the developer for applying fixes in the form of ready-to-use source code.

The complete description of our methodology is available at the publication:

This repository contains all code and instructions required to reproduce the findings of the above publication. If this seems helpful or relevant to your work, you may cite it.
### Instructions

Our methodology is applied on the Software Heritage Graph Dataset which is available [here](https://docs.softwareheritage.org/devel/swh-dataset/graph/index.html).So,the first step is to download the data dump in the PostgeSQL format.The code is actually a collection of scripts that are used to make data manipulations one after the other (we use the numbering *s1, s2, s3, ...* to dictate the order of running the scripts).

### Data Preprocessing

This step reads the Software Heritage Graph data dump and produces a new data dump, which includes only the data of the 3000 most popular Java-related GitHub Repositories and excludes the tables in the **directory** and **content** subgroups of the original dataset graph,becasause they will not be used in our analysis,which focuses on fast-extraction of commit patterns.

Before reading the dataset we have manually detected the 3000 most popular Java-related GitHub Repositories based on their number of stars which are given in csv format: `repos3000Java.csv`

Open file `properties.py` and set the variable `data_dump_original_path` to the directory where Software Heritage Graph is downloaded.Set also the variable `data_dump_final_path` to the directory where you want to save the final data dump.

Run the script `s1_preprocess_data_dumb.py` and check that the new data dump is created correctly in the new directory.

Set up a PostgreSQL server (available [here](https://www.postgresql.org/)), navigate to the new directory and follow the instructions there for creating the database and importing the data (using `load.sql`).

### Git Clone and Sha Extraction

This step reads the `repos3000Java.csv` and for every entry ,clones the given GitHub Repository keeping only single file modification commits . The sha IDs of those commits are saved in csv format for each cloned Repo as Repo_Name_shas.csv (for example the commits of the cloned Repository MiningGHCommits will be saved as MiningGHCommits_shas.csv).

Open file `properties.py` and set the variable `dataFolderPath ` to the directory where you want to save the data and the variable `gitExecutablePath` to the directory where git.exe is saved on your computer .Run the script `s2_git_clone_and_extract_shas.py` and check that the folder `shas_files`is created containing all the ***_shas.csv** files for each cloned Repository.

### Commit Abstract Syntax Tree (AST) Extraction

Download the ASTExtractor tool (available [here](https://github.com/thdiaman/ASTExtractor)), and set the variables ASTExtractorPath,ASTExtractorPropertiesPath and ASTExtractorPropertiesPathDetailed  in the `properties.py` file to the path of the **ASTExtractor-0.4.jar**,**ASTExtractor.properties** and **ASTExtractorDetailed.properties** resepectively.

Run the script `s3_extract_commit_asts.py` in order to produce the `commits_files` folder containing a ***_commits.csv** file per Repository (using the respective ***_shas.csv** file and cloned Repository)  containing the following columns:
- sha :                sha1_git   (sha1_git id of the revision)
- filename:                text   (path of the file modified by the revision)
- message:                 text   (message of the revision)
- code_diff:               text   (diff of the file as Git presents it containing code additions and deletions)
- code_additions_ast:      text   (the abstract syntax tree of the code additions of the revision)
- code_deletions_ast:      text   (the abstract syntax tree of the code deletions of the revision)
- method_code_before:      text   (the code before the revision, starting from the outer Method Declaration)
- method_code_after:       text   (the code after the revision, starting from the outer Method Declaration)
- method_code_before_ast:  text   (the abstract syntax tree of the code before the revision, starting from the outer Method Declaration)
- method_code_after_ast:   text   (the abstract syntax tree of the code after the revision, starting from the outer Method Declaration)

### Database Connection

Run the script `s4_merge_revisions_and_add_to_db.py` to produce the **merged_revisions_A.csv** and **merged_revisions_B.csv**  by merging all ***_commits.csv** files together and then import it to the PostgreSQL database by setting the relevant database connection settings in `properties.py`. Two files are created, each containing approximately half of the data because of size consraints while importing the data to PostgreSQL.This step will produce an extra table **file_revisions** in the database.

After completing the database, make sure that the relevant settings for connecting to it in file `properties.py` are set correctly.

Set also the dataFolderPath to the path where all data of the methodology are going to be stored.

Run the script `s5_extract_data_from_db.py`. This should produce a file **revisions.csv**, which includes file revisions with columns sha, filename, message, code_diff, code_additions_ast, code_deletions_ast, method_code_before, method_code_after, method_code_before_ast, method_code_after_ast for each revision.By adjusting the variable sha_linkage in `properties.py`choose between extracting revisions which are present in Software Heritage Graph Dataset or not.

### Revisions Filtering

Run the script `s6_filter_revisions.py` to  filter the **revisions.csv** and produce the **rev_add_del_asts.csv"** with the following columns:
- sha : sha1_git id of the revision
- filename: path of the file modified by the revision
- message: message of the revision
- code_diff: diff of the file as Git presents it containing code additions and deletions
- code_before: the code before the revision
- code_after: the code after the revision
- code_before_ast: the abstract syntax tree of the code before the revision
- code_after_ast: the abstract syntax tree of the code after the revision
- code_additions: the lines of code added by the revision
- code_deletions: the lines of code deleted by the revision
- code_additions_ast: the abstract syntax tree of the code additions of the revision
- code_deletions_ast: the abstract syntax tree of the code deletions of the revision

### Issuing Queries

Finally the file `s7_CommitMatcher.py` contains a class that can be used to perform queries. The users can select to execute some example queries from the examples folder or run their own.



