# FiniteFieldCS.py: helper functions for distributed compressed sensing over finite fields

import utilities
import random
import numpy as np
import hashlib
import math
import copy

def sparseDecode(PIR_result,searchIndex,nBins,mapping,redundancy,base):
    """ Converts a compressed sensing vector (PIR_result) into a sparse vector, and 
        returns the desired element(s) 'searchIndex' """
    PIR_result = np.array(PIR_result)
    # print('type',type(PIR_result))
    # print('decode this',PIR_result)
    retrieved = 0
    while not retrieved:
        singletonFound = 0
        for idx in range(nBins):
            singletonIdx = checkSingletonRatio(PIR_result[idx],base)
            if singletonIdx > -1:
                singletonFound = 1
                # check if it's the desired item 
                # print('indices',singletonIdx,searchIndex)
                if singletonIdx == searchIndex:
                    retrieved = 1
                    break
                #otherwise, remove this singleton from the other bins
                for i in range(nBins):
                    PIR_result[idx] = (PIR_result[idx] - scaledVal) % base
                
        if not singletonFound:
            print("Onion-peeling decoding failed.")
            return 0
    return PIR_result[idx,0]

def checkSingletonRatio(item,base):
    """ checks if a file is a singleton using the ratio test by hashing 
        the contents and comparing to the checksum of the file """
    # print('item',item[0,0])
    if (item[0,0] == 0) and (item[1,0] == 0):
        return -1
    else:
        ratio1 = ((int(item[1,0])*int(inverseGf(item[0,0],base)))%base)
        ratio2 = ((int(item[2,0])*int(inverseGf(item[1,0],base)))%base)
        # print('ratios',ratio1,ratio2)
    if ratio1 == ratio2:
        alpha = 3 # primitive element
        tmp = discreteLog(alpha,ratio1,base)
        return tmp
    return -1

def inverseGf(a,base):
    """ Returns the inverse of element 'el' in finite field 'base' using extended 
        Euclidean algorithm """
    
    t = 0
    newt = 1    
    r = base
    newr = a;    
    while not (newr == 0):
        quotient = int(r / newr)
        (t, newt) = (newt, t - quotient * newt) 
        (r, newr) = (newr, r - quotient * newr)
    if r > 1: 
        print("a is not invertible")
        return -1
    if t < 0: 
        t = t + base
    return t
    
    
def checkSingletonHash(file,hashLength):
    """ checks if a file is a singleton using the ratio test by hashing 
        the contents and comparing to the checksum of the file """
    try:
        fileString = bytes(''.join(chr(item) for item in file[:hashLength]),'utf-8')
        hashComputed = hashlib.md5(fileString).hexdigest()[:hashLength]
        hashRead = ''.join(chr(item) for item in file[-hashLength-1:-1])
        print ('hashes',hashComputed,hashRead,hashComputed==hashRead)
        return hashComputed == hashRead
    except:
        print("hash failed",file)
        return 0

def modularExp(el,power,base):
    """ Returns the modular exponentiation of el to the power 'power' over base 'base' """
    prod = el
    for i in range(1,power):
        prod = (prod * el) % base
    return prod
        
    
def discreteLog(alpha,y,base):
    """ Takes the logarithm of x in base alpha """
    # TO DO: this assumes that alpha is 2! Make it generalize
    z = y
    if (alpha == 3) and (base == 65537):
        beta = 21846
        n = 16
    else:
        beta = inverseGf(alpha,base)
        n = int( math.log(base) / math.log(2) )
    m = int((base-1)/2)
    i = 0
    b = ''
    while not (n == i):
        w = int(modularExp(z,m,base))
        # print('w is',w)
        # print('z:',z,'m:',m,'beta:',beta)
        if w == 1:
            b = '0' + b
        elif (w == (-1%base)):
            b = '1' + b
            z = (z*beta) % base
        
        beta = pow(beta,2) % base
        m = int(m / 2)
        i += 1
        
    return int(b,2)
    
def invFiniteFieldMat(V,base):
    """Inverts a (numServers)x(numServers) Vandermonde matrix V in base 'base' """
    
    Vinv = np.linalg.inv(V);
    for i in range(Vinv.shape[0]):
        for j in range(Vinv.shape[1]):
            x = Vinv[i,j]
            parts = [0,0]
            parts = utilities.rationalize(x)
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
        binsList = [i for i in range(nBins)]
        random.shuffle(binsList)
        mapping[fileIdx] = copy.copy(binsList[:binExpansion])
        # for c in range(binExpansion):
            # randBin = binsList.pop( 0 ) 
            # mapping[fileIdx].append(randBin)
    return mapping

def buildDetMapping(nEvaluations,dbSize,base):
    """ Build a Vandermonde mapping of files to bins """
    # select a primitive element
    alpha = 3
    mapping = [[] for i in range(dbSize)]
    for fileIdx in range(dbSize):
        mapping[fileIdx] = [pow(pow(alpha,fileIdx),i) for i in range(nEvaluations)]
    return mapping
    
def buildInvSamplingMatrix(numServers,base):
    """ Returns the inverse of a Vandermonde matrix with
        numServers entries, in base 'base' """
        
    V = [[] for tmp in range(numServers)]
    for x in range(1,numServers+1):
        V[x-1] = [pow(x,l) for l in range(numServers-1,-1,-1)]
    Vinv = invFiniteFieldMat(V,base)
    return Vinv