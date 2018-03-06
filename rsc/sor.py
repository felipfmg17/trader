

fin = open('result_xrp_4days.txt','r')
fout = open('result_xrp_4days2.txt','w')

ar = []
for line in fin:
	line = line.split()
	ar.append(line)

ar = sorted(ar)

for e in ar:
	e = ' '.join(e)
	print(e,file=fout)

fin.close()
fout.close()