import bintrees
from bintrees import RBTree
import time
import red_black_dict_mod 
from red_black_dict_mod import RedBlackTree


def rbt():
	tr = RBTree()

	n = 10000
	for i in range(n):
		tr[i] = True

	t0 = time.time()
	for i in range(100):
		slc = list(tr.key_slice(100,102))
	print(len(slc),round(time.time()-t0,2))


	# t0 = time.time()
	# for i in range(10000):
	# 	v = tr.ceiling_key(105.5)
	# print(v,round(time.time()-t0,2))
	#tr.slice(-2,-1)


def red():

	tr = RedBlackTree()
	for i in range(1000):
		tr[i] = True
	
	t0 = time.time()
	for i in range(10):
		nod = tr.find(12)
	nod = tr.find(12)
	t = round(time.time()-t0,4)
	print(nod,t)


	print()
	t0 = time.time()
	for i in range(10):
		nod = tr.find(900)
		while nod and nod.key < 1000:
			nod = nod.successor
	print(round(time.time()-t0,4))

	
red()


