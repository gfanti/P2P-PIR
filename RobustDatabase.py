# server_class.py 
#
# Class that stores the database and manages operations on that database.

from math import ceil
import numpy as np
import utilities

class RobustDatabase:

    def __init__(self,dbContent,base,fileSize=0,mapping=[],redundancy=[],nBins=1):
        if not (base == 65537):
            print('Cant deal with this base yet. Please try again later.')
            exit()
    
        # load the db from file
        if isinstance(dbContent[0],str): 
            self.dbSize = len(dbContent)
            self.db,self.fileSize = self.loadDb(dbContent,base) 
            self.mapping = mapping
            self.redundancy = redundancy
            self.nBins = nBins
            
        # db has already been provided as numeric array, just store it
        else:	
            self.db = dbContent
            self.dbSize = dbContent.shape[0]
            self.fileSize = fileSize
            self.mapping = mapping
            self.redundancy = redundancy
            self.nBins = nBins
        
    def getDb(self):
        """ Returns the database itself """
        return self.db
        
        
    def loadDb(self,dbContent,base):
        """ Converts the database from list of text strings to byte array in memory """
        
        db = utilities.db2bitarray(dbContent,self.dbSize,1,1,base)
        db = np.array(db).reshape(self.dbSize,-1)
        # track the size of each file
        fileSize = db.shape[-1]
        
        return (db,fileSize)
        
    def submitPirQuery(self,q,base):
        """Process a regular linear PIR query"""
        x,omega = self.db.shape
        print ('OMEGA IS ',omega)
        results = np.zeros(omega,dtype=np.uint64)            
        for bit_idx in range(len(q)):
            if q[bit_idx]==0:
                continue
            results = (utilities.scaleArrayGF(self.db[bit_idx],q[bit_idx],base) + results) % base
            
        return results
        
    def submitPirQueryHash(self,q,base):
        """Process a hashed PIR query"""
        x,omega = self.db.shape
        redundancyFactor = len(self.redundancy[0])
        results = np.zeros((self.nBins,redundancyFactor,omega),dtype=np.uint64)            
        for bit_idx in range(len(q)):
            if q[bit_idx]==0:
                continue
            scaledEntry = np.array([utilities.scaleArrayGF(self.db[bit_idx],utilities.multGf(i,q[bit_idx],base),base) \
                                    for i in self.redundancy[bit_idx] ],dtype=np.uint64 )
            # print('scaled entry',scaledEntry)
            # print('query',q)
            for bin_idx in self.mapping[bit_idx]:
                results[bin_idx] = [(scaledEntry[i] + results[bin_idx,i]) % base for i in range(redundancyFactor)]
        # print('mapping',self.mapping)
        return results