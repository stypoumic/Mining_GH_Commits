import os
import gzip
import sys
from shutil import copyfile
from properties import data_dump_original_path, data_dump_final_path


#-------Copy non-data files---------------------------------------------------------------------------------------------
for filename in os.listdir(data_dump_original_path):
    if filename.endswith('.sql') or filename.endswith('.md'):
        copyfile(data_dump_original_path + filename, data_dump_final_path + filename)


#-------Find the 3000 most popular github originated java projects------------------------------------------------------
java_ids = set()
lineList = set([line.rstrip('\n').split(';')[0] for line in open(data_dump_final_path + 'repos3000Java.csv')])
with gzip.open(data_dump_original_path + 'origin.csv.gz', 'rt') as theinput:
    for line in theinput:
        #ID: big serial id of origin
        ID=line.split(',')[0]
        url=line.split(',')[2].strip()
        if url in lineList:
            java_ids.add(ID)

#-------Write origins of 3000 most popular github originated java projects to file---------------------------------------------------
sys.stdout.write('Writing origins of 3000 most popular github originated projects to file \n')
with gzip.open(data_dump_final_path + 'origin.csv.gz', 'wt') as myfile:
    with gzip.open(data_dump_original_path + 'origin.csv.gz', 'rt') as theinput:
        for line in theinput:
            #ID: big serial id of origin
            ID=line.split(',')[0]
            if ID in java_ids:
                myfile.write(line)
sys.stdout.write('Number of lines in final table:  {} \n\n'.format(len(java_ids)))


visit_ids = set()
#-------Find origin_visits of 3000 most popular github originated java projects and write them to file-------------------------------
sys.stdout.write('Writing origin_visits to file  \n')
with gzip.open(data_dump_final_path + 'origin_visit.csv.gz', 'wt') as myfile:
    with gzip.open(data_dump_original_path + 'origin_visit.csv.gz', 'rt') as theinput:
        for line in theinput:
            #origin: big serial id of origin
            origin=line.split(',')[0]
            #snap_ID: big serial id of snapshot
            snap_ID=line.split(',')[5][:-1]
            if origin in java_ids:
                myfile.write(line)
                visit_ids.add(snap_ID)
sys.stdout.write('Number of lines in final table:  {} \n\n'.format(len(visit_ids)))


snap_ids = set()
#-------Find snapshots of 3000 most popular github originated java projects and write them to file-----------------------------------
sys.stdout.write('Writing snapshots to file \n')
with gzip.open(data_dump_final_path + 'snapshot.csv.gz', 'wt') as myfile:
    with gzip.open(data_dump_original_path + 'snapshot.csv.gz', 'rt') as theinput:
        for line in theinput:
            #ID: big serial id of snapshot
            ID=line.split(',')[0]
            if ID in visit_ids:
                myfile.write(line)
                snap_ids.add(ID)
sys.stdout.write('Number of lines in final table:  {} \n\n'.format(len(snap_ids)))


snap_brcs_ids = set()
#-------Find snapshot_branches(intermediate table) of 3000 most popular github originated java projects and write them to file-------
sys.stdout.write('Writing snapshot_branches(intermediate table) to file \n')
with gzip.open(data_dump_final_path + 'snapshot_branches.csv.gz', 'wt') as myfile:
    with gzip.open(data_dump_original_path + 'snapshot_branches.csv.gz', 'rt') as theinput:
        for line in theinput:
            #snap_ID: big serial id of snapshot
            snap_ID=line.split(',')[0]
            #brch_ID: big serial id of branch
            brch_ID=line.split(',')[1][:-1]
            if snap_ID in snap_ids:
                myfile.write(line)
                snap_brcs_ids.add(brch_ID)
sys.stdout.write('Number of lines in final table:  {} \n\n'.format(len(snap_brcs_ids)))


snap_brch_ids = set()
#-------Find snapshot_branches of 3000 most popular github originated java projects and write them to file---------------------------
sys.stdout.write('Writing snapshot branchesto file \n')
with gzip.open(data_dump_final_path + 'snapshot_branch.csv.gz', 'wt') as myfile:
    with gzip.open(data_dump_original_path + 'snapshot_branch.csv.gz', 'rt') as theinput:
        for line in theinput:
            #ID: big serial id of snapshot_branch
            ID=line.split(',')[0]
            #target: sha1_git id of target revision
            target=line.split(',')[2]
            if ID in snap_brcs_ids:
                myfile.write(line)
                snap_brch_ids.add(target)
sys.stdout.write('Number of lines in final table:  {} \n\n'.format(len(snap_brch_ids)))


rev_ids = set()
ppl_ids = set()
#-------Find revisions of 3000 most popular github originated java projects and write them to file-----------------------------------
#-------Furthermore find all authors and commiters of 3000 most popular github originated java projects---------------------------------
sys.stdout.write('Writing revisions to file \n')
with gzip.open(data_dump_final_path + 'revision.csv.gz', 'wt') as myfile:
    with gzip.open(data_dump_original_path + 'revision.csv.gz', 'rt') as theinput:
        for line in theinput:
            #rev_ID: sha1_git id of revision
            rev_ID = line.split(',')[0]
            #auth_ID: bigint id of author
            auth_ID = line.split(',')[-2]
            #com_ID: bigint id of committer
            com_ID = line.split(',')[-1][:-1]
            if rev_ID in snap_brch_ids:
                myfile.write(line)
                rev_ids.add(rev_ID)
                ppl_ids.add(auth_ID)
                ppl_ids.add(com_ID)
sys.stdout.write('Number of lines in final table:  {} \n\n'.format(len(rev_ids)))

ppl_c = 0
#------Write  people of 3000 most popular github originated java projects to file--------------------------------------------------------
sys.stdout.write('Writing people to file \n')
with gzip.open(data_dump_final_path + 'person.csv.gz', 'wt') as myfile:
    with gzip.open(data_dump_original_path + 'person.csv.gz', 'rt') as theinput:
        for line in theinput:
            #ID: bigint id of person
            ID=line.split()[0]
            if ID in ppl_ids:
                ppl_c=ppl_c+1
                myfile.write(line)
sys.stdout.write('Number of lines in final table:  {} \n\n'.format(ppl_c))


rh_c = 0
#------Write revision_history of 3000 most popular github originated java projects to file----------------------------------------------
sys.stdout.write('Writing revision_history  to file \n')
with gzip.open(data_dump_final_path + 'revision_history.csv.gz', 'wt') as myfile:
    with gzip.open(data_dump_original_path + 'revision_history.csv.gz', 'rt') as theinput:
        for line in theinput:
            #sha1_git id of revison
            ID=line.split(',')[0]
            if ID in rev_ids:
                rh_c=rh_c+1
                myfile.write(line)
sys.stdout.write('Number of lines in final table:  {} \n\n'.format(rh_c))
