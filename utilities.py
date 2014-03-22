# utilities
import random 
from server_class import *
from global_constants import *
import numpy
import webbrowser
import os,marshal,copy
import struct
import hashlib

def clearScreen():
	os.system('cls')
	
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
	
def multGf(a,b,base):
    # a is an element of GF4
    # b is a byte, i.e. 4 elements of GF(4), each 2 bits long

    # Check if binary (base 2), then just do regular multiplication
    if base == 2:
        return a*b
    global GF8_TABLE	# access the global table
    if base == 4:
        global GF4_TABLE	# access the global table
        table = GF4_TABLE
    elif base == 16:
        table = GF16_TABLE
    elif base == 65537: #(pow(2,16)+1):
        return (a*b)%65537
    try:
        return int(table[a][b])
    except:
        print( "This is not a valid input to a GF multiplication in base",base,' : ' ,a,b)
        return	    
	
def db2bitarray(dbContent,cubeSize,cubeDim,multFactor,base):
    """ Converts a database of strings into a numeric byte array"""
    num_file_bits = len(max(dbContent,key=len))
    db=[]
    if multFactor == 1:
        # convert the DB into bitstrings
        for item in dbContent:
            item = item.ljust(num_file_bits)
            db = db + [numpy.uint8(ord(y)) for y in item]
            # db = db + [ord(' ') for y in range(num_file_bits-len(item))]
        # fill in the last slots of the database with all spaces
        for item in range(int(pow(cubeSize,cubeDim) - len(dbContent))):
            db = db + [numpy.uint8(ord(' '))]*num_file_bits
    else:
        for item in dbContent:
            item = item.ljust(num_file_bits)
            db = db + [numpy.uint8(multGf(multFactor,int(ord(y)),base)) for y in item]
            # db = db + [multGf4(multFactor,int(ord(' '))) for y in range(num_file_bits-len(item))]
        # fill in the last slots of the database with all spaces
        for item in range(int(pow(cubeSize,cubeDim) - len(dbContent))):
            db = db + [numpy.uint8(multGf(multFactor,int(ord(' ')),base))]*num_file_bits
    return db
		
def scaleArrayGF(x,a,base):
	# x is the array
	# a is the GF(4) element to scale by
	if a == 1:
		return x
	else:
		arrayShape = x.shape
		# print 'Were in the scaleArray. arrayShape is ',arrayShape,type(x),'x[:] is',x[:]
		b = x[:].reshape(-1,1)
		# print 'b is ',b, 'a is',a
		
		xnew = numpy.array([multGf(a,item,base) for item in b]).reshape(arrayShape)
		# print 'new shape is',xnew.shape, arrayShape
		# print 'new array is ',xnew,'old is',x
		# raw_input()
		return xnew

def retrieve_webpage(url):
	webbrowser.open(url)

def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)
    
def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytes('','utf-8')
    # data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
    
def isSingleton(file,hashLength):
    # print(type(file),file[:hashLength],file[-hashLength:],HASH_LEN, len(file),file[:HASH_LEN])
    fileString = bytes(''.join(chr(item) for item in file[:HASH_LEN]),'utf-8')
    hashComputed = hashlib.md5(fileString).hexdigest()[:hashLength]
    hashRead = ''.join(chr(item) for item in file[-hashLength-1:-1])
    print ('hashes',hashComputed,hashRead,hashComputed==hashRead)
    return hashComputed == hashRead
    # return file[:hashLength] == file[-hashLength:]
    
