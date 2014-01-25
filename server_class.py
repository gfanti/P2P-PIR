from math import ceil
import numpy
import utilities

class Server:

    def __init__(self,db,cubeDim,base,fileSize=0):
        # create a cube for the db
        self.cubeDim = cubeDim
        if isinstance(db[0],str): 
            dbCube,cubeSize,self.fileSize = self.reshapeDb(db,cubeDim,base)

            print( 'filesize is ',self.fileSize)
            self.db = [[]]*base
            for i in range(1,base):
                self.db[i] = dbCube[i]
            self.cubeSize = cubeSize
        # db has already been provided, just store it
        else:	
            self.db = db
            self.cubeDim = cubeDim
            self.cubeSize = db.shape[0]
            self.fileSize = fileSize
        
    def getDb(self):
        return self.db
        
        
    def reshapeDb(self,dbContent,cubeDim,base):
        print(cubeDim,base)
        
        if cubeDim>3:
            print ("ERROR, Can't deal with weird-dimensioned cubes (ie not 1 or 3)!")
            return (0,0,0)

        # find the dimension of the cube
        cubeSize = int(ceil(pow(len(dbContent),1.0/cubeDim)))

        db = [[]]*base
        dbCube = [[]]*base
        for i in range(1,base):
            # convert the db to a bit array
            db[i] = utilities.db2bitarray(dbContent,cubeSize,cubeDim,i,base)

            # reshape the arrays into cubes
            if cubeDim==1:
                dbCube[i] = numpy.array(db[i]).reshape(cubeSize,-1)
            elif cubeDim==2:
                dbCube[i] = numpy.array(db[i]).reshape(cubeSize,cubeSize,-1)
            elif cubeDim==3:
                dbCube[i] = numpy.array(db[i]).reshape(cubeSize,cubeSize,cubeSize,-1)

        # track the size of each file
        fileSize = dbCube[1].shape[-1]

        return (dbCube,cubeSize,fileSize)
        
    def submitPirQuery(self,q,base):
        if self.cubeDim > 3:
            return 0
        if self.cubeDim == 3:
            # takes as input a 3D PIR query and returns the appropriate combo of files
            #Projection 1: 4d-->3d
            x,y,z,omega = self.db[1].shape
            proj3d = numpy.zeros((1,y,z,omega),dtype=numpy.uint8)
            for bit_idx in range(len(q[0])):
                if q[0][bit_idx]==0:
                    continue
                proj3d = numpy.bitwise_xor(self.db[q[0][bit_idx]][bit_idx,:,:,:],proj3d)
            proj3d = numpy.add.reduce(proj3d,0)



            #scale everything by the GF(4) value in q
            #Projection 2: 3d-->2d
            proj2d = numpy.zeros((1,z,omega),dtype=numpy.uint8)
            for bit_idx in range(len(q[1])):
                if q[1][bit_idx]==0:
                    continue
                proj2d = numpy.bitwise_xor(utilities.scaleArrayGF(proj3d[bit_idx,:,:],q[1][bit_idx],base),proj2d)
            proj2d = numpy.add.reduce(proj2d,0)


            #Projection 3: 2d-->1d
            proj1d = numpy.zeros((1,omega),dtype=numpy.uint8)
            for bit_idx in range(len(q[2])):
                if q[2][bit_idx]==0:
                    continue
                proj1d = numpy.bitwise_xor(utilities.scaleArrayGF(proj2d[bit_idx,:],q[2][bit_idx],base),proj1d)
            proj1d = numpy.add.reduce(proj1d,0)
        elif self.cubeDim == 1:
            x,omega = self.db[1].shape
            proj1d = numpy.zeros((1,omega),dtype=numpy.uint8)
            for bit_idx in range(len(q[0])):
                if q[0][bit_idx]==0:
                    continue
                proj1d = numpy.bitwise_xor(utilities.scaleArrayGF(proj2d[bit_idx,:],q[0][bit_idx],base),proj1d)
            proj1d = numpy.add.reduce(proj1d,0)
            
        return proj1d