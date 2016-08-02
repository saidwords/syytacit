# coding=UTF-8
# -*- coding: UTF-8 -*-
from HTMLParser import HTMLParseError
import datetime
import email
import logging
from random import randint
import xml.dom.minidom

from google.appengine.api import urlfetch, taskqueue, datastore_errors
from google.appengine.api.urlfetch import DownloadError, DeadlineExceededError

from common.lib.MLStripper import strip_tags
from common.lib.MyHTMLParser import MyHTMLParser
from common.lib.SyytacitUrlFetch import SyytacitUrlFetch
from module.article.lib.ArticleLib import ArticleLib
from module.article.model.ArticleModel import ArticleModel
from module.comments.model.Comments import Comments
import traceback


class RSSLib(object):
    
    def saveArticles(rss_url):
        logging.info("processing "+rss_url)
        
        num_articles=0
        skipped=0
        #def fetch(url, payload=None, method=GET, headers={},allow_truncated=False, follow_redirects=True,deadline=None, validate_certificate=None)
        
        try:
            urlFetchResult = SyytacitUrlFetch.fetch(rss_url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,20)
        except DownloadError,DeadlineExceededError:
            logging.info("Failed to download "+rss_url)
            return 0
        if urlFetchResult.status_code!=200:
            logging.error("url returned http  "+str(urlFetchResult.status_code)+":"+rss_url)
            return 0
        import re
        # loop through the xml, pulling out article urls
        result_xml = xml.dom.minidom.parseString(urlFetchResult.content)
        del urlFetchResult; #free memory?
        items = result_xml.getElementsByTagName('item')
        del result_xml; # free memory?
        htmlparser=MyHTMLParser()
        for item in items:
            # get the articles publication date
            elements=item.getElementsByTagName('pubDate')
            if not elements:
                #<dc:date>2014-06-03T09:37:45Z</dc:date>
                elements=item.getElementsByTagName('dc:date')
                
            if elements and elements[0] and elements[0].childNodes and elements[0].childNodes[0]:
                pubDate=elements[0].childNodes[0].data
                pubDate=pubDate.replace("\n"," ")
                try:
                    d=email.Utils.parsedate_tz( pubDate)
                except IndexError:
                    d=False   
                if d:
                    a=email.Utils.mktime_tz(d)
                    pubDate=datetime.datetime.fromtimestamp(a)
                else:
                    flag=False
                    try:
                        #d=datetime.datetime.strptime(pubDate, "%Y-%m-%dT%H:%M:%S.%f%Z")
                        pubDate=datetime.datetime.strptime(pubDate, "%Y-%m-%d %H:%M:%S")
                        flag=True
                    except ValueError:
                        flag=False
                    if not flag:
                        try:
                            pubDate=datetime.datetime.strptime(pubDate, "%Y-%m-%d %H:%M:%S.%f")
                            flag=True
                        except ValueError:
                            flag=False
                    if not flag:
                        try:
                            pubDate=datetime.datetime.strptime(pubDate, "%d %B %Y")
                            flag=True
                        except ValueError:
                            flag=False
                    if not flag:
                        try:
                            pubDate=datetime.datetime.strptime(pubDate, "%Y-%m-%dT%H:%M:%SZ")
                            flag=True
                        except ValueError:
                            flag=False
                    if not flag: # if we were not able to get the pubDate, then just set it to now
                        pubDate=datetime.datetime.now()

                if pubDate:
                    if pubDate < datetime.datetime.now()-datetime.timedelta(days=2): # dont load old articles
                        skipped=skipped+1
                        continue
                    
            else:
                pubDate=datetime.datetime.now()
                    
            elements=item.getElementsByTagName('link')
            if elements and elements[0].childNodes:
                link=elements[0].childNodes[0].data
                link=link.strip()
            else:
                continue
            elements=item.getElementsByTagName('title')
            if elements and elements[0].childNodes:
                title=elements[0].childNodes[0].data
                title=title.strip()
            else:
                continue
            
            # fetch the actual link and resolve its url
            try:
                urlFetchResult = SyytacitUrlFetch.fetch(link,None,urlfetch.GET,{},False,True,10)
                if urlFetchResult.status_code!=200:
                    logging.warn("unable to load "+link)
                if urlFetchResult.final_url and urlFetchResult.final_url != link:
                    link=urlFetchResult.final_url
                del urlFetchResult; #free memory?
                    
            except Exception,e:
                logging.error(e.message)
                continue
            
            existing_article=ArticleLib.getByHref(link)
            
            if existing_article:
                #logging.info("article already eixsts: "+link)
                continue
            del existing_article; #this frees memory?
            
            elements=item.getElementsByTagName('description')
            if elements and elements[0].childNodes:
                description=elements[0].childNodes[0].data
                description=description.replace("\n"," ")
                description=htmlparser.unescape(description)
                try:
                    #description=html.strip_tags(description)
                    description=strip_tags(description)
                except HTMLParseError:
                    logging.info("unable to strip tags from "+description)
                    continue
                description=re.sub("\s\s+" , " ",description).strip()
                if len(description)>500:
                    description=description[0:495]+"..."
            else:
                description=None
            
            title=title.replace("\n"," ")
            title=re.sub("\s\s+" , " ",title).strip()
            try:
                article = ArticleModel(title=title,href=link,ihref='null',description=description)
            except datastore_errors.BadValueError:
                logging.error("Failed to save "+link)
                stacktrace = traceback.format_exc()
                logging.error("%s", stacktrace)
                continue
            
            article.ihref=ArticleLib.createUrl(article)
            article.username="syytacit"
            article.r2=randint(1,2000)
            article.v2=10
            # create a top level comment.
            comment=Comments(text=".")
            comment.put()
            article.comment=comment
            article.created=pubDate
            article.updated=pubDate
            article.put();
            ArticleLib.saveToMemcache(article)
            ArticleLib.getByHref(link,False,True) # clear cache
            ArticleLib.getByIhref(article.ihref,False,True) #clear cache
            num_articles=num_articles+1
            
            #taskqueue.add(queue_name="articleclassify",url='/json/article/classify/'+str(article.key()),retry_options=taskqueue.TaskRetryOptions(task_retry_limit=0)) 
            
            del article; # this frees memory?
        
        return num_articles
    saveArticles=staticmethod(saveArticles)
    