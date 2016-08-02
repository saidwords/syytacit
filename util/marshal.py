import os
import marshal

def load_wordfrequency():
	f = open("/home/username/workspace/saidwords/src/resources/wordfrequency.pyc","rb")
	foo=marshal.load(f)
	f.close();
	
	print str(foo)



def foo():
	f = open("/tmp/englishwords.txt","r")

	frequency={}
	line=f.readline();
	while line !="":
		frequency[line.strip()]=1
		line=f.readline();
		
	f.close()

	f = open("/tmp/englishwords.pyc","w+b")

	marshal.dump(frequency,f);

	f.close();

	f = open("/tmp/englishwords.pyc","rb")
	foo=marshal.load(f)
	f.close();

	print str(foo)

load_wordfrequency()


