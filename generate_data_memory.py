# generate database that fits in memory as one data structure
import os,random
import hashlib
from global_constants import HASH_LEN

P = 4		# page size (bytes)
n = 2
digits = 3
hashBits = 4

directory = str(P)+'bytes'
# cmd = 'mkdir data/'+ directory
# print cmd
# os.system(cmd)
db_filename = 'data_memory/'+directory+'/' + str(int(n)) + 'files'
db_dir = 'data_memory/'+directory
try:
    os.stat(db_dir)
except:
    os.mkdir(db_dir) 

print ('\n\n')
f = open(db_filename,'wb')
for i in range(n):
    random_list = [random.randint(48,122) for r in range(P)]
    random_list_string = bytes(str(i).zfill(3) + ''.join(chr(item) for item in random_list),'utf-8')
    random_list_string += bytes(hashlib.md5(random_list_string[:HASH_LEN]).hexdigest()[:hashBits]+ '\n','utf-8') #
    f.write(random_list_string)
f.close()