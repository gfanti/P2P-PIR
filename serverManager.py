# server.py
#
# Runs all the things that a server should do, including calling the database, processing queries, communicating with the client

import socket
import sys
from _thread import *
from RobustDatabase import RobustDatabase
import utilities,json,os,marshal
import time
from bitstring import BitArray
import random
import numpy as np
import FiniteFieldCS

hashFlag = 0
backlog = 5

if len(sys.argv) < 5:
    print( "Not enough input arguments: cubeDim,port,newDatabase")
    sys.exit()
	

port = int(sys.argv[1])
newDatabase = int(sys.argv[2])
dbFilename = sys.argv[3]
base = int(sys.argv[4])

if len(sys.argv) >= 6:
    binSeed = int(sys.argv[5])
    nbins = int(sys.argv[6])
    hashFlag = 1  # the server should hash the results into bins

t = time.time()
# Build the database
if newDatabase or not os.path.isfile(dbFilename+str(base)+'_db.npy'):
    # Make sure that the directory actually exists
    try:
        f = open(dbFilename,'r')
    except:
        print('\n\nERROR: You need to generate the database first!\n\n')
        exit()
    dbContent = f.readlines()
    f.close
    serv = RobustDatabase(dbContent,base);
    np.save(dbFilename+str(base)+'_db',serv.db)
    f = open(dbFilename+'_meta','wb')
    f.write(bytes(str(serv.dbSize)+'\n','utf-8'))
    f.write(bytes(str(serv.fileSize)+'\n','utf-8'))
    f.close()
    sys.exit()
else:
    db = np.load(dbFilename+str(base)+'_db.npy')
    f = open(dbFilename+'_meta','r')
    f.readline()
    fileSize = int(f.readline())
    f.close()
    
    # Generate a server 
    if hashFlag:
        # generate the mapping from database elements to bins (indexed by seed, so the 
        #     client and server have the same mapping
        binExpansion = 3
        binSeed = 0
        dbSize = utilities.file_len(dbFilename)
        mapping = FiniteFieldCS.buildRandMapping(binSeed,nbins,binExpansion,dbSize)
        serv = RobustDatabase(db,base,fileSize,mapping,nbins)
    else:
        serv = RobustDatabase(db,base,fileSize)
# print 'Loading db', time.time()-t
t = time.time()
 
 
# Socket stuff
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = ''
# print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((host, port)) 
    s.listen(backlog)
    # print 'Bound socket ',port
except socket.error as message:
    s.close()
    print ('Could not open socket: ')
    print (message)
    sys.exit(1)


while 1:
    client_socket, address = s.accept()
    # print "got a connection from ",address
    break
# t=time.time()
#now collect the PIR query from the client
data = client_socket.recv(4000)
query = marshal.loads(data)

f=open(str(port)+'.txt','a')
t = time.time()

## --------------Run the PIR query---------------------##

# Check if we're running regular PIR (hashFlag=0) or hashed PIR (hashFlag=1)
if not hashFlag:
    result = serv.submitPirQuery(query,base).tolist()
    result = [int(a) for a in result]
else:
    # print('bins is ',bins)
    result = serv.submitPirQueryHash(query,base,mapping,nbins)
    # print('result is ',result)
    # print('result dims',[len(item) for item in result])

t = time.time()-t
f.write(str(t)+'\n')
f.close()
# return the result to the client
print ('size result',len(result),len(marshal.dumps([port]+result)), len(marshal.loads(marshal.dumps([port]+result))))
# print('result is',result[0][:10])
# client_socket.send(marshal.dumps([port]+result))
if hashFlag:
    result = sum(result.tolist(),[])
    msg = [port] + result
    utilities.send_msg(client_socket,marshal.dumps(msg))
else:
    utilities.send_msg(client_socket,marshal.dumps([port]+result))

t = time.time()
client_socket.close()