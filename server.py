# server.py
#
# Runs all the things that a server should do, including calling the database, processing queries, communicating with the client

import socket
import sys
from _thread import *
from server_class import *
import utilities,json,os,marshal
import time
from bitstring import BitArray
import random

hashFlag = 0

if len(sys.argv) < 5:
    print( "Not enough input arguments: cubeDim,port,newDatabase")
    sys.exit()
	
cubeDim = int(sys.argv[1])
port = int(sys.argv[2])
newDatabase = int(sys.argv[3])
dbFilename = sys.argv[4]
base = int(sys.argv[5])

if len(sys.argv) >= 7:
    binSeed = int(sys.argv[6])
    nBins = int(sys.argv[7])
    hashFlag = 1  # the server should hash the results into bins
    
backlog = 5

t = time.time()
# Build the database
if newDatabase or not os.path.isfile(dbFilename+str(base)+'_db.npy'):
    f = open(dbFilename,'r')
    dbContent = f.readlines()
    f.close
    serv = Server(dbContent,cubeDim,base);
    numpy.save(dbFilename+str(base)+'_db',serv.db)
    f = open(dbFilename+'_meta','wb')
    f.write(bytes(str(serv.cubeSize)+'\n','utf-8'))
    f.write(bytes(str(serv.fileSize)+'\n','utf-8'))
    f.close()
    sys.exit()
else:
    db = numpy.load(dbFilename+str(base)+'_db.npy')
    f = open(dbFilename+'_meta','r')
    cubeSize = int(f.readline())
    fileSize = int(f.readline())
    f.close()
    serv = Server(db,cubeDim,base,fileSize)
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

# try:
	# s.connect((host,port))
	# print "connected to port ",port
# except socket.error , msg:
	# print 'Connection failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
	# print port,host
	# raw_input('heres where the connection failed')
	# sys.exit()
# print 'Socket connection complete'
# print 'Connecting', time.time()-t
# t = time.time()

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

# # run the PIR query

if not hashFlag:
    result = serv.submitPirQuery(query,base).tolist()
    result = [int(a) for a in result]
else:
    # generate the mapping from database elements to bins
    random.seed(binSeed)
    print('cubesize is ',serv.cubeSize)
    binExpansion = 3
    bins = [[] for i in range(nBins)]
    for fileIdx in range(serv.nBlocks):
        for c in range(binExpansion):
            randBin = random.randint(0,nBins-1)
            while fileIdx in bins[randBin]:
                randBin = random.randint(0,nBins-1)
            bins[randBin].append(fileIdx)
    # print('bins is ',bins)
    result = serv.submitPirQueryHash(query,base,bins)
    # print('result is ',result)
    # print('result dims',[len(item) for item in result])

t = time.time()-t
f.write(str(t)+'\n')
f.close()

# return the result to the client
print ('size result',len(result),len(marshal.dumps([port]+result)), len(marshal.loads(marshal.dumps([port]+result))))
# print('result is',result[0][:10])
# client_socket.send(marshal.dumps([port]+result))
utilities.send_msg(client_socket,marshal.dumps([port]+result))

t = time.time()
client_socket.close()