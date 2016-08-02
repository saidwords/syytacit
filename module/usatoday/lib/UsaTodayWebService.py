import datetime
from xml.dom.minidom import parse,parseString
from xml.dom import EMPTY_NAMESPACE
from common.lib.Config import Config
from google.appengine.api import urlfetch
from module.usatoday.model.UsaTodayCategoryModel import UsaTodayCategoryModel
from module.usatoday.model.UsaTodayHeadlineModel import UsaTodayHeadlineModel
import urllib
import logging
from django.utils import simplejson
from module.article.model.ArticleModel import ArticleModel

class UsaTodayWebService:
    # http://api.usatoday.com/open/articles?tag=barack+obama&api_key=XXXXXX
    DOMAIN='api.usatoday.com'
    PROTOCOL='http'
    VERSION=1
    ARTICLE_APIKEY='38mjhe8v4mzx75msuc29gqej'
    BREAKING_NEWS_API_KEY='gynggqy3xsdxvrccnynuptyc'
    ATOM_NS = 'http://www.w3.org/2005/Atom'
    
    CATEGORY_TOP_GENERAL_SHORT_HEADLINES=31990;
    
    def getLatestArticles(self):
        articles=[]
        content=self.sendRequest('/open/articles',{'days':2,'encoding':'json'})
        if len(content)<3:
            logging.warn("no data retreived from "+self.DOMAIN)
        else:
            data = simplejson.loads(content)
            if data['stories']:
                for article in data['stories']:
                    pubDate=datetime.datetime.strptime(article['pubDate'], '%a, %d %b %Y %H:%M:%S %Z') # Wed, 17 Jul 2013 08:57:58 GMT
                    ihref='null'
                    articles.append(ArticleModel(title=article['title'],description=article['description'],href=article['link'],source='usatoday',updated=pubDate,ihref=ihref))
                
        return articles
    def sendRequest(self,path=None,params=None):
        if params==None:
            params={}
        params['api_key']=self.ARTICLE_APIKEY
        qs=urllib.urlencode(params)
        url=self.PROTOCOL+'://'+self.DOMAIN+'/'+path+'?'+qs
        urlFetchResult = urlfetch.fetch(url,deadline=120)
        #if urlFetchResult.status_code != 200:
        return urlFetchResult.content
    def parseDate(self):
        #atomdate='2010-09-17T02:16:16Z';
        atomdate='2010-09-17T02:16:16Z';
        dateobj=datetime.datetime.strptime(atomdate,'%Y-%m-%dT%H:%M:%SZ')
        return dateobj
