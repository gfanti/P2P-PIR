import utilities
import random
import socket, select
import sys, os
import json,marshal
import time
import numpy as np
import FiniteFieldCS

    
def generatePirQueries(searchIndex, dbSize, numServers, base):
    """ Generates one PIR query for each server in the system"""
    a = [[] for i in range(numServers-1)] # random strings defining polynomials for secret sharing
    q = [[] for i in range(numServers)] # queries to be sent to each server
    
    # generate the indicator vector for desired file
    e = []
    equery = [0 for l in range(dbSize)]
    equery[searchIndex] = 1
    e.append( equery )
    
    # generate the shares for masking
    for i in range(numServers-1):
        a[i] = [random.randint(0,base-1) for q in range(0,dbSize)]
    # if there are only 2 servers, we don't need to worry about collusion, and just use a and a+e_i
    if numServers == 2:
        q[0] = [item for item in a[0]];
        q[1] = [item for item in a[0]];
        q[1][searchIndex] = (q[1][searchIndex] + 1) % base
    # if there are more than 2 servers, we use shamir secret sharing
    else:
        # construct the related polynomials
        for i in range(numServers):
            x = i+1
            q[i] = [item for item in equery]
            for j in range(1,numServers):
                xeval = pow(x,j)
                q[i] = [(a+b)%base for (a,b) in zip(q[i],[xeval*c%base for c in a[j-1]])] # add term in polynomial
    return q
    


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
            data = utilities.recv_msg(r)  # THIS DOESN'T WORK FOR SOME REASON
            
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
                # print('res is ',res)
                rPort = int(res.pop(0)) - BASE_PORT
                results[rPort] = utilities.chunks(res,int(len(res)/nBins))
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

def decodeResults(results,fileSize,base,numServers,hashFlag,searchIndex,Vinv):
    """ Aggregates the PIR results from all the servers into a numeric list or
        list of lists """
        
    # Initialize the results structure
    PIR_result = np.zeros((fileSize),dtype=np.uint64)
    PIR_result = [[0 for i in range(fileSize)] for i in range(nBins)]
    print([len(res) for res in results])
    # print(results[0][:10])
    # print(PIR_result)
    # print([len(a) for a in results[0]],[len(a) for a in PIR_result])
    # if ((base == 4) or (base==2)) and (numServers==2):
        # for s in range(numServers):          
            # print(len(PIR_result))
            # for idx in range(len(PIR_result)):
                # if not hashFlag:
                    # PIR_result[idx] = [a^b for a,b in zip(PIR_result[idx] , results[s])]
                # else:               
                    # PIR_result[idx] = [a^b for a,b in zip(PIR_result[idx] , results[s][idx])]
        # if hashFlag:    
            # PIR_result = onionPeel(PIR_result,searchIndex,bins,hashLength)
                
    # elif base == 16:
        # if numServers==4:
            # scale = [6,1,1,1]
        # elif numServers == 7:
            # scale = [6,7,13,11,10,12,6]
        # elif numServers == 10:
            # scale = [4,1,2,2,13,13,10,10,4,4]
        # elif numServers == 13:
            # scale = [10,5,7,10,10,13,8,6,4,14,9,10,9]
        # elif numServers == 16:
            # scale = [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        # # now combine the results appropriately
        # for s in range(numServers):
            # PIR_result = [a^utilities.multGf(scale[s],b,base) for a,b in zip(PIR_result , results[s])]	
            
    # At the moment, this has only been tested on one prime base (65537), but this code /should/ work for other
    #       prime bases as well
    
    if base == 65537:
        if numServers == 2: # subtract results
            PIR_result = [[(a-b)%base for a,b in zip(r1,r2)] for r1,r2 in zip(results[1] , results[0])]
            if not hashFlag:
                PIR_result = PIR_result[0]
            print('PIR RESULT',PIR_result)
            
        else:   # multiply by the appropriate matrix
            print('results',np.array(results))
            results = np.array(results)
            VinvTimesR = np.array([[[int((Vinv[-1,i]*item)%base) for item in results[i,k]] for i in range(numServers)] for k in range(len(results[0]))])
            if not hashFlag:
                VinvTimesR = VinvTimesR[0]
            PIR_result = np.sum(VinvTimesR,0)%base 
            print('result',PIR_result,PIR_result.shape)
    
    # Decode the sparse vector if needed
    if hashFlag:
        PIR_result = FiniteFieldCS.sparseDecode(PIR_result, searchIndex, bins, hashLength)
    ResultFile = ''.join([chr(z) for z in PIR_result])
    
    return ResultFile


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
        hashFlag = 1
        nBins = int(sys.argv[5])
        print('nbins is',nBins)
        
        binSeed = 0
        binExpansion = 3
        mapping = FiniteFieldCS.buildRandMapping(binSeed,nBins,binExpansion,dbSize)
        
    # choose which file to query (can be random or deterministic)
    searchIndex = 0
    
    # build the inverse sampling matrix V (inverse of Vandermonde matrix)
    Vinv = FiniteFieldCS.buildInvSamplingMatrix(numServers,base) 
    
    t1 = time.time()

    # generate the PIR queries
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
        PIRresult = decodeResults(results,fileSize,base,numServers,hashFlag,searchIndex,Vinv)
        
        # print ('pir result is ',PIR_result[0][:10])
        print ('pir result is ',PIRresult)

        
        # measure the total time
        t2 = time.time()
        dt = t2-t1
        print ('Runtime is ',dt)
        f = open('tot_times.txt','a')
        f.write(str(dt)+'\n')
        f.close()