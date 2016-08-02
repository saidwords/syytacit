import unittest
from module.article.model.ArticleModel import ArticleModel
from module.article.lib.ArticleLib import ArticleLib
from google.appengine.ext import db
from google.appengine.api import users

class Test_Article(unittest.TestCase):
    def setUp(self):
        pass
    def test_saveArticle(self):
        article = ArticleModel(title='footitle',id='foo',ihref='fooref')
        article.title='bartitle'
        article.id='bar'
        article.ihref='barref'
        article.authors.append('sedwards')
        
        # save the article in the database
        result=article.put()
        
        #verify that there are no 'foo' articles
        q=article.all()
        q.filter("id =","foo")
        articles=q.fetch(255, 0)
        self.assertEquals(0,len(articles));

        # retrieve the article from the database
        q=article.all()
        q.filter("id =","bar")
        articles=q.fetch(255, 0)
        self.assertEquals(1,len(articles));
        
        for a in articles:
            self.assertEqual(article.id,a.id)
            self.assertEqual(article.title,a.title)
            self.assertEqual(article.ihref,a.ihref)
        
        # delete the article from the database
        for a in articles:
            a.delete()
        
        # verify that the article was deleted
        articles2 = db.GqlQuery("SELECT * FROM ArticleModel WHERE id = :1",'bar')
        self.assertEquals(0,articles2.count());
        
        return None
    
    def test_createUrl(self):
        article=ArticleModel(title="1 some the kind    of-article-#titlE",ihref='null')
        url = ArticleLib.createUrl(article)
        self.assertEqual("1-kind-of-article-title",url)
    def runTest(self):
        pass
    def tearDown(self):
        pass
