# FiniteFieldCS.py: helper functions for distributed compressed sensing over finite fields

import utilities

def sparseDecode(PIR_result, searchIndex, bins, hashLength):
    """ Converts a compressed sensing vector (PIR_result) into a sparse vector, and 
        returns the desired element(s) 'searchIndex' """
        
    retrieved = 0
    while not retrieved:
        for binIdx in range(len(bins)):
            if isSingleton(PIR_result[binIdx],hashLength):
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

def isSingleton(file,hashLength):
    """ checks if a file is a singleton by hashing the contents and
        comparing to the checksum of the file """
        
    # print(type(file),file[:hashLength],file[-hashLength:],HASH_LEN, len(file),file[:HASH_LEN])
    fileString = bytes(''.join(chr(item) for item in file[:HASH_LEN]),'utf-8')
    hashComputed = hashlib.md5(fileString).hexdigest()[:hashLength]
    hashRead = ''.join(chr(item) for item in file[-hashLength-1:-1])
    print ('hashes',hashComputed,hashRead,hashComputed==hashRead)
    
    return hashComputed == hashRead
    
def invFiniteFieldMat(V,base):
    """Inverts a (numServers)x(numServers) Vandermonde matrix V in base 'base' """
    
    Vinv = numpy.linalg.inv(V);
    for i in range(Vinv.shape[0]):
        for j in range(Vinv.shape[1]):
            x = Vinv[i,j]
            parts = [0,0]
            parts = rationalize(x)
            if x%1 > 0:
                num = parts[0]
                while x%1 > 0:
                    num += base
                    x = num / parts[1]
            x = int(x % base)
            Vinv[i,j] = x
    return Vinv
    
def buildRandMapping(binSeed,nBins,binExpansion,dbSize):
    """ Build a random mapping of files to bins """
    random.seed(binSeed)
    mapping = [[] for i in range(dbSize)]
    for fileIdx in range(dbSize):
        for c in range(binExpansion):
            randBin = random.randint(0,nBins-1)
            mapping[fileIdx].append(randBin)
    return mapping
    
def buildInvSamplingMatrix(numServers,base):
    """ Returns the inverse of a Vandermonde matrix with
        numServers entries, in base 'base' """
        
    V = [[] for tmp in range(numServers)]
    for x in range(1,numServers+1):
        V[x-1] = [pow(x,l) for l in range(numServers-1,-1,-1)]
    Vinv = invFiniteFieldMat(V,base)
    return Vinv