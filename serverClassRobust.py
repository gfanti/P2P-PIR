# server_class.py 
#
# Class that stores the database and manages operations on that database.

from math import ceil
import numpy
import utilities

class RobustServer:

    def __init__(self,dbContent,base,fileSize=0):
        if not (base == 65537):
            print('Cant deal with this base yet. Please try again later. Or implement it yourself.')
            exit()
    
        # load the db from file
        if isinstance(dbContent[0],str): 
            self.dbSize = len(dbContent)
            self.db,self.fileSize = self.loadDb(dbContent,base) 
            
        # db has already been provided as numeric array, just store it
        else:	
            self.db = dbContent
            self.dbSize = dbContent.shape[0]
            self.fileSize = fileSize
        
    def getDb(self):
        """ Returns the database itself """
        return self.db
        
        
    def loadDb(self,dbContent,base):
        """ Converts the database from list of text strings to byte array in memory """
        
        db = utilities.db2bitarray(dbContent,self.dbSize,1,1,base)
        db = numpy.array(db).reshape(self.dbSize,-1)
        # track the size of each file
        fileSize = db.shape[-1]
        
        return (db,fileSize)
        
    def submitPirQuery(self,q,base):
        """Process a regular linear PIR query"""
        x,omega = self.db.shape
        proj1d = numpy.zeros(omega,dtype=numpy.uint32)            
        for bit_idx in range(len(q)):
            if q[bit_idx]==0:
                continue
            proj1d = (utilities.scaleArrayGF(self.db[bit_idx],q[bit_idx],base) + proj1d) % base
            
        return proj1d
        
    def submitPirQueryHash(self,q,base,bins):
        """Process a hashed PIR query"""
        x,omega = self.db[1].shape
        results = []
        proj1d = numpy.zeros(omega,dtype=numpy.uint32)            
        for bin_idx in bin:
            if q[bin_idx]==0:
                continue
            proj1d = (utilities.scaleArrayGF(self.db[bin_idx],q[bin_idx],base) + proj1d) % base
        print('proj1d is ',proj1d,len(proj1d))
        results = [list(arr) for arr in results]
            
        return results