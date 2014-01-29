from utilities import *
import random
import socket, select
import sys, os
import json,marshal
import time

def recv_timeout(the_socket,data_size,timeout=2):
    #make socket non blocking
    the_socket.setblocking(0)
     
    #total data partwise in an array
    total_data=[];
    data='';
     
    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break
         
        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            print('TIMEOUT, NO DATA')
            break
         
        #recv something
        try:
            # data = the_socket.recv(data_size)
            data = the_socket.recv()
            if data:
                # total_data.append(data)
                total_data = total_data + data
                #change the beginning time for measurement
                begin=time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
     
    #join all parts to make final string
    # return ''.join(total_data)
    print('\n\ntotal data is ',total_data)
    return total_data

def generatePirQueries(searchIndex, numServers, cubeDim, queryDim,base):
	# generates one PIR query for each cache node
	polyDim = int((numServers-1)/cubeDim)
	# find the appropriate indices of the query file in the database
	sq = pow(queryDim,2)
	i = int(searchIndex / sq)
	j = int((searchIndex % sq) / queryDim)
	k = int(searchIndex % queryDim)
	print ('desired indices are',i,j,k)
	# find the canonical vectors
	e = []
	equery = [0 for l in range(queryDim)]
	equery[i] = 1
	e.append( equery )
	equery = [0 for l in range(queryDim)]
	equery[j] = 1;
	e.append(equery)
	equery = [0 for l in range(queryDim)]
	equery[k] = 1;
	e.append(equery)
	
	# find the random strings for each dimension of the cube
	a = [[]]*polyDim
	for p in range(polyDim):
		a_temp = []
		for r in range(cubeDim):
			# change this to random integers in GF(base)
			# a_temp.append( [random.randint(0,base-1) for q in range(0,queryDim)] )
			a_temp.append( [0 for q in range(0,queryDim-1)] + [1] )
		a[p] = a_temp
	# raw_input('here')
		
	# add multiples of the random string to the desired vector
	queries = [[]]*numServers
	queries[0] = a[-1]
	# print 'before',queries
	# print 'polydim is',polyDim
	for r in range(1,numServers):
		dimQuery = copy.deepcopy(e)
		# print 'e is',e
		r_pow = 1
		# print 'server',r
		for deg in range(polyDim):
			r_pow = multGf(r_pow,r,base)
			# print 'r_pow is ',r_pow
			for q in range(0,cubeDim):
				# print dimQuery[q],'and',a[deg][q]
				dimQuery[q] = ( [multGf(r_pow,x,base) ^ y for x,y in zip( a[deg][q] , dimQuery[q] ) ]) # make this addition in GF4
		queries[r] = dimQuery
		# print 'r is ',r,'query is \n',queries
	# print 'queries is',queries
	# raw_input('hi here ')
	return queries	

def distributePirQueries(numServers,cubeDim,pirQueries,BASE_PORT):

    ports = []
    for i in range(numServers):
        ports.append(BASE_PORT+i);
    print (ports)
    sock_lst = []
    host = ''
    backlog = 5 # Number of clients on wait.
    buf_size = 20000
    buf_size = 10255
    errorFlag = 0
    print ('NUM SERVERS IS',numServers)
    try:
        for port in ports:
            sock_lst.append(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
            host = socket.gethostname()
            sock_lst[-1].connect((host,port))
            print ('Connected to socket ',port)
            sock_lst[-1].send(marshal.dumps(pirQueries.pop(0)))
            # sock_lst[-1].bind((host, item)) 
            # sock_lst[-1].listen(backlog)
            # print "bound socket ",item
    except socket.error as message:
        if sock_lst[-1]:
            sock_lst[-1].close()
            sock_lst = sock_lst[:-1]
        print ('Could not connect to socket: ')# + message.args)
        sys.exit(1)


    # sumbit the PIR queries to each server and collect the results	

    result_cnt = 0;
    results = [[]]*numServers	
    while result_cnt < numServers:
        # read, write, error = select.select(sock_lst,[],[])
        inputready,outputready,exceptready = select.select(sock_lst,[],[]) 
        for r in inputready:
            print('buf size is ',buf_size)
            data = r.recv(buf_size)
            # data = recv_timeout(r,buf_size,5)  # THIS DOESN'T WORK FOR SOME REASON
            print('data size is ',len(data))
            if data:
                try:
                    res = marshal.loads(data)
                except ( EOFError, ValueError, TypeError) as m:
                    print ('\n\nMAJOR ERROR ',len(data),data[len(data)-10:len(data)+4] ,'\n\n')
                    print ('Error message: ',m)
                    # print ('type',type(data))
                    # print ('The received data was ',data,len(data),'\n\n')
                    errorFlag = 1
                    return([],errorFlag)
                rPort = int(res.pop(0)) - BASE_PORT
                results[rPort] = res
                # print('res is ',res,rPort)

                result_cnt = result_cnt + 1
            else:
                print('No data in client.py')
            r.close()
            sock_lst.remove(r)
            if not sock_lst:
                break
    # close all the server sockets
    for item in sock_lst:
        item.close()
        
    return (results,errorFlag)
		
	
if len(sys.argv) < 5:
    print ("Not enough input arguments: numServers,cubeDim,queryDim,BASE_PORT")
    sys.exit()

numServers = int(sys.argv[1])
cubeDim = int(sys.argv[2])
queryDim = int(sys.argv[3])		
BASE_PORT = int(sys.argv[4])	
base = int(sys.argv[5])	


searchIndex = 0

t1 = time.time()

# generate the PIR queries
pirQueries = generatePirQueries(searchIndex,numServers,cubeDim,queryDim,base)
print('queries',pirQueries)

# submit the queries to the servers
results,errorFlag = distributePirQueries(numServers,cubeDim,pirQueries,BASE_PORT)
if not errorFlag:
    fileSize = len(results[0])
    PIR_result = numpy.zeros((fileSize),dtype=numpy.uint8)
    PIR_result = [0]*fileSize
    if (base == 4) or (base==2):
        for s in range(numServers):
            PIR_result = [a^b for a,b in zip(PIR_result , results[s])]
    elif base == 16:
        if numServers==4:
            scale = [6,1,1,1]
        elif numServers == 7:
            scale = [6,7,13,11,10,12,6]
        elif numServers == 10:
            scale = [4,1,2,2,13,13,10,10,4,4]
        elif numServers == 13:
            scale = [10,5,7,10,10,13,8,6,4,14,9,10,9]
        elif numServers == 16:
            scale = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]		
        # now combine the results appropriately
        for s in range(numServers):
            PIR_result = [a^utilities.multGf(scale[s],b,base) for a,b in zip(PIR_result , results[s])]	
                
    PIR_result = ''.join([chr(z) for z in PIR_result])
    print ('pir result is ',PIR_result[:10])


    # print '\n\nYour local result is: ',PIR_result

    # measure the total time
    t2 = time.time()
    dt = t2-t1
    print ('Runtime is ',dt)
    f = open('tot_times.txt','a')
    f.write(str(dt)+'\n')
    f.close()