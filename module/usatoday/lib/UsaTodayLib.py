# coding=UTF-8
# -*- coding: UTF-8 -*-
from module.usatoday.lib.UsaTodayWebService import UsaTodayWebService
from module.article.model.ArticleModel import ArticleModel
from module.article.lib.ArticleLib import ArticleLib
from module.comments.model.Comments import Comments
import logging
from common.lib.MyHTMLParser import MyHTMLParser
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch_errors import DeadlineExceededError

class UsaTodayLib:
    def save_latest_headlines(self):
        response=[]
        articles=UsaTodayWebService().getLatestArticles()
        urlfetch.set_default_fetch_deadline(60)
                
        import time
        for article in articles:
            # do not insert the article if it already is in the db
            try:
                
                urlFetchResult = urlfetch.fetch(article.href,None,urlfetch.GET,{},False,True,60)
            except DeadlineExceededError:
                logging.error("DeadlineExceededError: "+article.href)
                continue
                
            if urlFetchResult.status_code!=200:
                logging.error("url returned http  "+str(urlFetchResult.status_code)+":"+article.href)
                continue
            
            if urlFetchResult.final_url and urlFetchResult.final_url != article.href:
                article.href=urlFetchResult.final_url
            
            existing_article=ArticleLib.getByHref(article.href)
            if existing_article:
                logging.warn("skipping duplicate article "+article.href) 
            else:      
                article.title=MyHTMLParser().html_entity_decode(article.title)
                xarticle = ArticleModel(title=article.title,id=article.id,href=article.href,updated=article.updated,ihref='null',description=article.description)
                xarticle.ihref=ArticleLib.createUrl(xarticle)
                xarticle.source=ArticleLib.SOURCE_USATODAY
                xarticle.username="syytacit"
                xarticle.sortkey=float(int(time.time()))/10000000000.0
                # create a top level comment.
                comment=Comments(text=".")
                comment.put()
                xarticle.comment=comment
                
                xarticle.put();
                response.append(xarticle)
                
        return response