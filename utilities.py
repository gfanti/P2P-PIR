# utilities
import random 
# from server_class import *
from global_constants import *
import numpy as np
import webbrowser
import os,marshal,copy
import struct
import hashlib
import fractions

def clearScreen():
	os.system('cls')
	
def file_len(fname):
    """ Returns the number of elements in file 'fname' """
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
	
def multGf(a,b,base):
    """ Multiplies 'a' by 'b' in finite field base 'base'  """
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
        return (a*b)%base
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
            db = db + [np.uint64(ord(y)) for y in item]
            # db = db + [ord(' ') for y in range(num_file_bits-len(item))]
        # fill in the last slots of the database with all spaces
        for item in range(int(pow(cubeSize,cubeDim) - len(dbContent))):
            db = db + [np.uint64(ord(' '))]*num_file_bits
    else:
        for item in dbContent:
            item = item.ljust(num_file_bits)
            db = db + [np.uint64(multGf(multFactor,int(ord(y)),base)) for y in item]
            # db = db + [multGf4(multFactor,int(ord(' '))) for y in range(num_file_bits-len(item))]
        # fill in the last slots of the database with all spaces
        for item in range(int(pow(cubeSize,cubeDim) - len(dbContent))):
            db = db + [np.uint64(multGf(multFactor,int(ord(' ')),base))]*num_file_bits
    return db
		
def scaleArrayGF(x,a,base):
    """Multiply an array 'x' by a constant 'a' in base 'base' """
    # x is the array
    # a is the GF(q) element to scale by
    if a == 1:
        return x
    else:
        arrayShape = x.shape
        # print 'Were in the scaleArray. arrayShape is ',arrayShape,type(x),'x[:] is',x[:]
        b = x[:].reshape(-1,1)
        # print 'b is ',b, 'a is',a
        
        xnew = np.array([multGf(a,item,base) for item in b]).reshape(arrayShape)
        return xnew

def retrieve_webpage(url):
	webbrowser.open(url)

def send_msg(sock, msg):
    """ Prefix each message with a 4-byte length (network byte order) """
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)
    
def recv_msg(sock):
    """ Read message length and unpack it into an integer """
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    """ Helper function to recv n bytes or return None if EOF is hit """
    data = bytes('','utf-8')
    # data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data
    
def rationalize(x):
    """ Takes a rational number in decimal representation 'x', and outputs 
        a fraction representation of that number (outputs [numerator denominator]) """
        
    parts = [0,0]
    st = str(x)
    if len(st) > 4:
        if (st[4] == '0'):
            x = round(x,10)
            frac = fractions.Fraction(x)
            parts = [frac.numerator, frac.denominator]
        elif st.split('.')[1][:5] == '33333':
            parts[0] = 3 * int(x) + 1*(x>0) - 1*(x<0)
            parts[1] = 3
        elif st.split('.')[1][:5] == '66666':
            parts[0] = 3 * int(x) + 2*(x>0) - 2*(x<0)
            parts[1] = 3
        elif st.split('.')[1][:5] == '16666':
            parts[0] = 6 * int(x) + 1*(x>0) - 1*(x<0)
            parts[1] = 6
        elif st.split('.')[1][:5] == '83333':
            parts[0] = 6 * int(x) + 5*(x>0) - 5*(x<0)
            parts[1] = 6
        else:
            print ('string',st.split('.')[1][:5])
    else:
        frac = fractions.Fraction(round(x,4))
        parts = [frac.numerator, frac.denominator]
    
    return parts
    
def chunks(l, n):
    """ Divide list l into chunks of size n"""
    
    if n<1:
        n=1
    return [l[i:i+n] for i in range(0, len(l), n)]
    
