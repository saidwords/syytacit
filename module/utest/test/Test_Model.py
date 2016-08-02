import unittest
from google.appengine.ext import db
from module.wiki.model.WikiCategoryModel import WikiCategoryModel

class Test_Model(unittest.TestCase):
    def test_queryListProperty(self):
        #for cat in WikiCategoryModel.all():
        #    cat.delete()
        
        cats=WikiCategoryModel.all().filter('name =','Technology').fetch(50)
        #parentCat=records[0]
        #cats=WikiCategoryModel.gql("WHERE categories = :1", parentCat.key())
        
        #self.assertTrue(cats.count()>0)
        
        for cat in cats:
            print "top category="+cat.name
            
            found=False
            for subcatkey in cat.categories:
                subcat=db.get(subcatkey)
                print "subcategory="+subcat.name
                #if pcat.key()==parentCat.key():
                #    found=True
            #self.assertTrue(found)
                

        #get all categories tagged with Almanacs
       # cats=WikiCategoryModel.all().filter('category =',cat1.key()).fetch(5)
        #self.assertEquals(len(cats),2);
        
        #cat1.delete()
        #cat2.delete()
        #cat3.delete()
        #
        
            
    def setUp(self):
        pass
    def runTest(self):
        pass
    def tearDown(self):
        pass