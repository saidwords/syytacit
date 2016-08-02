import unittest
import time
from google.appengine.ext import db
from module.wiki.lib.WikiLib import WikiLib
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
from module.wiki.model.WikiModel import WikiModel
from module.natlang.model.SentenceModel import SentenceModel
class Test_Wiki(unittest.TestCase):
    def setUp(self):
        pass
    def runTest(self):
        pass
    def test_loadSubCategories(self):
        WikiLib.loadSubCategories()
    def test_loadCategories(self):
        for cat in WikiCategoryModel.all():
            cat.delete()
        categories=WikiLib.loadCategories()
    def test_deleteWikiCategoryModelEntity(self):
        q = db.GqlQuery("SELECT __key__ FROM WikiCategoryModel")
        while q.count() > 0 :
            db.delete(q.fetch(200))
            time.sleep(0.5)
    def test_getPages(self):
        for page in WikiModel.all():
            page.delete()
        cat=WikiCategoryModel.all().filter("name =","Agriculture").fetch(1,0)
        WikiLib.getPages(cat[0])
    def test_getSentences(self):
        wikipages=WikiModel.all().fetch(1,0)
        for sentence in SentenceModel.all():
            sentence.delete()
        sentences=WikiLib.getSentences(wikipages[0])
        
            
    def tearDown(self):
        pass

        