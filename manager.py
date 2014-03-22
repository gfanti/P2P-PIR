# manager.py
# This code calls all the necessary components for simulating the PIR network. It calls the client and a number of servers and tracks the total runtime.
#
# Inputs:
#   (none)
#
# Outputs:
#   (none)

import os
import subprocess,multiprocessing
from multiprocessing import Process
import time
from math import ceil
import utilities, scipy.io


if __name__=='__main__':

    # set the relevant parameters
    BASE_PORT = 8888
    numServers = 2
    cubeDim = 1 #GET RID OF THE CUBE DIMENSION
    newDatabase = 0
    base = pow(2,16)+1
    hashFlag = 0
    seed = 0
    nBins = 10
    # dbFilenames = ['data/2048bytes/500files','data/2048bytes/2500files','data/2048bytes/5000files','data/2048bytes/7500files','data/2048bytes/10000files']
    dbFilenames = ['data_memory/2048bytes/2files']


    trials = 1
    tot_times = []


    # first wipe the data from previous runs
    for p in range(numServers):
        f = open(str(BASE_PORT+p)+'.txt','w')
        f.close()
    f = open('tot_times.txt','w')
    f.close()


    # then cycle through the different databases 
    for dbIdx in range(len(dbFilenames)):

        dbFilename = dbFilenames[dbIdx]

        # if necessary, construct a new database and exit
        if newDatabase or not os.path.isfile(dbFilename+str(base)+'_db.npy'):
            print ("Making database for ",dbFilename)
            cmd = ['serverManager.py',str(BASE_PORT),str(newDatabase),dbFilename,str(base)]
            child = subprocess.Popen(cmd,shell=True)
            child.wait()
            
            print ('Databases built!')
            
        # otherwise, run the PIR queries
        else:

            queryDim = int(ceil(pow(utilities.file_len(dbFilename),1.0/cubeDim)))
            times = []
            for k in range(trials):
                print ('Running trial ',k)
                # start each of the servers
                children = []
                port = []
                for i in range(numServers):
                    port.append(BASE_PORT + i)
                    if hashFlag:
                        cmd = ['serverManager.py',str(port[i]),str(newDatabase),dbFilename,str(base),str(seed),str(nBins)]
                    else:
                        cmd = ['serverManager.py',str(port[i]),str(newDatabase),dbFilename,str(base)]                
                    children.append( subprocess.Popen( cmd, shell=True ) )
                # wait for the servers to load
                time.sleep(10)
            
                t1 = time.time()
                # call the client process
                if hashFlag:
                    cmd = ['clientManager.py',str(utilities.file_len(dbFilename)),str(numServers),str(BASE_PORT),str(base),str(seed),str(nBins)]
                else:
                    cmd = ['clientManager.py',str(utilities.file_len(dbFilename)),str(numServers),str(BASE_PORT),str(base)]            
                children.append( subprocess.Popen( cmd, shell=True ) )

                # make sure all the child processes are finished
                for child in children:
                    child.wait()

                # measure the total time
                t2 = time.time() - t1
                times.append(t2)
                # dt = t2-t1
                # print 'Runtime is ',dt
            # print 'Times are ',times
            tot_times.append(times)

    if len(tot_times) > 1:
        print ('tot_times',tot_times)
        print ('average time: ',float(sum(tot_times[0]))/float(trials))
    # scipy.io.savemat('tot_times.mat',mdict={'tot_times':tot_times})