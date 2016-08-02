import datetime
from xml.dom.minidom import parse,parseString
from xml.dom import EMPTY_NAMESPACE
from common.lib.Config import Config
from google.appengine.api import urlfetch
from module.associatedpress.model.AssociatedPressCategoryModel import AssociatedPressCategoryModel
from module.associatedpress.model.AssociatedPressHeadlineModel import AssociatedPressHeadlineModel
import urllib
import logging

class AssociatedPressWebService:
    DOMAIN='developerapi.ap.org'
    PROTOCOL='http'
    VERSION=2
    APIKEY='wjuf66yqhd2dg39yq95n7f7v'
    ATOM_NS = 'http://www.w3.org/2005/Atom'
    
    CATEGORY_TOP_GENERAL_SHORT_HEADLINES=31990;
    
    def getBreakingNews(self,category):
        assert isinstance(category, AssociatedPressCategoryModel)
        news=[]
        content=self.sendRequest('categories.svc/'+str(category.id))
        if len(content) == 0:
            return news

        logging.info(content)
        dom=parseString(content)
        dom.normalize()
        
        entries=dom.getElementsByTagName('entry')
        
        for entry in entries:
            headline=AssociatedPressHeadlineModel()
            headline.id=entry.getElementsByTagNameNS(self.ATOM_NS, u'id')[0].firstChild.nodeValue
            headline.title=entry.getElementsByTagNameNS(self.ATOM_NS, u'title')[0].firstChild.nodeValue
            
            # get article categories
            headline.categories=[]
            content2=entry.getElementsByTagName('content')[0]
            divs=content2.getElementsByTagName('div')
            className=None
            for div in divs:
                x=div.getAttributeNode('class')
                if x:
                    className=x.nodeValue
                if className=='categories':
                    hrefs=div.getElementsByTagName('a')
                    for href in hrefs:
                        rel=href.getAttributeNode('rel').nodeValue
                        if rel=='tag':
                            categoryName=href.firstChild.nodeValue
                            if categoryName:
                                headline.categories.append(categoryName)
                  
            # get article authors
            headline.authors=[]
            authors=entry.getElementsByTagNameNS(self.ATOM_NS, u'author')
            for author in authors:
                author_names=author.getElementsByTagNameNS(self.ATOM_NS, u'name')
                for author_name in author_names:
                    headline.authors.append(author_name.firstChild.nodeValue)
            
            # get article update date    
            headline.updated= datetime.datetime.strptime(entry.getElementsByTagNameNS(self.ATOM_NS, u'updated')[0].firstChild.nodeValue, '%Y-%m-%dT%H:%M:%SZ')
            #get article external url
            headline.href=entry.getElementsByTagNameNS(self.ATOM_NS, u'link')[0].getAttributeNode('href').nodeValue;
            
            news.append(headline)
            
        return news
    def sendRequest(self,path=None,params=None):
        if params==None:
            params={}
        params[self.APIKEY]=Config.AP_APIKEY
        qs=urllib.urlencode(params)
        url=self.PROTOCOL+'://'+self.DOMAIN+'/v'+str(self.VERSION)+'/'+path+'?'+qs
        urlFetchResult = urlfetch.fetch(url,deadline=120)
        #if urlFetchResult.status_code != 200:
        return urlFetchResult.content
    def parseDate(self):
        #atomdate='2010-09-17T02:16:16Z';
        atomdate='2010-09-17T02:16:16Z';
        dateobj=datetime.datetime.strptime(atomdate,'%Y-%m-%dT%H:%M:%SZ')
        return dateobj
