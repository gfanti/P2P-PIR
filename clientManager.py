from utilities import *
import random
import socket, select
import sys, os
import json,marshal
import time

    
def generatePirQueries(searchIndex, dbSize, numServers, base):
    """ Generates one PIR query for each server in the system"""
    a = [[] for i in range(numServers-1)]
    q = [[] for i in range(numServers)]
    
    # generate the indicator vector for desired file
    e = []
    equery = [0 for l in range(dbSize)]
    equery[searchIndex] = 1
    e.append( equery )
    
    # generate the shares for masking
    for i in range(numServers-1):
        a[i] = [random.randint(0,base-1) for q in range(0,dbSize)]
        a[i] = [5 for q in range(0,dbSize)]
        a[i][1] = 0#base-1
        
    # if there are only 2 servers, we don't need to worry about collusion, and just use a and a+e_i
    if numServers == 2:
        q[0] = [item for item in a[0]];
        q[1] = [item for item in a[0]];
        q[1][searchIndex] = (q[1][searchIndex] + 1) % base
    # if there are more than 2 servers, we use shamir secret sharing
    else:
        # construct the related polynomials
        print('generatePIRqueries is possibly not done yet!')
        for i in range(numServers):
            x = i+1
            q[i] = [item for item in equery]
            for j in range(1,numServers):
                xeval = pow(x,j)
                q[i] = [(a+b)%base for (a,b) in zip(q[i],[xeval*c for c in a[j]])] # add term in polynomial
    # print(' queries are',q)
    return q
    
def onionPeel(PIR_result, searchIndex, bins, hashLength):
    retrieved = 0
    while not retrieved:
        for binIdx in range(len(bins)):
            if utilities.isSingleton(PIR_result[binIdx],hashLength):
                print("singleton")
                if searchIndex in bins[binIdx]:
                    retrieved = 1
                    break
                # # Remove the singleton from the other bins
                # singletonId
                # locations
                # PIR_result[binIdx] -= 
                # break
            retrieved = 1
    return PIR_result

def distributePirQueries(numServers,pirQueries,BASE_PORT):

    ports = []
    for i in range(numServers):
        ports.append(BASE_PORT+i);
    print (ports)
    sock_lst = []
    host = ''
    backlog = 5 # Number of clients on wait.
    buf_size = 20000
    # buf_size = 10255
    buf_size = 123000
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
            # print('buf size is ',buf_size)
            # data = r.recv(buf_size)
            data = recv_msg(r)  # THIS DOESN'T WORK FOR SOME REASON
            
            # print('data size is ',len(data))
            if data:
                try:
                    # reading = []
                    # for i in range(0,len(data),1):
                        # reading += [struct.unpack('>I', data[i:i+4])[0]]
                    # print('REEESULTS',reading[:10])
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

def decodeResults(results,fileSize,base,numServers,hashFlag,searchIndex):
    """Aggregate the PIR results from all the servers"""
    if hashFlag:
        # convert back to ints if necessary
        results = [[[ord(a) for a in item] for item in servitem] for servitem in results]

    PIR_result = numpy.zeros((fileSize),dtype=numpy.uint64)
    PIR_result = [[0 for i in range(fileSize)] for i in range(nBins)]
    print([len(res) for res in results])
    # print(results[0][:10])
    # print(PIR_result)
    # print([len(a) for a in results[0]],[len(a) for a in PIR_result])
    if ((base == 4) or (base==2)) and (numServers==2):
        for s in range(numServers):          
            print(len(PIR_result))
            for idx in range(len(PIR_result)):
                if not hashFlag:
                    PIR_result[idx] = [a^b for a,b in zip(PIR_result[idx] , results[s])]
                else:               
                    PIR_result[idx] = [a^b for a,b in zip(PIR_result[idx] , results[s][idx])]
        if hashFlag:    
            PIR_result = onionPeel(PIR_result,searchIndex,bins,hashLength)
                
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
    elif numServers == 2:
        PIR_result = [(a-b)%base for a,b in zip(results[1] , results[0])]
    
    PIR_result = ''.join([chr(z) for z in PIR_result])    
    # print('pir results',PIR_result)
    # for idx in range(len(PIR_result)):
        # PIR_result[idx] = ''.join([chr(z) for z in PIR_result[idx]])    
    
    return PIR_result


if __name__=='__main__':	
    if len(sys.argv) < 5:
        print ("Not enough input arguments: numServers,queryDim,BASE_PORT")
        sys.exit()
    hashFlag = 0
    nBins = 1
    dbSize = int(sys.argv[1])
    numServers = int(sys.argv[2])	
    BASE_PORT = int(sys.argv[3])	
    base = int(sys.argv[4])	
    if len(sys.argv) >= 6: # if we're running the hashed version, there will be more arguments
        hashLength = 4
        seed = int(sys.argv[5])
        hashFlag = 1
        nBins = int(sys.argv[6])
            
        binExpansion = 3
        bins = [[] for i in range(nBins)]
        for fileIdx in range(pow(queryDim,cubeDim)):
            for c in range(binExpansion):
                randBin = random.randint(0,nBins-1)
                while fileIdx in bins[randBin]:
                    randBin = random.randint(0,nBins-1)
                bins[randBin].append(fileIdx)
    searchIndex = 0
    t1 = time.time()

    # generate the PIR queries
    # print('querydim is ',queryDim)
    pirQueries = generatePirQueries(searchIndex,dbSize,numServers,base)
    print('queries generated',pirQueries[:10])

    # submit the queries to the servers
    results,errorFlag = distributePirQueries(numServers,pirQueries,BASE_PORT)
    if not errorFlag:
        # print('the lengths',len(results),len(results[0]),len(results[0][9]))
        if hashFlag:
            fileSize = len(results[0][0])
        
        else:
            fileSize = len(results[0])
        PIR_result = decodeResults(results,fileSize,base,numServers,hashFlag,searchIndex)
        # print ('pir result is ',PIR_result[0][:10])
        print ('pir result is ',PIR_result)

        # print '\n\nYour local result is: ',PIR_result

        # measure the total time
        t2 = time.time()
        dt = t2-t1
        print ('Runtime is ',dt)
        f = open('tot_times.txt','a')
        f.write(str(dt)+'\n')
        f.close()