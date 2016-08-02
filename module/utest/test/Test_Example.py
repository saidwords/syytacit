import unittest
import os
import sys
import marshal

class Test_Example(unittest.TestCase):
    def setUp(self):
        foo=None
    def test_make_word_frequency(self):
        f = open(os.path.abspath(".")+"/resources/wordfrequency.txt", "r")
        
        result=[]
        frequency={}
        line=f.readline();
        while line !="":
            tokens=line.split(" ")
            if len(tokens) > 1:
                frequency[tokens[2]]=int(tokens[0])
            line=f.readline();
        
        f.close()
        f = open("/tmp/foo/txt","r+b")
        
        marshal.dump(frequency,f)
        f.close()
        
    def test_example_failure(self):
        self.assertEqual(1,0);
        return None
    def test_example_success(self):
        self.assertEqual(1,1);
        return None
    def runTest(self):
        foo=None
    def tearDown(self):
        bar=None