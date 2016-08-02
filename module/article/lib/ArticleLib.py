# coding=UTF-8
# -*- coding: UTF-8 -*-
from collections import OrderedDict
import datetime
import logging
from math import sqrt
from random import randint
import re

from google.appengine.api import memcache, taskqueue, urlfetch
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from google.appengine.api.search import search
from google.appengine.ext import db
from webapp2_extras.appengine.auth.models import User

from common.lib.CategoryLib import CategoryLib
from common.lib.NatLangLib import NatLangLib
from common.lib.SyytacitUrlFetch import SyytacitUrlFetch
from common.lib.Users import Users
from common.models.ArticleRank import ArticleRank
from common.models.CategoryModel import CategoryModel
from module.article.model.ArticleApproveModel import ArticleApproveModel
from module.article.model.ArticleCategoryModel import ArticleCategoryModel
from module.article.model.ArticleModel import ArticleModel
from module.comments.lib.CommentsLib import CommentsLib
from module.opencalais.lib.OpenCalais import OpenCalais
from module.wiki.lib.WikiLib import WikiLib
from module.wiki.model.WikiCategoryModel import WikiCategoryModel


class ArticleLib:
    SOURCE_AP='ap' # associated press
    SOURCE_USATODAY='usat' #USA Today
    GRAVITY=1
    
    def addToSearchIndex(article):
        index = search.Index(name="articles")
        categories=ArticleLib.getCategories(article)
        cats=[]
        for category in categories:
            cats.append(category.name)
        document = search.Document(
            doc_id=None,
            fields=[
                    search.TextField(name='title', value=article.title),
                    search.TextField(name='subtitle', value=article.subtitle),
                    search.TextField(name='description', value=article.description),
                    search.TextField(name='subdescription', value=article.subdescription),
                    search.TextField(name='href', value=article.href),
                    search.TextField(name='ihref', value=article.ihref),
                    search.TextField(name='category', value=article.category),
                    search.DateField(name='created',value=article.created),
                    search.TextField(name='categories', value=",".join(cats)),
                    search.TextField(name='key', value=str(article.key()))       
            ]
        )
        index.put(document)
        
        return True
    
    def removeFromSearchIndex(article_key):
        index = search.Index(name="articles")
        query_string = "key="+str(article_key) 
        try:
            results = index.search(query_string) 
        
            for scored_document in results:
                index.delete(scored_document.doc_id)
                return True

        except search.Error:
            logging.exception('removeFromSearchIndex failed')

        return False
    
    def deleteSearchIndex(limit=100):
        total=0
        index = search.Index(name="articles")
        
        while True:
            if total>=limit:
                break
            
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [document.doc_id for document in index.get_range(ids_only=True)]
            if document_ids:
                total=total+len(document_ids)
            if not document_ids:
                break
        # Delete the documents for the given ids from the Index.            
        if document_ids:
            index.delete(document_ids)
        return total
    def createUrl(article):
        assert isinstance(article, ArticleModel)
        # lowercase the title
        url=article.title.lower()
                
        #remove all lame characters
        p=re.compile("([^a-z 0-9-])")
        url=p.sub("", url)
        
        # reduce sequential spaces to one space
        p=re.compile("\s{2,}")
        url=p.sub(" ", url)
        
        #remove duplicate '-'
        url=re.sub("-+","-", url)
        url=url.strip("-")
        
        words=url.split(" ")
        url=""
        counter=0
        for word in words:
            counter=counter+1
            url=url+word
            if counter>2:
                article=ArticleLib.getByIhref(url)
                if not article:
                    break
            url=url+"-"
            #remove duplicate '-'
            url=re.sub("-+","-", url)
            
        if article:
            counter=1
            while article and counter < 10:
                newurl=url+"-"+str(counter)
                
                article=article=ArticleLib.getByIhref(newurl)
                counter=counter+1
                if not article:
                    url=newurl
        if article:
            return None
        return url
    
    """
    Gets the list of top articles from memcache
    """
    def new_getTopNews(page=1,category=None,cacheread=True,cachewrite=True):
        
        articles=None
        key='topnews_'+str(page)+"_"+str(category)
            
        if cacheread:
            articles=memcache.get(key)
        
        updatecache=False
        if not articles:
            articles=ArticleLib.getTopNews(page, category)
            updatecache=True
           
        if articles:
            keys=[]
            #TODO: get the correct article.numapprovals and article.numcomments
            for article in articles:
                keys.append("n_approvals_"+str(article.key()))
                keys.append("ncomments_"+str(article.key()))
            records=memcache.get_multi(keys)
#            for key,value in records.items():
#                logging.info(key+"="+str(value))
            for article in articles:
                if records.has_key("n_approvals_"+str(article.key())) and records["n_approvals_"+str(article.key())]:
                    if records["n_approvals_"+str(article.key())] > article.numapprovals:
                        #logging.info("overriding numapprovals to "+str(records["n_approvals_"+str(article.key())]))
                        article.numapprovals=records["n_approvals_"+str(article.key())]
                if records.has_key("ncomments_"+str(article.key())) and records["ncomments_"+str(article.key())]:
                    if records["ncomments_"+str(article.key())] > article.numcomments:
                        article.numcomments=records["ncomments_"+str(article.key())]
        if updatecache:
            #logging.info("memcache set articles") 
            memcache.set(key,articles,86400)
        
        return articles
   
    def getTopNews(page=1,category=None):
        
        limit=10
        articles=[]    
        if category:
            c=CategoryLib.getByTag(category)
            acs=ArticleCategoryModel.all().filter("archived =",False).filter("category =",c).order("-r2").fetch(limit,(page-1)*limit)
            for ac in acs:
                try:
                    articles.append(ac.article)
                except ReferencePropertyResolveError:
                    ac.delete()
        else:
            articles=ArticleModel.all().filter("archived =",False).order("-r2").fetch(limit,(page-1)*limit)
            
        return articles
    
    def getLatestNews(page=1,category=None):
        limit=10
        articles=[]
        if category:
            c=CategoryLib.getByTag(category)
            acs=ArticleCategoryModel.all().filter("category =",c).order("-updated").fetch(limit,(page-1)*limit)
            for ac in acs:
                articles.append(ac.article)
        else:
            articles=ArticleModel.all().order("-created").fetch(limit,(page-1)*limit)
                
        return articles
        
        
    """
    get a list of all categories that dont have a wiki page associated. Then tries to find the wiki page for the given category
    """
    def map_categories_to_wiki():
        
        page=0
        limit=50
        num_missing_cats=0
        allcats={}
        tags=ArticleLib.getTopTags(cacheread=False)
        cats=[]
        
        for tag in tags:
            category=CategoryLib.getByTag(tag)
            if category and category.wikiname==None:
                allcats[category.name]=category
                                
        if len(cats)<limit:
            cats=CategoryModel.all().filter("wikiname =",None).fetch(limit-len(cats),page*limit)
            for cat in cats:
                if not allcats.has_key(cat.name):
                    allcats[cat.name]=cat
                else:
                    logging.error(cat.name+" is DUPLICATED!")
                    
        for tag,cat in allcats.items():
            wikiname=cat.name.capitalize().replace(' ','_')
            wikicat=WikiCategoryModel.all().filter("name =",wikiname).get()
            
            if not wikicat:
                wikiname=cat.name.title().replace(' ','_')
                wikicat=WikiCategoryModel.all().filter("name =",wikiname).get()
            
            if wikicat:
                #logging.info("There is a wikicategory in the DB named "+wikiname)
                cat.wikiname=wikiname
                cat.save()
                CategoryLib.getByTag(cat.name,True,False,True) #reload cache
                
            else:
                wikicat=WikiLib.getCategory(wikiname)
                if not wikicat:
                    wikiname=cat.name.capitalize().replace(' ','_')
                    wikicat=WikiLib.getCategory(wikiname)
                if wikicat:
                    #logging.info("FOUND wikipedia category "+wikicat.name)
                    wikicat.save()
                    cat.wikiname=wikicat.name
                    cat.save()
                    CategoryLib.getByTag(cat.name,True,False,True) #reload cache
                else:
                    num_missing_cats=num_missing_cats+1
                    #logging.info("cant find wikipedia category for "+wikiname)
        
        return num_missing_cats
    
    def getTopTags(cacheread=True,cachewrite=True):
        tags=[]
        # check for tags in memcache
        if cacheread:
            tags=memcache.get('toptags')
        if tags:
            return tags
        
        # get list of top most frequent tags
        h={} # histogram
        tags=[]
        articles=ArticleLib.getTopNews()
        #simulate numcomments
        for article in articles:
            article_cats=ArticleLib.getArticleCategories(article)
            for cat in article_cats:
                if h.has_key(cat.category.name):
                    h[cat.category.name]=h[cat.category.name]+cat.catscore
                else:
                    h[cat.category.name]=cat.catscore
        
        #sort
        tags=sorted(h,key=h.__getitem__,reverse=True)
                
        #save tags to memcache
        if cachewrite:
            memcache.set('toptags',tags,900)
    
        return tags

    
    """
    return a dict of categories that this article has
    """
    def getCategories(article,cacheread=True,cachewrite=True):
        categories=[]
        
        key='get_article_cats_'+str(article.key())
            
        if cacheread:
            categories=memcache.get(key)
        
        if cacheread==False or categories==None:
            categories=[]
            records=ArticleCategoryModel.all().filter("article =",article).fetch(32)
            for record in records:
                categories.append(record.category)
        
        if cachewrite:
            memcache.set(key,categories)
       
        return categories
    
    def getArticleCategories(article,cache=True,clear=False):
        
        article_cats=False
        
        if clear:
            memcache.delete('get_article_cats2_'+str(article.key()))
        
        if cache:
            article_cats=memcache.get('get_article_cats2_'+str(article.key()))
        
        if cache==False or not article_cats: 
            article_cats=ArticleCategoryModel.all().filter("article =",article).fetch(32)
            if not article_cats:
                article_cats=[]
            
        if cache:
            memcache.set('get_article_cats2_'+str(article.key()),article_cats)
        
        return article_cats
    
    def getArticleCategory(article,category,cache=True):
        article_cat=False
        
        if cache:
            article_cat=memcache.get('getarticlecat'+str(article.key()))
        
        if cache==False or not article_cat: 
            article_cat=ArticleCategoryModel.all().filter("article =",article).filter("category =",category).get()
            if not article_cat:
                article_cat=False
            
        if cache:
            memcache.set('getarticlecat'+str(article.key()),article_cat)
        
        return article_cat
    
    
        
    def getByIhref(ihref,cache=True,clear=False):
        return ArticleLib.getArticleBy("ihref", ihref, cache, cache)
        
    
    def getArticleBy(column,value,cacheread=True,cachewrite=True):
        article=None
        if column=='href':
            value=value.encode("utf-8",errors="ignore")
        key='getarticle_'+column+"_"+str(value)
        numapprovals=None
        numcomments=None
        r2=None
        v2=None
        if cacheread:
            article=memcache.get(key)
            if article:
                numapprovals=memcache.get("n_approvals_"+str(article.key()))
                numcomments=memcache.get("ncomments_"+str(article.key()))
                r2=memcache.get("article_r2_"+str(article.key()))
                v2=memcache.get("article_v2_"+str(article.key()))
                if v2:
                    v2=v2-4611686018427387403
        if not article:
            if column=='key':
                article=ArticleModel.get(value)
            else:
                article=ArticleModel.all().filter(column+" =",value).get()
            if not article:
                article=False
            if cachewrite:
                memcache.set(key,article)
        
        if article:
            if numapprovals and numapprovals > article.numapprovals:
                article.numapprovals=numapprovals
            if numcomments and numcomments > article.numcomments:
                article.numcomments=numcomments
            if r2 and r2!=article.r2:
                article.r2=r2
            if v2 and v2!=article.v2:
                article.v2=v2
            
            
        return article
    def getByHref(href,cache=True,clear=False):
        return ArticleLib.getArticleBy("href", href, cache, cache)
    
    def approve(article,username,approve=True):
        approvals={}
        article_cats=ArticleLib.getCategories(article)
        userknowledge=Users.getUserKnowledge(username)
        if article_cats:
            for category in article_cats:
                if userknowledge.has_key(category.name):
                    score=userknowledge[category.name].score
                else:
                    score=0.01
                score=score+10
                article_approval=ArticleApproveModel(article=article,username=username,score=score,approve=approve,category=category)
                article_approval.save()
                
                approvals[article_approval.category.name]=article_approval
                
        if article.category:
            if not approvals.has_key(article.category):
                if userknowledge.has_key(article.category):
                    score=userknowledge[article.category].score
                else:
                    score=0.01
                score=score+10
                category=CategoryLib.getByTag(article.category)
                if category:
                    article_approval=ArticleApproveModel(article=article,username=username,score=score,approve=approve,category=category)
                    article_approval.save()
                   
                    approvals[article.category]=article_approval
        return approvals
    
    def newApplyApprovals(article,approvals,approve=True):
        raise Exception("deprected function?")
        key="articlerank_"+str(article.key())
        articlerank=memcache.get(key)
        if not articlerank:
            articlerank=ArticleRank(rank=article.r2,hrank=article.hrank,v=article.v2,key=article.key())
            
        article_cats=ArticleLib.getArticleCategories(article)
        impact=0.0
        for article_cat in article_cats:
            if approvals.has_key(article_cat.category.name):
                if approvals[article_cat.category.name].approve:
                    impact=impact+(approvals[article_cat.category.name].score/100)
                else:
                    impact=impact-(approvals[article_cat.category.name].score/100)

        articlerank.rank=articlerank.rank+impact
        
        # save the articlerank back to memcache
        memcache.set(key,articlerank)
        
        return True
    
        
    """
    Apply the given users knowledge about a category (from ArticleApproval) to the articles 'score'
    """
    def applyApprovals(article,user1=None,approvals1=None,approve=True):
        x=0
        if not article.numapprovals:
            article.numapprovals=0
            
        if not article.r2:
            article.r2=0
        if not article.v2:
            article.v2=0
        
        if user1:
            users=[user1]
        else:
            users=User.query().fetch(200)
            
        for user in users:
            x=x+1
            if not user1:
                user.username=user.auth_ids[0]
            
            if approvals1:
                approvals=approvals1
            else:
                approvals=ArticleLib.getApprovals(article, user)
            if approve:
                article.numapprovals=article.numapprovals+1
                memcache.incr("n_approvals_"+str(article.key()),1,None,article.numapprovals-1)
                #foo=memcache.get("n_approvals_"+str(article.key()))
                #logging.info("incrememted napprovals to "+str(foo))
            article_cats=ArticleLib.getArticleCategories(article)
            
            for article_cat in article_cats:
                if approvals.has_key(article_cat.category.name):
                    if approve:
                        article_cat.v2=article_cat.v2+int(approvals[article_cat.category.name].score*100)
                    else:
                        article_cat.v2=article_cat.v2-int(approvals[article_cat.category.name].score*100)
                else:
                    if approve:
                        article_cat.v2=article_cat.v2+1
                    else:
                        article_cat.v2=article_cat.v2-1
            if article_cats:
                db.put(article_cats)
                
            impact=10+ArticleLib.calculate_impact(article, user.username)
            
            #logging.info("apply_impact to article: "+str(article.key()))
            #logging.info("apply impact = "+str(impact))    
            #foo=memcache.get("article_r2_"+str(article.key()))
            #logging.info("current rank ="+str(foo))
            
            if approve:
                #memcache.incr("article_r2_"+str(article.key()),impact)
                #velocity=memcache.get("article_v2_"+str(article.key()))
                #logging.info("current v2 = "+str(velocity))
                #logging.info("incrementing velocity +"+str(impact))
                if article.v2+impact < 9223372036854774807:
                    #memcache.incr("article_r2_"+str(article.key()),impact,None,article.r2+impact)
                    memcache.incr("article_v2_"+str(article.key()),impact,None,10)
                    article.v2=article.v2+impact
            else:
                #logging.info("descrementing velocity +"+str(impact))
                #memcache.decr("article_r2_"+str(article.key()),impact)
                if article.v2-impact >=0:
                    #memcache.decr("article_r2_"+str(article.key()),impact,None,article.r2-impact)
                    memcache.decr("article_v2_"+str(article.key()),impact,None,2)
                    article.v2=article.v2-impact
                    
        article.save()
        # clear cache
        #article_cats=ArticleLib.getArticleCategories(article,True,True)
         
        return True
    
    
    """
    remove the given users knowledge about a category (from ArticleApproval) from the articles 'score'
    """
    def removeApprovals(article,user1=None):
        page=0;limit=100
        
        if user1: 
            users=[user1]
        else:# if no user specified, then apply all users
            users=User.all().fetch(limit,page*limit)
            
        while users:
            for user in users:
                approvals=ArticleLib.getApprovals(article, user)
                if approvals:
                    logging.info("TODO: lock the ArticleCategory records for update")
                    article_cats=ArticleLib.getCategories(article)
                    if article_cats:
                        for article_cat in article_cats:
                            if approvals.has_key(article_cat.category):
                                article_cat.r2=article_cat.r2-(approvals[article_cat.category].score/100)
                            else:
                                article_cat.r2=article_cat.r2-(0.01/100)
                            article_cat.save()
                            
                            
            page=page+1
            if not user1:
                users=User.all().fetch(limit,page*limit)
        
        return None
    
    
    def confidence(ups, downs):
        if ups + downs == 0:
            return 0
        else:
            n = ups + downs
    
            if n == 0:
                return 0
    
            z = 1.0 #1.0 = 85%, 1.6 = 95%
            phat = float(ups) / n
            return ((phat + z*z/(2*n) - z * sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n))
        
    def getApproval(article,user,cacheread=True):
        
        if not user or not user.username:
            return None
        
        approval=None
        key="approval_"+str(article.key())+"_"+user.username
        if cacheread:
            approval=memcache.get(key)
            
        if approval==None:
            if user:
                record=ArticleApproveModel.all().filter("article =",article).filter("username =",user.username).get()
                if record:
                    approval=record.approve
                else:
                    approval='None'
            else:
                approval='None'
            memcache.set(key,approval,86400+randint(1,3600))
        
        if approval=='None':
            approval=None
        return approval
    
    def getApprovals(article,user,limit=32):
        approvals={}
     
        records=ArticleApproveModel.all().filter("article =",article).filter("username =",user.username).fetch(limit,0)
        for record in records:
            approvals[record.category.name]=record
            
        return approvals
                    
    def delete(article):
        ArticleLib.removeFromMemcache(article)
        ArticleLib.removeFromSearchIndex(article.key())
        # delete all the aticle categories
        article_cats=ArticleLib.getArticleCategories(article, False)
        for article_cat in article_cats:
            article_cat.delete()
            
        #delete all comments
        if article.comment:
            CommentsLib.deleteChildren(article.comment)
            article.comment.delete()
                    
        # delete the article
        article.delete()
        
        # clear the cache
        memcache.set('getByIhref'+article.ihref,False)
        #TODO: also update the 'topnews' cache
        
        return True
    
    def getFullUrl(article):
        if article.category:
            return 'http://www.syytacit.net/community/'+article.category+'/'+article.ihref
        else:
            return 'http://www.syytacit.net/article/detail/'+article.ihref
    
    """
    Load all articles, ranks, and velocities into memcache for fast processing
    """
    def reload_memcache():
        #if flush_memcache_to_db() has not been run:
        #        flush_memcache_to_db()
        #        taskqueue.add(reload_memcache());
        #        return False
        
        #lock this process
        lock=memcache.add("reload_memcache_lock",1,10*60)
        if not lock:
            logging.info("another process has this function locked")
            return False
        
        memcache.set("article_queue",0,86400+3600)
        num_articles=0
       
        logging.info("reloading article info into memcache")
        for article in ArticleModel.all().filter("archived =",False): #TODO: use memcache.set_multi()
            num_articles=num_articles+1
            ArticleLib.saveToMemcache(article) #TODO: do a batch saveToMemcache([])
            
        logging.info("loaded "+str(num_articles)+" articles into memcache")
        memcache.delete("reload_memcache_lock")
        return num_articles
    
    def sort_articles():
        # get ALL articles from article_queue
        index=memcache.get("article_queue")
        if not index:
            logging.error("article_queue not in memcache")# self.reload_memcache
            ArticleLib.reload_memcache()
            return False
        keys=[]
        for i in range(1,index+1):
            keys.append("article_queue_"+str(i))
        
        articles=memcache.get_multi(keys)
        num_articles=len(articles)
        
        #get the ranks of the articles 
        r2_keys=[]; v2_keys=[];
        for key,article in articles.items(): #TODO: skip duplicate articles
            if article and article['key']:
                r2_keys.append("article_r2_"+article['key'])
                v2_keys.append("article_v2_"+article['key'])
            else:
                del articles[key]
                #TODO: reload the record into memcache? ArticleLib.saveToMemcache(article,key)
        article_ranks={}
        r2_records=memcache.get_multi(r2_keys)
        for key,rank in r2_records.items():
            article_key=key[11:]
            article_ranks[article_key]=rank
         
        v2_records=memcache.get_multi(v2_keys)
        article_velocities={}
        for key,velocity in v2_records.items():
            article_key=key[11:]
            article_velocities[article_key]=velocity
        
        #logging.info("found "+str(len(article_ranks))+" ranks in memcache")
        #logging.info("found "+str(len(article_velocities))+" velocities in memcache")
        
        #apply gravity and impact
        #logging.info(len(articles))
        memcache_keys={}
        for mkey,article in articles.items():
            if article and article['key']:
                key=article['key']
                if article_ranks.has_key(key) and article_velocities.has_key(key):
                    if article_velocities[key]>9223372036854774807:
                        article_velocities[key]= 9223372036854774807
                    if article_ranks[key]>9223372036854774807:
                        article_ranks[key]= 9223372036854774807
                    # if the article rank is not increasing and its rank is already below zero and its an old article, then archive it
                    
                    if article_velocities[key] <= 4611686018427387403 and article_ranks[key] <= 0 :
                        #logging.info(str(article_velocities[key])+ ":"+str(article_ranks[key]))
                        if article_velocities[key] < 100:
                            memcache.set("article_v2_"+key,100)
                        if article_ranks[key] <0:
                            memcache.set("article_r2_"+key,0)# TODO: the minuium rank should be the time at which the article was submitted
                        
                        if article['created'] < datetime.datetime.now()-datetime.timedelta(days=3):
                            taskqueue.add(url="/article/archive/"+key)
                    else:
                        #logging.info("article_key="+key)
                        #logging.info("current r2="+str(articles[mkey]['r2']))
                        #logging.info("current v2="+str(articles[mkey]['v2']))
                        #logging.info("current velocity="+str(article_velocities[key]-4611686018427387403))
                        #adjusted_article_velocity=article_velocities[key]-4611686018427387403;
                        articles[mkey]['v2']=(article_velocities[key]-4611686018427387403)-ArticleLib.GRAVITY
                        articles[mkey]['r2']=article_ranks[key]+(articles[mkey]['v2']);
                        memcache_keys["article_v2_"+key]=articles[mkey]['v2']+4611686018427387403
                        memcache_keys["article_r2_"+key]=articles[mkey]['r2']
                        memcache_keys[mkey]=articles[mkey]
                        
                        #memcache.set("article_v2_"+key,articles[key]['v2'])
                        #memcache.set("article_r2_"+key,articles[key]['r2'])
                        #logging.info("new r2="+str(articles[mkey]['r2']))
                        #logging.info("new v2="+str(articles[mkey]['v2']))
                        #logging.info("new velocity="+str(article_velocities[key]-4611686018427387403))
                else:
                    #logging.warn("no ranks found for article "+key)
                    articlemodel=ArticleLib.getArticleBy('key', key)
                    if articlemodel:
                        ArticleLib.saveToMemcache(articlemodel,mkey)
                    
                #logging.info(str(orig_rank)+":"+str(articles[key]['r2']))
        if memcache_keys:
            memcache.set_multi(memcache_keys)
            #for key,value in memcache_keys.items():
            #    logging.info("memcache.set("+key+","+str(value)+")")
                   
        records = OrderedDict(sorted(articles.items(), key=lambda x: x[1]['r2'],reverse=True))
        
        articles=[]
        i=0
        memcache_keys={}
        update=False;page=1;category=None
        for key,article in records.items():
            i=i+1;
            record=ArticleLib.getByKey(article['key'])
            
            if article['v2'] <=0 and article['r2'] <=0:
                pass
            else:
                if record:
                    if record.v2!=article['v2']:
                        update=True
                        record.v2=article['v2']
                    if record.r2!=article['r2']:
                        update=True
                        record.r2=article['r2']
            if record:     
                articles.append(record)
                if i>10 and update:
                    i=0
                    key='topnews_'+str(page)+"_"+str(category)
                    memcache_keys[key]=articles
                    #logging.info("1. saving "+str(len(memcache_keys))+" records to memcache")
                    #memcache.set(key,articles)
                    articles=[]
                    page=page+1
                
            #logging.info(str(article['r2'])+":"+str(article['v2']))
                
        #write the sorted list of articles back to memcache:
        if update and articles:
            key='topnews_'+str(page)+"_"+str(category)
            #memcache.set(key,articles)
            memcache_keys[key]=articles
        
        if memcache_keys:
            memcache.set_multi(memcache_keys)
        return num_articles
    def getByKey(key,cacheread=True,cachewrite=False):
        return ArticleLib.getArticleBy("key", key, cacheread, cachewrite)
       
    def flush_memcache_to_db():
        keys=[];total=0
        index=memcache.get("article_queue")
        if not index:
            logging.error("article_queue not found in memcache")
            return total
        for i in range(1,index+1):
            keys.append("article_queue_"+str(i))
        articles=memcache.get_multi(keys)
        logging.info("pulled "+str(len(articles))+" articles from memcache")
        
        r2_keys=[]; v2_keys=[];
        for key,article in articles.items(): #TODO: skip duplicate articles
            r2_keys.append("article_r2_"+article['key'])
            v2_keys.append("article_v2_"+article['key'])
        
        # get article ranks    
        article_ranks={}
        r2_records=memcache.get_multi(r2_keys)
        for key,rank in r2_records.items():
            article_key=key[11:]
            article_ranks[article_key]=rank
        logging.info("pulled "+str(len(article_ranks))+" article_ranks from memcache")
        
        # get article velocities
        article_velocities={}
        v2_records=memcache.get_multi(v2_keys)
        for key,velocity in v2_records.items():
            article_key=key[11:]
            article_velocities[article_key]=velocity
            #logging.info("velocity for article "+article_key+" == "+str(velocity))
        logging.info("pulled "+str(len(article_velocities))+" article_velocities from memcache")
           
        records=[];num_records=0;update=False
        for key,article in articles.items(): #TODO: skip duplicates
            articlemodel=ArticleLib.getByKey(article['key'])
            if not articlemodel:
                pass;#logging.error("article not found "+article['key'])
            else: 
                update=False
                if article_velocities.has_key(article['key']):
                    adjusted_article_velocity=article_velocities[article['key']]-4611686018427387403;
                        
                    if articlemodel.v2!=adjusted_article_velocity:
                        update=True
                        #logging.info("setting v2 from "+str(articlemodel.v2)+" to "+str(article_velocities[article['key']])+" for article "+article['key'])
                        articlemodel.v2=adjusted_article_velocity
                        #logging.info("v2="+str(articlemodel.v2))
                        
                else:
                    pass;#logging.error("no velocity found for article "+article['key'])
                if article_ranks.has_key(article['key']):
                    if articlemodel.r2!=article_ranks[article['key']]:
                        update=True
                        articlemodel.r2=article_ranks[article['key']]
                    #if article_ranks[article['key']]>0:
                    #    logging.info("r2="+str(article_ranks[article['key']]))
               
                #TODO: also flush the 'numapprovals' property
                if update:
                    records.append(articlemodel)
                    #logging.info("v2="+str(articlemodel.v2)+" for article "+str(articlemodel.key()))
                    num_records=num_records+1
                    if num_records >100:
                        logging.info("saving 100 records")
                        db.save(records)
                        total=total+num_records
                        records=[];num_records=0
            
        if records:
            logging.info("saving "+str(num_records)+" records")
            total=total+num_records
            db.save(records)
        return total
    def saveToMemcache(article,key=None): 
        #logging.info(str(article.key())+" v2="+str(article.v2))
            
        #TODO: also process categories
        index=memcache.get("article_queue")
        if not index:
            memcache.set("article_queue",0,86400+3600)
        
        if not key:
            index=memcache.incr("article_queue",1,None,1)
            key="article_queue_"+str(index)
            
        if key:
            #logging.info("saving article to memcache "+str(article.key()))
            #if article.v2>0:
            memcache.set(key,{"key":str(article.key()),"r2":article.r2,"v2":article.v2,"created":article.created},86400+3600)
            if article.r2<0:
                article.r2=0
            memcache.set("article_r2_"+str(article.key()),int(article.r2),86400+3600)
            #logging.info("memcache.set(article_v2_"+str(article.key())+",int("+str(article.v2)+"+4611686018427387403,86400+3600)")
            memcache.set("article_v2_"+str(article.key()),int(article.v2)+4611686018427387403,86400+3600)
        
            #memcache.set('getarticle_key_'+str(article.key))
            return True
        else:
            logging.error("failed to save article to memcache")
        
        return False
    
    def calculate_impact(article,username):
        impact=0
        
        # based on the users knowledge of the categories related to the article, calculate an 'impact'
        categories=ArticleLib.getCategories(article)
        userknowledge=Users.getUserKnowledge(username)
        for category in categories:
            if userknowledge.has_key(category.name):
                impact=impact+int(userknowledge[category.name].score*100)
            else:
                impact=impact+1
        
        num_categories=len(categories)
        if num_categories>0:
            impact=int((0.0+impact)/num_categories)
        
        return impact
    def archive(article):
        # only archive the article if its is more than 3 days old
        r=False
        if article.created < datetime.datetime.now()-datetime.timedelta(days=3):
            ArticleLib.removeFromMemcache(article)
            article.archived=True
            article.save()
            r=True
            # remove article info from memcache queues
        
        return r
    def removeFromMemcache(article,category=None):
        memcache.set("article_v2_"+str(article.key()),0)
        memcache.set("article_r2_"+str(article.key()),0)
        index=memcache.get("article_queue")
        if not index:
            logging.error("article_queue not in memcache")# self.reload_memcache
            return False
        else:
            keys=[]
            for i in range(1,index+1):
                keys.append("article_queue_"+str(i))
            
            articles=memcache.get_multi(keys)
            for key,record in articles.items():
                if record['key']==article.key():
                    record['r2']=0;
                    record['v2']=0;
                    memcache.set(key,record)
            records=True
            page=1
            while records:
                records=ArticleLib.new_getTopNews(page)
                if records:
                    i=0
                    for record in records:
                        if record.key()==article.key():
                            key='topnews_'+str(page)+"_"+str(category)
                            records.remove(record)
                            memcache.set(key,records)
                            records=False
                            break
                        i-i+1
                page=page+1
                
                    
        return True 
    def classify(article):
        num_article_cats=0
        update_article=False
        
        tags=[]
        
        if article:
            try:
                urlFetchResult = SyytacitUrlFetch.fetch(article.href,None,urlfetch.GET,{},False,True,5)
                if urlFetchResult.status_code!=200:
                    return 0
                if urlFetchResult.final_url and urlFetchResult.final_url != article.href:
                    article.href=urlFetchResult.final_url
                    update_article=True
            except Exception,e:
                logging.error(e.message)
                return 0
            
            tags=OpenCalais.classify(urlFetchResult.content)
            biggest_tag=None
            shortest_tag=None
            if tags:
                biggest_tag=tags[0]
                shortest_tag=tags[0]
                article.cats=[]
                article.catscore=[]
                unique_tags={}
                for tag in tags:
                    tag.name=tag.name.lower().strip()
                    unique_tags[tag.name]=tag
                    if biggest_tag.score < tag.score:
                        biggest_tag=tag
                    if len(tag.name) < len(shortest_tag.name):
                        shortest_tag=tag
                    
                for name,tag in unique_tags.items():
                    #logging.info("OC tag="+name)
                    cat=CategoryLib.getByTag(name)   
                    if not cat:
                        cat=CategoryModel(name=name)
                        cat.save()
                        CategoryLib.addToSearchIndex(cat)
                    article_cat=ArticleLib.getArticleCategory(article,cat)
                    if not article_cat:
                        article_cat=ArticleCategoryModel(article=article,category=cat,catscore=tag.score)
                        article_cat.save()
                    
                    if not hasattr(article_cat,'r2'):
                        article_cat.r2=0
                    if not hasattr(article_cat,'v2'):
                        article_cat.v2=0

                    userknowledges=Users.getUserKnowledge(article.username,cat)
                    if userknowledges.has_key(cat.name):
                        article_cat.r2=article_cat.r2+int(userknowledges[cat.name].score*100)
                    else:
                        article_cat.r2=article_cat.r2+1
                    
                    num_article_cats=num_article_cats+1
            
        if update_article or not article.category:
            if biggest_tag:
                cat=CategoryLib.getByTag(biggest_tag.name)
                if cat:
                    article.category=biggest_tag.name   
                
            article.save()
       
        impact=10+ArticleLib.calculate_impact(article, article.username)
        
        memcache.incr("article_v2_"+str(article.key()),impact)
                
        if num_article_cats>0:
            #clear cache
            ArticleLib.getArticleCategories(article, False, True)
            ArticleLib.getCategories(article, False,True)
        return num_article_cats
    
    def buildSearchIndex(page=1,limit=100):
        
        page=int(page)
        limit=int(limit)
        total=0
        index = search.Index(name="articles")
        
        articles=ArticleModel.all()
        db_cursor = memcache.get('art_search_index_cur')
        if db_cursor:
            articles.with_cursor(start_cursor=db_cursor)
            
        for article in articles:
            if total>=limit:
                break
            
            categories=ArticleLib.getCategories(article)
            cats=[]
            for category in categories:
                cats.append(category.name)
            document = search.Document(
                doc_id=None,
                fields=[
                    search.TextField(name='title', value=article.title),
                    search.TextField(name='subtitle', value=article.subtitle),
                    search.TextField(name='description', value=article.description),
                    search.TextField(name='subdescription', value=article.subdescription),
                    search.TextField(name='href', value=article.href),
                    search.TextField(name='ihref', value=article.ihref),
                    search.TextField(name='category', value=article.category),
                    search.DateField(name='created',value=article.created),
                    search.TextField(name='categories', value=",".join(cats)),
                    search.TextField(name='key', value=str(article.key()))       
                ]
           )
            index.put(document)
            total=total+1
            
        if total==0:
            memcache.delete('art_search_index_cur')
        else:
            # Get updated cursor and store it for next time
            db_cursor = articles.cursor()
            memcache.set('art_search_index_cur', db_cursor)
            
        return total
    
    buildSearchIndex=staticmethod(buildSearchIndex)                            
    removeFromMemcache=staticmethod(removeFromMemcache)
    archive=staticmethod(archive)
    calculate_impact=staticmethod(calculate_impact)
    saveToMemcache=staticmethod(saveToMemcache)
    getByKey=staticmethod(getByKey)
    createUrl = staticmethod(createUrl)
    getTopNews = staticmethod(getTopNews)
    getLatestNews = staticmethod(getLatestNews)
    map_categories_to_wiki = staticmethod(map_categories_to_wiki)
    getTopTags = staticmethod(getTopTags)
    getApprovals = staticmethod(getApprovals)
    applyApprovals = staticmethod(applyApprovals)
    getCategories=staticmethod(getCategories)
    getArticleCategories=staticmethod(getArticleCategories)
    removeApprovals = staticmethod(removeApprovals)
    getApproval=staticmethod(getApproval)
    confidence=staticmethod(confidence)
    approve=staticmethod(approve)
    getByIhref=staticmethod(getByIhref)
    getArticleCategory=staticmethod(getArticleCategory)
    delete=staticmethod(delete)
    getByHref=staticmethod(getByHref)
    getFullUrl=staticmethod(getFullUrl)
    newApplyApprovals=staticmethod(newApplyApprovals)
    new_getTopNews = staticmethod(new_getTopNews)
    reload_memcache=staticmethod(reload_memcache)
    sort_articles=staticmethod(sort_articles)
    flush_memcache_to_db=staticmethod(flush_memcache_to_db)
    getArticleBy=staticmethod(getArticleBy)
    classify=staticmethod(classify)
    addToSearchIndex=staticmethod(addToSearchIndex)
    removeFromSearchIndex=staticmethod(removeFromSearchIndex)
    deleteSearchIndex=staticmethod(deleteSearchIndex)