# coding=UTF-8
# -*- coding: UTF-8 -*-
from google.appengine.api import urlfetch, memcache
from google.appengine.ext import db
from xml.dom.minidom import parseString,NamedNodeMap
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
from module.wiki.model.WikiModel import WikiModel
import datetime
import re
from hashlib import md5
from module.natlang.model.SentenceModel import SentenceModel
import urllib
import logging
from django.utils import simplejson
from module.wiki.lib.WikiHtmlParser import WikiHtmlParser
import pickle
from google.appengine.api.urlfetch import DownloadError
import sys
from common.models.QuestionModel import QuestionModel
from common.lib.SyytacitUrlFetch import SyytacitUrlFetch

#http://en.wikipedia.org/wiki/Wikipedia:Creating_a_bot#APIs_for_bots
#http://en.wikipedia.org/wiki/Special:ApiSandbox

class WikiLib():
    BASE_URL="http://en.wikipedia.org"
    BASE_CATEGORY_PORTAL_URL="wiki/Category:"
    ROOT_CATEGORY="Main_topic_classifications"
    ROOT_CATEGORY2="Main topic classifications"
    
    API_ENDPOINT='/w/api.php'
    EXCLUDE_CATEGORIES=["Categories","Content_portals","Semi-protected_portals","Main_topic_classifications","Categories_requiring_diffusion","Categories by parameter","Wikipedia categorization","Wikipedia categories","Contents"]
    SPECIAL_PAGES=['Talk:', 'User:', 'User_talk:', 'Wikipedia:', 'Wikipedia_talk:', 'File:', 'File_talk:', 'MediaWiki:', 'MediaWiki_talk:', 'Template:', 'Template_talk:', 'Help:', 'Help_talk:', 'Category:', 'Category_talk:', 'Portal:', 'Portal_talk;', 'Book:', 'Book_talk:', 'Draft:', 'Draft_talk:', 'Education_Program:', 'Education_Program_talk:', 'TimedText:', 'TimedText_talk:', 'Module:', 'Module_talk:'];
    def delete(wiki):
        i=0
        # delete all sentences attached to the wiki
        sentences=SentenceModel.all().filter("wiki =",wiki)
        for sentence in sentences:
            # delete all questions attached to the sentences
            questions=QuestionModel.all().filter("sentence in",[sentence.key()])
            for question in questions:
                i=i+1
                question.delete()
            i=i+1
            sentence.delete()
        
        i=i+1
        wiki.delete()
        
        return i
    def getMainTopicClassifications():
        cats=[]
        url = WikiLib.BASE_URL+"/"+WikiLib.BASE_CATEGORY_PORTAL_URL+"Main_topic_classifications"
        urlFetchResult = SyytacitUrlFetch.fetch(url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,10)
        html = unicode(urlFetchResult.content,errors='ignore')
        x=1+len(WikiLib.BASE_CATEGORY_PORTAL_URL)
        dom=parseString(html)
        dom.normalize()
        anchors=dom.getElementsByTagName("a")
        for anchor in anchors:
            att=anchor.attributes
            item=att.getNamedItem("href")
            if item != None:
                id=anchor.parentNode.nodeName+anchor.parentNode.parentNode.nodeName+anchor.parentNode.parentNode.parentNode.nodeName+anchor.parentNode.parentNode.parentNode.parentNode.nodeName
                if id=="divdivliul":
                    href=item.nodeValue
                    if href.find(WikiLib.BASE_CATEGORY_PORTAL_URL) == 1 :
                        if href[x:] in WikiLib.EXCLUDE_CATEGORIES:
                            continue
                        cat = WikiCategoryModel(name=href[x:],url=db.Link(WikiLib.BASE_URL+href))
                        cats.append(cat)
        
        return cats

    """
    returns a list of WikiCategoryModels that the url is tagged of
    @param topcat - the name of a wikicategory
    """    
    def getCategories(topcat,level=0):
        cats=[]
        if level > 4: return cats
        urlFetchResult = SyytacitUrlFetch.fetch(topcat.url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,10)
        html = unicode(urlFetchResult.content,errors='ignore')
        x=1+len(WikiLib.BASE_CATEGORY_PORTAL_URL)
        dom=parseString(html)
        dom.normalize()
        anchors=dom.getElementsByTagName("a")
        for anchor in anchors:
            att=anchor.attributes
            item=att.getNamedItem("href")
            if item != None:
                id=anchor.parentNode.nodeName+anchor.parentNode.parentNode.nodeName+anchor.parentNode.parentNode.parentNode.nodeName+anchor.parentNode.parentNode.parentNode.parentNode.nodeName
                if id=="spandivdivdiv":
                    href=item.nodeValue
                    if href.find(WikiLib.BASE_CATEGORY_PORTAL_URL) == 1 :
                        if href[x:] in WikiLib.EXCLUDE_CATEGORIES:
                            continue
                        cat = WikiCategoryModel(name=href[x:],url=db.Link(WikiLib.BASE_URL+href))
                        cats.append(cat)
        #topcat.save()                
        topcat.categories=[]
        for cat in cats:
            foo=WikiCategoryModel.all().filter("name =",cat.name).fetch(1,0)
            if len(foo) != 0:
                cat=foo[0]
            cat.parentcategory = topcat
            #cat.put()
            #topcat.categories.append(cat.key()
            topcat.categories.append(cat)
            
        #topcat.save()
        return cats
    
    def getCategoricalIndex():
        cats=[]
        url="http://en.wikipedia.org/wiki/Portal:Contents/Categorical_index";
        urlFetchResult = SyytacitUrlFetch.fetch(url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,10)
        html = unicode(urlFetchResult.content,errors='ignore')
        
        dom=parseString(html)
        dom.normalize()
        
        anchors=dom.getElementsByTagName("a")
        x=1+len(WikiLib.BASE_CATEGORY_PORTAL_URL)
        for anchor in anchors:
            att=anchor.attributes
            assert isinstance(att, NamedNodeMap)
            item=att.getNamedItem("href")
            if item != None:
                id=anchor.parentNode.nodeName+anchor.parentNode.parentNode.nodeName+anchor.parentNode.parentNode.parentNode.nodeName+anchor.parentNode.parentNode.parentNode.parentNode.nodeName
                if id=="idddldiv":
                    href=item.nodeValue
                    #ignore categories that are in the "exclude" list
                    if href[x:] in WikiLib.EXCLUDE_CATEGORIES:
                        continue
                    cat = WikiCategoryModel(name=href[x:],url=db.Link(WikiLib.BASE_URL+href))
                    cats.append(cat)
        return cats
           
    def getSubCategories(tag,html=None,cacheread=True,cachewrite=True):
        if cacheread:
            html=memcache.get('wikicatpage_'+tag)
            
        subcats=[]
        if not html:
            url = WikiLib.BASE_URL+"/"+WikiLib.BASE_CATEGORY_PORTAL_URL+tag
            urlFetchResult = SyytacitUrlFetch.fetch(url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,10)
            html = unicode(urlFetchResult.content,errors='ignore')
        x=1+len(WikiLib.BASE_CATEGORY_PORTAL_URL)
        dom=parseString(html)
        dom.normalize()
        anchors=dom.getElementsByTagName("a")
        for anchor in anchors:
            att=anchor.attributes
            item=att.getNamedItem("href")
            if item != None:
                href=item.nodeValue
                id=anchor.parentNode.nodeName+anchor.parentNode.parentNode.nodeName+anchor.parentNode.parentNode.parentNode.nodeName+anchor.parentNode.parentNode.parentNode.parentNode.nodeName
                if id=="divdivliul":
                    href=item.nodeValue
                    if href.find(WikiLib.BASE_CATEGORY_PORTAL_URL) >0 :
                        if href[x:] in WikiLib.EXCLUDE_CATEGORIES:
                            continue
                        subcats.append(href[x:])
                        #subcat = WikiCategoryModel(name=href[x:],url=db.Link(WikiLib.BASE_URL+href))
                        #subcats.append(subcat)
        memcache.set('wikicatpage_'+tag,html)
            
        return subcats
    """
    retrieve category information from wiki and save in datastore
    """
    def loadCategories():
        
        cats=WikiLib.getMainTopicClassifications()
        
        for cat in cats:
            #insert this category into the database if it is not already there
            foo=WikiCategoryModel.all().filter("name =",cat.name).fetch(1,0)
            if len(foo) != 0:
                cat=foo[0]
            
            cat.categories=[]
            
            # get the categories that this category is tagged with
            WikiLib.getCategories(cat)
            #subcats=WikiLib.getSubCategories(cat)
                   
        return None
    
    """
    for every category in the datastore, grab its subcategories from wikipedia
    """
    def loadSubCategories():
        # get all categories that dont have subcategories
        for cat in WikiCategoryModel.all():
            subcats=WikiCategoryModel.all().filter("parentcategory =",cat.key()).fetch(1,0)
            if len(subcats) == 0:
                subcats=WikiLib.getSubCategories(cat)
                for subcat in subcats:
                    subcat.parentcategory=cat
                    WikiLib.getCategories(cat)
        return None
    """
    @param cat - a WikiCategory
    """
    def getPages(cat):
        result=[]
        #url = WikiLib.BASE_URL+"/"+WikiLib.BASE_CATEGORY_PORTAL_URL+urllib.quote(cat.name);
        from google.appengine.api import memcache
        
        data=memcache.get('WikiLibgetPages'+cat.name)
        if not data:
            url = WikiLib.BASE_URL+"/"+WikiLib.API_ENDPOINT+"?action=query&list=categorymembers&format=json&cmtitle=Category:"+cat.name+"&cmlimit=10&generator=allpages&gaplimit=10"
            
            try:
                urlFetchResult = SyytacitUrlFetch.fetch(url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,30)
            except DownloadError as e:
                logging.info("Failed to download "+url)
                return result
            data = simplejson.loads(urlFetchResult.content)
            memcache.set('WikiLibgetPages'+cat.name,data,(86400*8))
        
        if data['query']['categorymembers']:
            for page in data['query']['categorymembers']:
                process_page=True
                # do not include some "special pages"
                for page_type in WikiLib.SPECIAL_PAGES:
                    foo=page['title'][:len(page_type)]
                    #logging.info(page['title']+'='+foo)
                    if foo==page_type:
                        #logging.info("skipping special page "+page['title'])
                        process_page=False
                page['title']=page['title'].replace(" ","_")
                if process_page:
                    href=WikiLib.BASE_URL+"/wiki/"+page['title']
                    wiki=WikiModel.all().filter("url =",href).get()
                    if not wiki:
                        # save this wiki url in the datastore
                        wiki=WikiModel(title=page['title'],url=href,rank=0,categories=[cat.key()])
                        if not wiki.title:
                            logging.error("no title found for "+wiki.url)
                            continue
                        wiki.put()
                        logging.info("added new wiki page "+page['title'])
                        result.append(wiki)
                    result.append(wiki)
        else:
            logging.info('failed to get list of pages for category: '+cat.name)
        
        return result
    
    def getPageCategories(wikititle,level=0):
        #/w/api.php?action=query&prop=categoryinfo&format=json&generator=categories&titles=Art&gclshow=!hidden&gcllimit=10
        from google.appengine.api import memcache
        cats=[]
        
        
        data=memcache.get('WikiLibgetPageCats'+wikititle)
        if not data:
            url = WikiLib.BASE_URL+"/"+WikiLib.API_ENDPOINT+"?action=query&format=json&generator=categories&titles="+wikititle.replace(' ','_')+"&gclshow=!hidden&gcllimit=10"
            
            try:
                urlFetchResult = SyytacitUrlFetch.fetch(url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,30)
                #logging.info("successfully downloaded "+url)
            except DownloadError as e:
                logging.warn("Unable to download "+url)
                logging.warn(sys.exc_info()[0])
                return cats
            data = simplejson.loads(urlFetchResult.content)
            memcache.set('WikiLibgetPageCats'+wikititle,data,(86400*8))
            
        if u'query' in data and u'pages' in data[u'query']:
            for id in data[u'query'][u'pages']:
                title=data[u'query'][u'pages'][id][u'title'].split(':')
                if title[1]:
                    
                    cat = WikiLib.getCategoryByName(title[1])
                    if not cat:
                        cat = WikiCategoryModel(name=title[1],url=db.Link(WikiLib.BASE_URL+'/'+WikiLib.BASE_CATEGORY_PORTAL_URL+title[1]))
                        cat.save()
                    cats.append(cat)
                else:
                    logging.error('failed to get page categories for '+wikititle)
        else:
            logging.error('failed to get page categories for '+wikititle)
            
        
        return cats
            
       
    """
    For the given tag, get and save sentences for later conversion to questions.
    """    
    def acquireSentences(tag):
        numsentences=0
        # get the wikicategory for the given tag
        cat=WikiCategoryModel.all().filter("name =",tag).get()
        if not cat:
            return 0
        # get all the wikimodels having this category
        q = WikiModel.all()
        q.filter("categories =",cat.key())
        q.order("date_updated") #oldest page
        wiki=q.get()
        if wiki:
            logging.info('acquiring sentences for '+wiki.url)
            numsentences=WikiLib.getSentences(wiki)
            if numsentences>0:
                cat.numsentences=cat.numsentences+numsentences
                cat.save()
            #update the date_updated date for the wiki
            wiki.date_updated=datetime.datetime.now()
            wiki.numsentences=numsentences
            wiki.save()
        else:
            logging.info('cant find wikis in '+tag)
        
        return numsentences
        
    def getNodeValues(e):
        text=''
        for child in e.childNodes:
            if child.nodeName=='sup':
                continue
            if child.nodeValue:
                text=text+child.nodeValue
            else:
                text=text+WikiLib.getNodeValues(child)
                
        return text
    
    def getSentences(wiki):
        
        #TODO: handle the case when more than one sentence occurs between quotes or parenthesis
        
        #the page http://en.wikipedia.org/wiki/Art fails to grab the sentence: For example, when the Daily Mail criticized Hirst's and Emin's work by arguing "For 1,000 years art has been one of our great civilising forces.
        
        sentencecount=0
        
        from google.appengine.api import memcache
        
        #check memcache first
        text=memcache.get('WikiLibgetSentences'+wiki.title)
        if not text:
            html=""
            foo=urllib.quote_plus(wiki.title.encode("utf-8"))
            url = WikiLib.BASE_URL+WikiLib.API_ENDPOINT+"?action=parse&format=json&page="+foo+"&prop=text&mobileformat=html"
            urlFetchResult = SyytacitUrlFetch.fetch(url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,30)
            data = simplejson.loads(urlFetchResult.content)
            
            if data.has_key('parse'):
                if not data['parse']['text']['*']:
                    logging.error('failed to get sentence for '+wiki.title)
                    return sentencecount 
                else:
                    html=data['parse']['text']['*']
                    
            if len(html) <64:
                logging.error("failed to get html for "+url)
                return 0
            
            parser=WikiHtmlParser()
            parser.feed(html)
            
            text=parser.text.replace("\n"," ").replace("\r"," ")
            
            memcache.set('WikiLibgetSentences'+wiki.title,text,7*86400)
        
        tok = pickle.load(open("nltk/english.pickle"))
        sentences = tok.tokenize(text)
        
        logging.info("found "+str(len(sentences))+" sentences")
        
        
        import math
        # TODO: join sentences having odd quotes
        i=0;total_quotes=0;num_sentences=len(sentences)
        order=0;sentencecount=0
        for sentence1 in sentences:
            offset=0;x=0
            p=sentence1.find('"',offset)
            while p != -1:
                offset=p+1;x=x+1;total_quotes=total_quotes+1
                p=sentence1.find('"',offset)
            
            offset=0;x1=0    
            p=sentence1.find('(',offset)
            while p != -1:
                offset=p+1;x1=x1+1;
                p=sentence1.find('(',offset)
                
            offset=0;x2=0
            p=sentence1.find(')',offset)
            while p != -1:
                offset=p+1;x2=x2+1;
                p=sentence1.find(')',offset)
                
            if math.ceil(x/float(2)) != (x/float(2)):
#                print("pos="+str(offset)+" x="+str(x)+ " x/2="+str(x/2))
                if i<(num_sentences-1) and sentences[i+1][0]=='"': # the next sentence ends the quote
                    sentence=sentence1+'"'
                elif sentence1[0]=='"':
                    sentence=sentence1[1:]
                else:
                    sentence=sentence1   
            elif x1!=x2:
                if i<(num_sentences-1) and sentences[i+1][0]==')': # the next sentence ends the parenthesis
                    sentence=sentence1+')'
                elif sentence1[0]==')':
                    sentence=sentence1[1:]
                else:
                    sentence=sentence1
            else:
                sentence=sentence1
                
            #print sentence1+"<HR>"
            offset=0;x=0
            i=i+1
           
            if len(sentence)<10:
                logging.warn("sentence too short for: "+sentence)
                continue
           
            if len(sentence)>501:
                logging.warn("sentence too long for: "+sentence)
                continue
            
            try:
                sentence=sentence.replace("\n"," ").replace("\r"," ")
                sentence=re.sub('\s{2,}', ' ', sentence).strip()
                m=md5(sentence.encode("ascii",errors="ignore"))
            except UnicodeEncodeError:
                logging.warn('UnicodeEncodeError on: '+sentence)
                continue
        
            signature=m.hexdigest()
            sentenceModel=SentenceModel.all().filter("signature =",signature).get()
            if sentenceModel:
                if sentenceModel.wiki == None:
                    sentenceModel.wiki=wiki
            else:
                sentenceModel = SentenceModel(score=0,sentence=sentence,signature=signature,order=order)
                sentenceModel.wiki = wiki
                sentenceModel.put()
                sentencecount=sentencecount+1
                order=order+1
                         
        return sentencecount
        
    def getCategoryUrl(name):
        url = WikiLib.BASE_URL+"/"+WikiLib.BASE_CATEGORY_PORTAL_URL+name
        return url
    """
    get category information from wikipedia and save in datastore
    """
    def getCategory(name,cacheread=True,cachewrite=True):
        from google.appengine.api import memcache
        
        #check memcache first
        curl=False
        if cacheread:
            curl=memcache.get('WikiLibgetCategory'+name)
        
        if not curl:
            url = WikiLib.BASE_URL+"/"+WikiLib.API_ENDPOINT+"?action=query&prop=info&format=json&inprop=url&titles=Category:"+name
            try:
                urlFetchResult = SyytacitUrlFetch.fetch(url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,30)
            except DownloadError:
                logging.error("unable to fetch contents from "+url);
                return None
            data = simplejson.loads(urlFetchResult.content)
            
            if data['query']['pages']:
                for r in data['query']['pages']:
                    if r != "-1":
                        curl=data['query']['pages'][r]['fullurl']
                        if cachewrite:
                            memcache.set('WikiLibgetCategory'+name,curl,7*86400)
                    else:
                        curl=False
                
        if not curl:
            return None
        
        category=WikiCategoryModel(name=name,url=curl)
        
        return category
    
    def getCategoryByName(name):
        from google.appengine.api import memcache
        
        cat=memcache.get('WikiLibgetCategoryByName'+name)
        if not cat:
            cat=WikiCategoryModel.all().filter("name =",name).get()
            memcache.set('WikiLibgetCategoryByName'+name,cat,7*86400)
        return cat
    
    def getTags(wiki,cacheread=True,cachewrite=True):
        tags=None
        
        key='wgt_'+str(wiki.key())
        if cacheread:
            tags=memcache.get(key)
            
        if tags==None:
            tags=[]
            wikicats=WikiCategoryModel.get(wiki.categories)
            for wikicat in wikicats:
                tags.append(wikicat.name)
                
        if cachewrite:
            memcache.set(key,tags)
            
        return tags
  
    getTags=staticmethod(getTags)
    getMainTopicClassifications=staticmethod(getMainTopicClassifications)  
    getCategoricalIndex=staticmethod(getCategoricalIndex)
    loadSubCategories=staticmethod(loadSubCategories)
    getPageCategories=staticmethod(getPageCategories)
    getSubCategories=staticmethod(getSubCategories)
    loadCategories=staticmethod(loadCategories)
    getCategories=staticmethod(getCategories)
    acquireSentences=staticmethod(acquireSentences)
    getSentences=staticmethod(getSentences)
    getPages=staticmethod(getPages)
    getCategory=staticmethod(getCategory)
    getCategoryUrl=staticmethod(getCategoryUrl)
    getNodeValues=staticmethod(getNodeValues)
    getCategoryByName=staticmethod(getCategoryByName)
    delete=staticmethod(delete)
    
    