# coding=UTF-8
# -*- coding: UTF-8 -*-
import datetime
import logging
import re

from google.appengine.api import taskqueue, memcache
from google.appengine.api import urlfetch, mail

from common.lib.CategoryLib import CategoryLib
from common.lib.Controller import Controller
from common.lib.KnowledgeLib import KnowledgeLib
from common.lib.MyHTMLParser import MyHTMLParser
from common.lib.Session import Session
from common.lib.SyytacitUrlFetch import SyytacitUrlFetch
from common.lib.Users import Users
from common.models.CategoryModel import CategoryModel
from module import user
from module.article.lib.ArticleLib import ArticleLib
from module.article.model.ArticleDetailModel import ArticleDetailModel
from module.article.model.ArticleModel import ArticleModel
from module.article.model.ArticleSubmitViewModel import ArticleSubmitViewModel
from module.article.model.SparseQuestion import SparseQuestion
from module.article.view.ArticleDetailView import ArticleDetailView
from module.article.view.ArticleSearchView import ArticleSearchView
from module.article.view.ArticleSubmitView import ArticleSubmitView
from module.comments.model.Comments import Comments
from module.home.HomeController import HomeController
from module.home.model.HomeModel import HomeModel
from module.home.view.NullView import NullView
from module.question.lib.QuestionLib import QuestionLib
from google.appengine.api.search import search

class ArticleController(Controller):
    
    def indexAction(self):
        model=HomeModel()
        model.user=self.user
        
        return ArticleDetailView(model)
    
    def searchAction(self,terms,sort='created',sort_order='descending',page=1):
        model={}
        try:
            page=int(page)
        except (TypeError,ValueError):
            page=1
        
        if page<1:
            page=1
        
        limit=10
        offset=(page-1)*limit
        
        if sort_order=='descending':
            direction=search.SortExpression.DESCENDING
        elif sort_order=='ascending':
            direction=search.SortExpression.ASCENDING
        else:
            sort_order='descending'
            direction=search.SortExpression.DESCENDING
            
        if sort=='alphabetical':
            expression='title'
            default_value='a'
        else:
            expression='created'
            default_value=datetime.datetime.now()
        
        
        model['articles']=[]
        model['terms']=terms
        model['sort']=sort
        model['sort_order']=sort_order
        model['page']=page
        model['limit']=limit
        model['user']=self.user
        model['num_records']=0
        
      
        if terms:
            model['metadescription']='Article Search Results for '+terms
            model['metakeywords']='Articles,'+terms
            model['page_subtitle']=model['metadescription']
        else:
            model['metadescription']='Search for Articles'
            model['metakeywords']='articles,search'
            model['page_subtitle']=model['metadescription']
            
        if model['page']>1:
            model['metadescription']=model['metadescription']+' - page '+str(model['page'])
            model['metakeywords']=model['metakeywords']+',page '+str(model['page'])
            if model['page_subtitle']:
                model['page_subtitle']=model['page_subtitle']+" - "
            model['page_subtitle']=model['page_subtitle']+'Page '+str(model['page'])
       
        
        index = search.Index(name="articles")
        sort1 = search.SortExpression(expression=expression, direction=direction, default_value=default_value)
        sort_opts = search.SortOptions(expressions=[sort1])
        query_options = search.QueryOptions(offset=offset,limit=limit,sort_options= sort_opts)
           
        if terms:
            query = search.Query(query_string="title: "+terms+" OR "+"description: "+terms, options=query_options)    
        
        article_keys=[]
        search_result = index.search(query)
        if search_result:
            model['num_records']=search_result.number_found
            
            #logging.info("found "+str(search_result.number_found)+" results for terms:"+terms);
            for document in search_result:
                article_keys.append({
                 "key":document.fields[9].value
                })
                    
        if article_keys:
            for record in article_keys:
                article=ArticleLib.getArticleBy('key', record['key'])
                if article:
                    article.tags=[]
                    acats=ArticleLib.getCategories(article)
                    for acat in acats:
                        article.tags.append(acat.name)
                    model['articles'].append(article)              
        
        model['num_records']=len(model['articles'])
   
        if model['articles']:
            model['nextpage']=page+1
        if page > 1:
            model['previouspage']=page-1
        
        return ArticleSearchView(model)
        #return ArticleSearchView(model)
    def detailAction(self,ihref,page=1):
        try:
            i=int(page);page=i;
        except ValueError:
            page=1
            
        model=ArticleDetailModel()
        model.article=ArticleLib.getByIhref(ihref)
        
        if not model.article:
            return HomeController().fourzerofourAction()
        model.page_subtitle=model.article.title
        model.metadescription=model.article.description
        
        if model.article:
           
            approved=ArticleLib.getApproval(model.article,self.user) 
            if approved==True:
                model.article.approved='1'
            elif approved==False:
                model.article.approved='0'
            else:
                model.article.approved=None
        
            model.article.tags=[]
            article_categories=[]
            article_cats=ArticleLib.getCategories(model.article)
            for article_cat in article_cats:
                model.article.tags.append(article_cat.name)
                article_categories.append(article_cat)
                
            model.metakeywords=",".join(model.article.tags)
            
            if not model.article.comment:
                c=Comments(text='None')
                c.save();
                model.article.comment=c
                model.article.save()
                
            model.comment_key=model.article.comment.key()
            question=QuestionLib.getRandomQuestion( model.article.tags)
            if question:
                
                if self.user:
                    signature=QuestionLib.getSignature(question.key().id(),Session.sessionid)
                else:
                    signature=None
                if question.question_type==1:
                    question_text=QuestionLib.toArray(question.question)
                else:
                    question_text=question.question
                model.article.question=SparseQuestion(question_type=question.question_type,id=question.key().id(),question=question_text,signature=signature)
            
        
            #(model.leaderboard,model.userstats,model.greater_userstats,model.lesser_userstats)=HomeController.getLeaderBoard(self.user,1,article_categories)
            #model.comments=CommentsLib.getComments(model.article.comment,page,limit)
            
            model.leaderboard=KnowledgeLib.getLeaderBoard(article_categories)
            model.userstats=KnowledgeLib.getUserStats(self.user,article_categories)
            model.lesser_userstats=KnowledgeLib.getRelativeUserStats(self.user,False,True,article_categories)
            model.greater_userstats=KnowledgeLib.getRelativeUserStats(self.user,True,False,article_categories)
        
        self.user.isadmin=self.isLoggedInAs('admin')
        model.user=self.user
        
        
        return ArticleDetailView(model)
    
    def demoteAction(self,article_key):
        model={"result":False}
        
        article=ArticleLib.getArticleBy("key", article_key)
        if article:
            article.r2=0
            article.v2=0
            article.save()
            ArticleLib.removeFromMemcache(article)
            
            model['result']=True
            
        return model
    def set_rankAction(self,article_key,rank=None):
        model={"rank":None}
        logging.info(rank)
        if rank!=None:
            rank=float(rank)
            logging.info(rank)
            article=ArticleModel.get(article_key)
            if article:
                article.sortkey=rank
                logging.info("rank="+str(article.sortkey))
                article.save()
            else:
                raise Exception("cant find article")
                
        return model
    
    def classifyAction(self,article_key=None):
        model={'num_article_cats':None}
        article=ArticleLib.getArticleBy("key",article_key)
        if article:
            model['num_article_cats']=ArticleLib.classify(article)
            ArticleLib.addToSearchIndex(article)
            
            if model['num_article_cats']==0:
                mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', '/article/classify results',"no categories found for "+article.title) 
        return NullView(model)
    
    
    """
    renders the 'submit article' page
    """
    def submitAction(self,community=None):
        model=ArticleSubmitViewModel()
        model.user=self.user
        model.metadescription='Submit an Article'
        model.metakeywords='submit article'
        
        if community:
            model.metadescription=model.metadescription+ ' to the '+community+' community'
            model.metakeywords=model.metakeywords+ ','+community
            
        model.page_subtitle=model.metadescription
            
        if model.user and model.user.username:
            user=model.user.username
        else:
            user=None
            
        model.article={"nofollow":"rel=nofollow","title":"","ihref":"/","href":"","tags":[],"username":user,"updated":datetime.datetime.now(),"description":"","category":community}
        
        return ArticleSubmitView(model)
    
    def saveAction(self,url,title=None,description=None,original_title=None,original_description=None,tags=None,post_target=None,category=None):
        self.requireLoggedin();
        model={"article":None}
        
        if category:
            category=category.lower().strip()
        if title:
            title=title.strip()
            title=MyHTMLParser().html_entity_decode(title)
            
        if post_target=='url' and not url:
            raise Exception('You must provide a url')
        
        if post_target=='syytacit' and not category:
            raise Exception('You must provide a category')
        
        if not title and not original_title:
            raise Exception('You must provide a title')
        
        #check for submission of a url that is already in the database
        article=ArticleLib.getByHref(url,False)
        
        if article:
            model['exception']={'message':"Url has already been submitted","type":"DuplicateUrl"}
            model['url']=ArticleLib.getFullUrl(article)
            return model;
             
        if not tags:
            tags=[];
            
        cats=[]
        for tag in tags:
            cat = CategoryLib.getByTag(tag.lower())
            if not cat:
                cat=CategoryModel(name=tag.lower())
                cat.save()
            cats.append(cat.key())
                
        comment=Comments(text="None")
        comment.save()
        import time
        if not url:
            url='http://www.syytacit.net/community/void'
        
        if not title:
            title=original_title
        if not description:
            description=original_description
        
        try:
            title=unicode(title,"UTF-8",errors="ignore")
        except UnicodeDecodeError:
            pass
        xarticle = ArticleModel(title=title,href=url,ihref='void',cats=cats,comment=comment,category=category)
        try:
            xarticle.subtitle=unicode(original_title,"UTF-8",errors="ignore")
        except UnicodeDecodeError:
            pass
            
        try:
            xarticle.subdescription=unicode(original_description,"UTF-8",errors="ignore")
        except UnicodeDecodeError:
            pass
        
        xarticle.username=self.user.username
        description=unicode(description,"UTF-8")
        xarticle.description=description
        xarticle.ihref=ArticleLib.createUrl(xarticle)
        xarticle.v2=10;
        xarticle.r2=100
        if post_target=='community':
            xarticle.url='http://www.syytacit.net/community/'+category+'/'+xarticle.ihref
            xarticle.href=xarticle.url
            xarticle.source='syytacit'
        xarticle.put()
        
        
        # put the article into the memcache article_queue
        ArticleLib.saveToMemcache(xarticle)
        
        # clear cache
        ArticleLib.getByIhref(xarticle.ihref,False,True)
        
        if post_target=='community':
            cat=CategoryLib.getByTag(category)
            if not cat:
                cat=CategoryModel(name=category)
                cat.save()
                CategoryLib.getByTag(category,False) # clear cache
                #article_cat=ArticleCategoryModel(article=xarticle,category=cat,catscore=1.0)
                userknowledges=Users.getUserKnowledge(xarticle.username, cat)
                if userknowledges.has_key(cat.name):
                    userknowledges_score=userknowledges[cat.name].score
                else:
                    userknowledges_score=0.01
                
        
        model['article']=xarticle
            
        if post_target=='url':
            taskqueue.add(queue_name="articleclassify",url='/article/classify/'+str(xarticle.key()))
            
        return NullView(model)
        
        
    def approveAction(self,article_key,approve=True):
        
        self.requireLoggedin()
        
        model={"article_key":article_key,"delta":0}
        key="approval_"+article_key+"_"+self.user.username
        memcache.set(key,approve)
        article=ArticleModel.get(article_key)
        if article:
            #if approve:
                #article.numapprovals=article.numapprovals+1
                #logging.info("numapprovals="+str(article.numapprovals))
                #article.save()
                #memcache.incr("n_approvals_"+article_key,1,None,1)
                
            approvals=ArticleLib.getApprovals(article,self.user)
            if approvals:
                logging.info("user "+self.user.username+" is trying to approve article "+article.ihref+" more than once")
            else:
                approvals=ArticleLib.approve(article, self.user.username, approve)
                if ArticleLib.applyApprovals(article,self.user,approvals,approve):
                    if approve==True:
                        model['delta']=1
                    else:
                        model['delta']=-1;
       
        return NullView(model)
    
    def rejectAction(self,article_key):
        return self.approveAction(article_key, False)
    
    def get_article_metaAction(self,url):
        self.requireLoggedin()
        
        #raise Exception('Unable to get content from  url')
    
        model={"title":None,"description":None}
        # validate the url
        
        from django.core.validators import URLValidator
        from django.core.exceptions import ValidationError
        
        val = URLValidator(verify_exists=False)
        try:
            val(url)
        except ValidationError, e:
            raise Exception("Invalid Url")
        
        
        # fetch the contents of the url
        # extract the meta tags (title description)
        
        try:
            #urlFetchResult = urlfetch.fetch(url,None,urlfetch.GET,{'User-Agent': "Syytacit"},False,True,10)
            urlFetchResult = SyytacitUrlFetch.fetch(url,None,urlfetch.GET,{},False,True,5)
            if urlFetchResult.status_code!=200:
                raise Exception('Unable to get content from  url')
        except Exception,e:
            raise Exception('Unable to get content from  url')
        
        #html = unicode(urlFetchResult.content,errors='replace')
        html=urlFetchResult.content
        if html:
            parser=MyHTMLParser()
            parser.getTitle(html)
            parser.getDescription(html)
            if parser.title:
                title = re.sub("\s\s+" , " ",parser.title)
                model["title"]=title
                
            else:
                logging.warn("no title fetched from "+url)
            if parser.description:
                
                
                if len(parser.description) > 500:
                    model["description"]=parser.description[0:495]+"..."
                else:
                    model["description"]=parser.description
            else:
                logging.warn("no description fetched from "+url)
        else:
            logging.warn("no html fetched from "+url)
    
      
        return NullView(model)
    
    def deleteAction(self,article_key):
        self.requireLoggedin('admin')
        
        article=ArticleModel.get(article_key)
        if not article:
            raise Exception('Article not found')
        
        ArticleLib.delete(article)
        
        model={'article_key':article_key}
        
        return model
    
    def archiveAction(self,article_key):
        model={"archived":False}
        article=ArticleLib.getByKey(article_key)
        if article:
            model['archived']=ArticleLib.archive(article)
        else:
            logging.error("Article not found "+article_key)
        return model
    
    def deletesearchindexAction(self):
        model={"total":0}
        model['total']=ArticleLib.deleteSearchIndex()
        return model
    
    def buildsearchindexAction(self):
        model={"total":0}
        
        #TODO: delete the existing records from the index
        model['total']=ArticleLib.buildSearchIndex()
        
        return model
        
        