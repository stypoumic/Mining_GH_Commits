from pandas import DataFrame
from properties import dataFolderPath,user,password,host,port,database,sha_linkage
import psycopg2
from texthelpers import  set_max_int_for_csv
set_max_int_for_csv()

conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)
cur = conn.cursor()
conn.autocommit = True


if sha_linkage:
    sql="""SELECT file_revision.sha
    FROM file_revision  INNER JOIN revision ON (file_revision.sha = revision.id );
    ;"""      
else:
    sql="""SELECT sha FROM public.file_revision;"""           
cur.execute(sql)
mview = cur.fetchall()
for x in range(0, len(mview)):
    mview[x] = ("\\x"+mview[x][-1].hex()) 
#Get  values from db and create revisions.csv
    
if sha_linkage:
    sql="""SELECT file_revision.sha,file_revision.filename,file_revision.message,file_revision.code_diff,
    file_revision.code_additions_ast,file_revision.code_deletions_ast,file_revision.method_code_before,
    file_revision.method_code_after,file_revision.method_code_before_ast,file_revision.method_code_after_ast
    FROM file_revision  INNER JOIN revision ON (file_revision.sha = revision.id );
    ;""" 
else:
    sql="""SELECT * FROM public.file_revision;""" 
cur.execute(sql)

print("Done Reading from DB!")

df_ID = DataFrame(mview)                    
df = DataFrame(cur.fetchall())
df.columns = [cur.description[0][0], cur.description[1][0], cur.description[2][0],cur.description[3][0],cur.description[4][0],cur.description[5][0], \
              cur.description[6][0],cur.description[7][0],cur.description[8][0],cur.description[9][0],]
df = df.assign(sha=df_ID)
df = df.set_index("sha", drop = True)
df.to_csv(dataFolderPath + 'revisions.csv', sep='\t', encoding='utf-8')
print("Done!")
