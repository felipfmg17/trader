import bintrees
from bintrees import RBTree



ar = []

print(max(ar))

tr = RBTree()

for i in range(10):
	tr[i] = True

print(list(tr.keys()))

flk = tr.floor_key(100)
print(flk)
clk = tr.ceiling_key(-100)
print(clk)


slc = tr.key_slice(tr.min_key(),3.001)
print(list(slc))
slc2 = tr.value_slice(6,tr.max_key()+0.001)
print(list(slc2))


