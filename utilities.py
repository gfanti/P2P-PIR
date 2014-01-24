# utilities
import random 
from server_class import *
from global_constants import *
import numpy
import webbrowser
import os,marshal,copy

def clearScreen():
	os.system('cls')

# def arr2json(arr):
    # # return marshal.dumps(arr.tolist())
	# return json.dumps(arr.tolist())
	
# def json2arr(astr,dtype):
	# t = json.loads(astr[1:-1])
	# # t = marshal.loads(astr)
	# return numpy.fromiter(t,dtype)
	# # return numpy.fromiter(json.loads(astr[1:3990]),dtype,len(astr)-2)
	
def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1
	
def multGf(a,b,base):
	# a is an element of GF4
	# b is a byte, i.e. 4 elements of GF(4), each 2 bits long
	global GF4_TABLE	# access the global table
	global GF8_TABLE	# access the global table
	if base == 4:
		table = GF4_TABLE
	elif base == 16:
		table = GF16_TABLE
	try:
		return int(table[a][b])
	except:
		print( "This is not a valid input to a GF multiplication in base",base,' : ' ,a,b)
		print( table)
		return	
	
def db2bitarray(dbContent,cubeSize,cubeDim,multFactor,base):
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
