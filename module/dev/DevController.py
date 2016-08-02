# coding=UTF-8
# -*- coding: UTF-8 -*-
import datetime
import hashlib
import logging
import os
import random
import time

from google.appengine.api import taskqueue, memcache
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
from google.appengine.ext import ndb, db
from webapp2_extras.appengine.auth.models import User, Unique
from common.lib.CategoryLib import CategoryLib
from common.lib.Controller import Controller
from common.lib.KnowledgeLib import KnowledgeLib
from common.models.AnswerModel import AnswerModel
from common.models.CategoryModel import CategoryModel
from common.models.MapReduceModel import MapReduceModel
from common.models.QuestionModel import QuestionModel
from common.models.SparseUser import SparseUser
from common.models.UserAnswerModel import UserAnswerModel
from common.models.UserKnowledgeModel import UserKnowledgeModel
from module import category
from module.article.lib.ArticleLib import ArticleLib
from module.article.model.ArticleApproveModel import ArticleApproveModel
from module.article.model.ArticleCategoryModel import ArticleCategoryModel
from module.article.model.ArticleModel import ArticleModel
from module.comments.lib.CommentsLib import CommentsLib
from module.comments.model.CommentApproveModel import CommentApproveModel
from module.comments.model.Comments import Comments
from module.dev.model.DevModel import DevModel
from module.dev.view.DevView import DevView
from module.natlang.model.SentenceModel import SentenceModel
from module.usatoday.lib.UsaTodayLib import UsaTodayLib
from module.wiki.lib.WikiLib import WikiLib
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
from module.wiki.model.WikiModel import WikiModel
from django.utils import html
from random import randint


#from google.appengine.api.users import User
class DevController(Controller):
    
    def fooAction(self):
        model={"x":None}
        page=1
        
        articledates=[]
        flag=True
        while flag:
            newarticles=ArticleLib.getLatestNews(page)
            if not newarticles:
                flag=False
            for article in newarticles:
                if article.updated < datetime.datetime.now()-datetime.timedelta(days=5):
                    flag=False
                    break
                articledates.append(article.updated)
            page=page+1
        
        
        
        return model
    
    
        
                
    def dump_memcacheAction(self,key):
        model={"v2":0,"r2":0,"article":None}
        
        model['v2']=memcache.get("article_v2_"+key)
        model['r2']=memcache.get("article_r2_"+key)
        index=memcache.get("article_queue")
        for i in range(1,index+1):
            article=memcache.get("article_queue_"+str(i))
            #logging.info("article at position "+str(i)+"="+article['key'])
            if article:
                if article['key']==key:
                    model['article']=article
            else:
                logging.info("article not found in queue in position "+str(i))
        return model
    
    
    
    def mapreduceAction(self):
        model={"result":None}
        filekey = "/tmp/filekey"
        blob_key = "blobkey"
        
        #article=ArticleModel.all().get()
        article=MapReduceModel
        
        logging.info(article)
    
        if issubclass(article, ndb.Model):
            model['result']=True;
        else:
            model['result']=False;
            
        record=MapReduceModel()
        
        logging.info(record)
        record.wilson=1.010101
        record.put()
        
        logging.info(record)
    
        #pipeline = WordCountPipeline(filekey, blob_key)
        #pipeline.start()

        return model
    
    def add_property_article_velocityAction(self,page=1,limit=50):
        model={"total":0}
        page=int(page)
        limit=int(limit)
        
        i=0
        records=ArticleModel.all()
        db_cursor = memcache.get('add_property_cursor')
        if db_cursor:
            records.with_cursor(start_cursor=db_cursor)
        
        updated_records=[]
        #keys=[]
        for record in records:
            if i > limit:
                break
            i=i+1
                
            record.r2=0
            record.v2=0
            updated_records.append(record)
            
        if updated_records:
            db.put(updated_records)
            
        model['total']=i
        if i==0:
            memcache.delete('add_property_cursor')
        else:
            # Get updated cursor and store it for next time
            db_cursor = records.cursor()
            memcache.set('add_property_cursor', db_cursor) 
        
        return model
    def reset_all_article_ranksAction(self,page=1,limit=50):
        model={"total":0}
        page=int(page)
        limit=int(limit)
        
        i=0
        records=ArticleModel.all()
        db_cursor = memcache.get('reset_art_cur')
        if db_cursor:
            records.with_cursor(start_cursor=db_cursor)
        
        updated_records=[]
        #keys=[]
        for record in records:
            if i > limit:
                break
            i=i+1
                
            record.r2=randint(1,500)
            record.v2=0
            updated_records.append(record)
            
        if updated_records:
            db.put(updated_records)
            
        model['total']=i
        if i==0:
            memcache.delete('reset_art_cur')
        else:
            # Get updated cursor and store it for next time
            db_cursor = records.cursor()
            memcache.set('reset_art_cur', db_cursor) 
        
        return model
    
    def delete_corrupt_articlesAction(self,page=1,limit=50):
        model={"total":0,"deletions":0}
        page=int(page)
        limit=int(limit)
        
        i=0
        records=ArticleModel.all()
        db_cursor = memcache.get('db_cursor')
        if db_cursor:
            records.with_cursor(start_cursor=db_cursor)
        
        deleted_records=[]
        
        for record in records:
            if i >= limit:
                break;
            i=i+1
            
            if record.title and record.title.find("http://") >=0:
                model['deletions']=model['deletions']+1
                deleted_records.append(record)   
        
        if deleted_records:
            db.delete(deleted_records) 
        model['total']=i
        if i==0:
            memcache.delete('db_cursor')
        else:
            # Get updated cursor and store it for next time
            db_cursor = records.cursor()
            memcache.set('db_cursor', db_cursor) 
        
        return model
    def add_property_article_cat_velocityAction(self,page=1,limit=50):
        model={"total":0}
        page=int(page)
        limit=int(limit)
        
        i=0
        records=ArticleCategoryModel.all()
        db_cursor = memcache.get('add_property_cursor')
        if db_cursor:
            records.with_cursor(start_cursor=db_cursor)
        
        updated_records=[]
        #keys=[]
        for record in records:
            if i > limit:
                break
            i=i+1
                
            record.r2=0
            record.v2=0
            updated_records.append(record)
            
        if updated_records:
            db.put(updated_records)
            
        model['total']=i
        if i==0:
            memcache.delete('add_property_cursor')
        else:
            # Get updated cursor and store it for next time
            db_cursor = records.cursor()
            memcache.set('add_property_cursor', db_cursor) 
        
        return model
    
    def archive_articlesAction(self,page=1,limit=50):
        model={"total":0,'num_updated':0}
        page=int(page)
        limit=int(limit)
        
        i=0;
        records=ArticleModel.all().filter("archived =",False)
        db_cursor = memcache.get('archive_articles_cur')
        if db_cursor:
            records.with_cursor(start_cursor=db_cursor)
        
        #keys=[]
        for record in records:
            if i > limit:
                break
            i=i+1
            if ArticleLib.archive(record):
                model['num_updated']=model['num_updated']+1
            
        model['total']=i
        if i==0:
            memcache.delete('archive_articles_cur')
        else:
            # Get updated cursor and store it for next time
            db_cursor = records.cursor()
            memcache.set('archive_articles_cur', db_cursor) 
        
        return model
    
    
    def unicodeAction(self):
        import encodings
        
        model={"sentence":None,"signature":None}
        sentence="At the same time, it sees that the economic organism has become truly global – has moved beyond national boundaries – so that when the economy is seen from a national perspective this is only partial and potentially harmful"
        
        #sentence=unicode(sentence).encode('utf-8'); # orginal from the datastore api
        sentence=unicode(sentence,"UTF-8")
        sentence=unicode(sentence).encode('utf-8')
        model['sentence']=sentence
        return model
    
    def fix_unicode_tagsAction(self,page=1,limit=100,tag=None):
        model=DevModel()
        total=0
        
        
        if tag:
            try:
                category=CategoryLib.getByTag(tag,False,False)
            except UnicodeDecodeError:
                #utag=tag.encode('utf-8')
                #utag=tag.encode('ascii')
                utag=unicode(tag, 'utf-8')
                #utag=unicode(tag,errors="ignore")
                #utag=tag.decode('utf-8')  # or:
                #utag=unicode(tag)
                category=CategoryLib.getByTag(utag,False,False)
                
                logging.info(category.name)
                
                
            #c=CategoryModel.all(keys_only=True).filter("name =",tag.encode('utf-8')).get()
            
            
            #category.name=utag
            #category.save()
            total=total+1
            categories=[1]
        else:
            
            p=int(page)
            l=int(limit)
            categories=CategoryModel.all().fetch(l,p*l)
            for category in categories:
                try:
                    category=CategoryLib.getByTag(category.name,False,False)
                except UnicodeDecodeError:
                    logging.info("fixing "+category.name)
                    name=unicode(category.name, 'utf-8')
                    category.name=name
                    category.save()
                    total=total+1
               
        model.messages=["modified "+str(total)+" of "+str(len(categories))+" records"]
        logging.info(model.messages) 
        return DevView(model)
    
    def fix_missing_wiki_titlesAction(self,page=1,limit=100):
        model={"total":0,"foo":0}
        page=int(page)
        limit=int(limit)
        wikis=WikiModel.all().fetch(limit,(page-1)*limit)
        for wiki in wikis:
            if not wiki.title:
                model['total']=model['total']+1
                pos = wiki.url.rfind('/')
                if pos > 0:
                    wiki.title=wiki.url[pos+1:]
                    wiki.save()
                else:
                    logging.error("invalid url "+wiki.url)
                        
        model['foo']=len(wikis)
        return model
    
    def delete_useless_wikisAction(self):
        model={"total":0,"deletions":0,"wiki":None}
        wikis=WikiModel.all().order('title')
        db_cursor = memcache.get('deletewiki_cursor')
        if db_cursor:
            wikis.with_cursor(start_cursor=db_cursor)
        
        i=0
        for wiki in wikis:
            if i > 100:
                break;
            i=i+1
            for page_type in WikiLib.SPECIAL_PAGES:
                pos = wiki.url.find(page_type) # The offset is optional
                if pos >0:
                    logging.info("deleting "+wiki.url)
                    WikiLib.delete(wiki)
                    model['deletions']=model['deletions']+1
                
        model['total']=i
        if i==0:
            memcache.delete('deletewiki_cursor')
        else:
            # Get updated cursor and store it for next time
            db_cursor = wikis.cursor()
            memcache.set('deletewiki_cursor', db_cursor) 
            
        return model
    def delete_duplicate_wikisAction(self,page=1,limit=100):
        model={"num_renamed_wikis":0,"num_duplicate_wikis":0,"num_deleted_wikis":0,"total":0,"num_deleted_sentences":0,"num_moved_sentences":0}
        page=int(page)
        limit=int(limit)
        
        wikis=WikiModel.all().order('title')
        
        db_cursor = memcache.get('dedupwiki_cursor')
        if db_cursor:
            wikis.with_cursor(start_cursor=db_cursor)
            
        prevwiki=None
        
        i=0
        for wiki in wikis:
            if i > limit:
                break
            i=i+1
            if not wiki.title:
                logging.error("no title found for wiki "+wiki.url)
                return model
            if " " in wiki.title or " " in wiki.url:
                    wiki.title=wiki.title.replace(" ","_")
                    wiki.url=wiki.url.replace(" ","_")
                    wiki.save()
                    model['num_renamed_wikis']=model['num_renamed_wikis']+1
            if prevwiki and prevwiki.title==wiki.title:
                logging.warn("duplicate wiki "+wiki.title)
                model['num_duplicate_wikis']=model['num_duplicate_wikis']+1
                #delete the wiki that has no sentences attaced
                sentences=SentenceModel.all().filter("wiki =",wiki).get()
                psentences=SentenceModel.all().filter("wiki =",prevwiki).get()
                if sentences and psentences: # if both have sentences, then move all sentences from one wiki to the other. then delete the duplcate wik 
                    logging.warn("both wikis have sentences. merging...")
                    
                    # copy all non-duplicate sentences out of wiki into prevwiki
                    sentences=SentenceModel.all().filter("wiki =",wiki).fetch(100,0)
                    for sentence in sentences:
                        psentence=SentenceModel.all().filter("wiki =",prevwiki).filter("signature =",sentence.signature).get()
                        if psentence:
                            #this sentence already exists in prevwiki, just delete it
                            model['num_deleted_sentences']=model['num_deleted_sentences']+1
                            sentence.delete()
                        else:
                            # add this sentence to prevwiki
                            sentence.wiki=prevwiki
                            sentence.save()    
                            model['num_moved_sentences']=model['num_moved_sentences']+1                
                            
                else:
                    if not sentences:
                        model['num_deleted_wikis']=model['num_deleted_wikis']+1
                        wiki.delete()
                        wiki=None
                    if not psentences:
                        model['num_deleted_wikis']=model['num_deleted_wikis']+1
                        prevwiki.delete()
                    
            prevwiki=wiki
        if prevwiki:
            model['wiki']=prevwiki.title
        model['total']=i
        if i==0:
            memcache.delete('dedupwiki_cursor')
        else:
            # Get updated cursor and store it for next time
            db_cursor = wikis.cursor()
            memcache.set('dedupwiki_cursor', db_cursor)
        
        return model
    
    
    def delete_duplicate_articlesAction(self,page=1,limit=100):
        model={"num_duplicate_articles":0,"num_deleted_articles":0,"total":0}
        page=int(page)
        limit=int(limit)
        
        articles=ArticleModel.all().order('title')
        
        db_cursor = memcache.get('deduparticle_cursor')
        if db_cursor:
            articles.with_cursor(start_cursor=db_cursor)
            
        prev=None
        
        i=0
        for article in articles:
            if i > limit:
                break
            i=i+1
           
            if prev and prev.href==article.href:
                model['num_duplicate_articles']=model['num_duplicate_articles']+1
                # delete the comments
                try:
                    if article.comment:
                        CommentsLib.deleteChildren(article.comment)
                except ReferencePropertyResolveError:
                    article.comment=None 
                    
                # delete the article categories
                articlecats=ArticleLib.getArticleCategories(article)
                if articlecats:
                    db.delete(articlecats)
                #delete the article:
                logging.warn("deleting duplicate article "+article.href)
                article.delete()
                model['num_deleted_articles']=model['num_deleted_articles']+1
                    
            prev=article
        
        model['total']=i
        if i==0:
            memcache.delete('deduparticle_cursor')
        else:
            # Get updated cursor and store it for next time
            db_cursor = articles.cursor()
            memcache.set('deduparticle_cursor', db_cursor)
        
        return model
     
    def delete_duplicate_sentencesAction(self,page=1,limit=100):
        
        model={"num_deleted_sentences":0,"total":0,"num_duplicate_sentences":0,"sentence":None}
        page=int(page)
        limit=int(limit)
        
        sentences=SentenceModel.all().order("signature")
    
        # If the application stored a cursor during a previous request, use it
        db_cursor = memcache.get('dedupsentences_cursor')
        if db_cursor:
            sentences.with_cursor(start_cursor=db_cursor)
            
        # Iterate over the results 100 times
        i=0
        prev=None
        for sentence in sentences:
            i=i+1
            if i > limit:
                break
            if prev and prev.signature==sentence.signature:
                model['num_duplicate_sentences']=model['num_duplicate_sentences']+1
                # if the sentence has questions attached then dont delete it
                questions=QuestionModel.all().filter("sentences in",[sentence.key()]).get()
                if not questions:
                    sentence.delete()
                    model['num_deleted_sentences']=model['num_deleted_sentences']+1
            
            prev=sentence
        if prev:
            model['sentence']=prev.sentence
        model['total']=i
        if i==0:
            memcache.delete('dedupsentences_cursor')
        else:
            # Get updated cursor and store it for next time
            db_cursor = sentences.cursor()
            memcache.set('dedupsentences_cursor', db_cursor)
        return model
    
    def checkEnv(self):
        return True
        if os.environ['SERVER_SOFTWARE'].find('Development') != 0:
            raise Exception("dev functions only available in Dev environment")
        
    def defaultAction(self,segments,qs):
        return self.indexAction()
    
    
    def indexAction(self):
        
        self.checkEnv()
            
        return DevView(DevModel)

    def delete_all_user_answersAction(self):
        page=0
        limit=100
        answers=[1]
        total=0
        while len(answers) >0:
            answers=UserAnswerModel.all().fetch(limit,page*limit)
            for answer in answers:
                answer.delete()
                total=total+1
            page=page+1
            logging.info("deleted "+str(total)+" records")
        model=DevModel()
        
        model.messages.append("deleted "+str(total)+" records")
            
        return DevView(DevModel())
    
    
    def delete_all_answersAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        answers=[1]
        while answers:
            answers=AnswerModel.all().fetch(limit,page*limit)
            page=page+1
            for answer in answers:
                answer.delete()
                total=total+1
        model.messages=["deleted "+str(total)+" records"]
        
        return DevView(model)
    
    def delete_all_wikimodelsAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=WikiModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                
                sentences=[1]
                spage=1
                while sentences:
                    sentences=SentenceModel.all().filter("wiki =",record).fetch(limit,(spage-1)*limit)
                    logging.info("found "+str(len(sentences))+" sentences attached to wiki page "+record.title)
                    spage=spage+1
                    if sentences:
                        for sentence in sentences:
                            sentence.delete()
                record.delete()
                total=total+1
            
        model.messages=["deleted "+str(total)+" records"]
        
        return DevView(model)
    
    def set_categories_for_wikipagesAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=WikiModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                cats=WikiLib.getPageCategories(record.title)
                
                flag=False
                for cat in cats:
                    if cat.key() not in record.categories:
                        flag=True
                        record.categories.append(cat.key())
                if flag:
                    record.save()
                    total=total+1
            
        model.messages=["deleted "+str(total)+" records"]
        
        return DevView(model)
    
    def delete_non_fib_questionsAction(self):
        model={"messages":[]}
        self.checkEnv()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=QuestionModel.all().fetch(limit,page*limit)
            for record in records:
                pos = record.question.find("__") # The offset is optional
                if pos < 0: # not found
                    record.delete()
                    total=total+1
            page=page+1
        model['messages'].append("deleted "+str(total)+" records")
        return model
    
    
    def delete_orphaned_answersAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=AnswerModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                question=QuestionModel.all().filter("correct_answer =",record).get()
                if not question:
                    record.delete()
                    total=total+1
        model.messages=["deleted "+str(total)+" records"]
        
        logging.info(model.messages[0])
        
        return DevView(model)
    
    def delete_article_categoriesAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=ArticleCategoryModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                try:
                    if not record.category:
                        record.delete()
                        total=total+1
                except Exception as e:
                    total=total+1
                    record.delete()
                    
                    
                        
        model.messages=["deleted "+str(total)+" records"]
        
        logging.info(model.messages[0])
        
        return DevView(model)
        
    def create_test_usersAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        
        total=0
        
        """
        fusers=[1]
        fusers=User.query().fetch(200)
        for user in fusers:
            if user and user.email_address:
                if '@syytacit.com'==user.email_address[-13:]:
                    Unique.delete_multi( map(lambda s: 'User.auth_id:' + s, user.auth_ids) )
                    ndb.delete_multi([user.key])
                    total=total+1
        page=page+1
        logging.info("deleted "+str(total)+" records")
        model.messages.append("deleted "+str(total)+" records")
        return DevView(model)
        """
        
        page=0
        total=0
        file_contents=open("fake_users.txt").read()
        file_lines=file_contents.split("\n")
        num_new_users=0
        #userdata=open("a").read()
        salt='1da6452f43f349e4a73e2a8db17ab826';
        now=time.time()
        for line in file_lines:
            userdata=line.split(",")
            if len(userdata) >2:
                t1=now-random.randint(0,(86400*365))
                date_created=datetime.datetime.utcfromtimestamp(t1)
                
                user = User.create_user(userdata[0],email_address=userdata[0]+"@syytacit.com", password_raw=hashlib.md5(userdata[0]+salt).hexdigest(),verified=False,created=date_created)
                num_new_users=num_new_users+1
                #user=user(type="fake",username=userdata[0],first_name=userdata[1],last_name=userdata[2],email=userdata[0]+"@syytacit.com")
                #user.save()
        logging.info("created "+str(num_new_users)+" new users");
        model.messages.append("created "+str(num_new_users)+" new users")
        return DevView(model)
    
    def delete_all_userknowledgeAction(self):
        self.checkEnv()
        page=0
        limit=100
        records=[1]
        total_records=0
        while records:
            records=UserKnowledgeModel.all().fetch(limit,page*limit)
            for record in records:
                record.delete()
                total_records=total_records+1
            page=page+1
            logging.info("page: "+str(page))
       
        model=DevModel()
        message="deleted "+str(total_records)+" records"
        model.messages.append(message)
        logging.info(message)
        
        return DevView(DevModel())
    
    def rename_category_namesAction(self,page=None):
        self.checkEnv()
        onepage=False
        if page:
            onepage=True
            page=int(page)
            
        limit=100
        records=[1]
        total_records=0
        while records:
            records=CategoryModel.all().fetch(limit,(page-1)*limit)
            for record in records:
                record.name=record.name.lower()
                record.save()
                
                total_records=total_records+1
            page=page+1
            logging.info("page: "+str(page))
            if onepage:
                break
       
        model=DevModel()
        message="updated "+str(total_records)+" records"
        model.messages.append(message)
        logging.info(message)
        
        return DevView(DevModel())
    def delete_all_commentsAction(self):
        page=0
        limit=100
        articles=[1]
        while articles:
            articles=ArticleModel.all().fetch(limit,page*limit)
            for article in articles:
                if article.comment!=None:
                    article.comment=None
                    article.save()
            page=page+1
        page=0
        limit=100
        comments=[1]
        while comments:
            logging.info("processing page "+str(page))
            comments=Comments.all().fetch(limit,page*limit)
            
            for comment in comments:
                comment_approvals=[1]
                cpage=0
                while comment_approvals:
                    comment_approvals=CommentApproveModel.all().filter("comment =",comment).fetch(limit,(cpage*limit))
                    cpage=cpage+1
                    for ca in comment_approvals:
                        ca.delete()
                    
                comment.delete()
            page=page+1
            
        return DevView(DevModel())    
    def delete_all_comment_approvalsAction(self):
        page=0
        limit=100
        records=[1]
        num_deleted=0
        model=DevModel()
        while records:
            records=CommentApproveModel.all().fetch(limit,page*limit)
            for record in records:
                record.delete();
                num_deleted=num_deleted+1
            logging.info("deleted "+str(num_deleted)+" records")
            page=page+1
        model.messages=["deleted "+str(num_deleted)+" records"]
        return DevView(model)  
    
    def delete_all_questionsAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=QuestionModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                record.delete()
                total=total+1
        model.messages=["deleted "+str(total)+" records"]
        #self.delete_all_answersAction()
        #self.delete_all_sentencesAction()
        return DevView(model)
        
        
    def reset_questions_catsAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        cats={}
        while records:
            records=QuestionModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                if len(record.cats)==0:
                    if record.sentences:
                        for sentence_key in record.sentences:
                            sentence=SentenceModel.get(sentence_key)
                            if sentence and sentence.wiki:
                                if sentence.wiki.categories:
                                    for wikicat_key in sentence.wiki.categories:
                                        wikicat=WikiCategoryModel.get(wikicat_key)
                                        if wikicat:
                                            category=CategoryLib.getByWikiName(wikicat.name)
                                            if category:
                                                cats[category.name]=category.key()
            if cats:
                record.cats=cats.values()
                #record.save()
                total=total+1
                
        model.messages=["updated "+str(total)+" records"]
        #self.delete_all_answersAction()
        #self.delete_all_sentencesAction()
        return DevView(model)
    
    
    def chown_articleAction(self,from_username,to_username):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=ArticleModel.all().filter("username =",from_username).fetch(limit,page*limit)
            page=page+1
            for record in records:
                record.username=to_username
                record.save()
                total=total+1
        model.messages=["modified "+str(total)+" records"]
        
        return DevView(model)
    
    def article_add_archivedAction(self,page=0,limit=100):
        self.checkEnv()
        
        page=int(page)
        limit=int(limit)        
        model=DevModel()

        total=0
      
        records=ArticleCategoryModel.all().fetch(limit,page*limit)
        for record in records:
            record.archived=False
            record.save()
            total=total+1
        model.messages=["modified "+str(total)+" records"]
        
        return DevView(model)
    
    def delete_all_articlesAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=ArticleModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                record.delete()
                total=total+1
        model.messages=["deleted "+str(total)+" records"]
        
        return DevView(model)
   
    def delete_all_sentencesAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=SentenceModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                record.delete()
                total=total+1
                """
                try:
                    x=record.wiki
                except Exception:
                    record.delete()
                    total=total+1
                """
        model.messages=["deleted "+str(total)+" records"]
        
        return DevView(model)
    
    def fix_all_sentence_whitespaceAction(self):
        import re
        from hashlib import md5
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=SentenceModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                new_sentence=re.sub('\s{2,}', ' ', record.sentence).strip()
                if record.sentence!=new_sentence:
                    record.sentence=new_sentence
                    record.signature=md5(record.sentence).hexdigest()
                    record.save()
                
                    total=total+1
        model.messages=["fixed "+str(total)+" records"]
        
        return DevView(model)
    
    def fix_all_question_whitespaceAction(self):
        import re
        from hashlib import md5
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=QuestionModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                new_question=re.sub('\s{2,}', ' ', record.question).strip()
                if record.question!=new_question:
                    record.question=new_question
                    record.signature=md5(record.question).hexdigest()
                    record.save()
                    total=total+1
               
        model.messages=["fixed "+str(total)+" records"]
        
        return DevView(model)
    
    def fix_all_answer_whitespaceAction(self):
        import re
        from hashlib import md5
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=AnswerModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                new_answer=re.sub('\s{2,}', ' ', record.answer).strip()
                if record.answer!=new_answer:
                    record.answer=new_answer
                    record.signature=md5(record.answer).hexdigest()
                    record.save()
                    total=total+1
               
        model.messages=["fixed "+str(total)+" records"]
        
        return DevView(model)
    
    def set_sentence_typeAction(self,sentence_type=1):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=SentenceModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                record.type=sentence_type
                record.numquestions=None
                record.save()
                total=total+1
         
        return DevView(model)
    
    def getlatestarticlesAction(self):
        self.checkEnv()
        #pubDate=datetime.datetime.strptime('Wed, 17 Jul 2013 08:57:58 GMT', '%a, %d %b %Y %H:%M:%S Z')
        #pubDate=datetime.datetime.strptime('Wed, 17 Jul 2013 08:57:58 GMT', '%a, %d %b %Y %H:%M:%S %Z')
        #logging.info(pubDate)
        #articles=UsaTodayWebService().getLatestArticles()
        UsaTodayLib().save_latest_headlines()
        
        self.attach_user_to_articlesAction()
        
        return DevView(DevModel())
    
    """
    attach a user to any article that doesnt already have a user attached
    """
    def attach_user_to_articlesAction(self):
        self.checkEnv()
        page=0
        limit=100
        articles=[1]
        users=User.query().fetch(200)
        
        while articles:
            articles=ArticleModel.all().filter("user =",None).fetch(limit,page*limit)
            for article in articles:
                user=random.sample(users,1)
                article.username=user[0].auth_ids[0]
                article.save()
                return DevView(DevModel())
            page=page+1
        return DevView(DevModel())
    
    def delete_all_usersAction(self):
        total=0
        page=0
        model=DevModel()
        fusers=User.query().fetch(200)
        for user in fusers:
            if user and user.email_address:
                if '@syytacit.com'==user.email_address[-13:]:
                    Unique.delete_multi( map(lambda s: 'User.auth_id:' + s, user.auth_ids) )
                    ndb.delete_multi([user.key])
                    total=total+1
        page=page+1
        logging.info("deleted "+str(total)+" records")
        model.messages.append("deleted "+str(total)+" records")
        return DevView(model)
    
    def delete_all_article_categoriesAction(self):
        self.checkEnv()
        limit=100
        page=0
        records=[1]
        total=0
        model=DevModel()
        while records:
            records=ArticleCategoryModel.all().fetch(limit,page*limit)
            for record in records:
                record.delete()
                total=total+1
            logging.info("deleted "+str(page*limit)+" records")
            page=page+1
            
        model.messages=["deleted "+str(total)+" records"]
            
        return DevView(model)
    
    
    def delete_all_article_approvalsAction(self):
        self.checkEnv()
        num_deleted=0
        model=DevModel()
        
        records=ArticleApproveModel.all()
        for record in records:
            record.article.numapprovals=0
            record.article.save()
            record.delete()
            num_deleted=num_deleted+1
            
        records=ArticleModel.all()
        for record in records:
            if record.numapprovals>0:
                record.numapprovals=0
                record.save()
    
        message="deleted "+str(num_deleted)+" records"
        logging.info(message)
        model.messages.append(message)
        
        return DevView(model)
    
    """
    creates random sentences and questions and answers
    """
    def create_random_questionsAction(self,amount=1000):
        self.checkEnv()
        model=DevModel()
        i = int(amount)
        amount=i
        
        #TODO: use lorem ipsum for question text: http://loripsum.net/api/10/short/headers/
    
        import string
        
        allcats=CategoryModel.all().fetch(200,0)
        numcats=len(allcats)
        
        for j in range(amount):
            sentence_text=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
            question_text=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
           
            sentence = SentenceModel(score=0,sentence=sentence_text,signature=hashlib.md5(sentence_text).hexdigest())
            sentence.save()
                  
            qsignature=hashlib.md5(question_text).hexdigest()
            question=QuestionModel.all().filter("signature =",qsignature).get()
            if question:
                logging.error("question already exists!")
            else:
                
                maxcats=random.randint(1,10) # tag the question with between 1 and 10 categories
                x=random.sample(allcats, maxcats)
                cats=[]
                for c in x:
                    cats.append(c.key())
                #logging.info(cats)
                #return NullView()
                question=QuestionModel(question=question_text,signature=qsignature,cats=cats)
                question.sentences.append(sentence.key())
                question.question_type=0
                question.num_wrong_answers=0
                
                if sentence.numquestions==None:
                    sentence.numquestions=1
                else:
                    sentence.numquestions=sentence.numquestions+1
                sentence.save()
                
                if not question.correct_answer: # if the question doesnt have an answer specified, then create one
                    question.save()
                    answer_text=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
                    signature=hashlib.md5(answer_text).hexdigest()
                    canswer=AnswerModel(answer=answer_text,iscorrect=True,signature=signature)
                    canswer.save()
                    question.correct_answer=canswer
                    
                else:
                    answer_text=question.correct_answer.answer
                    
                question.save()
        
        return DevView(model)
    
    def create_random_user_answersAction(self,username=None,background=False):
        model=DevModel()
        if background:
            model.messages=["queueing job "+"/json/dev/create_random_user_answers/"+username+"/false"]
            r=taskqueue.add(url="/json/dev/create_random_user_answers/"+username+"/false",retry_options=taskqueue.TaskRetryOptions(task_retry_limit=0))
            model.messages.append(r)
            return DevView(model)
        
        logging.info("running in background")
        # get list of all categories for all articles
        page=0
        limit=100
        articlecategories=[1]
        categories = {}
        while articlecategories:
            articlecategories=ArticleCategoryModel.all().fetch(limit, page*limit);
            for articlecategory in articlecategories:
                if not categories.has_key(articlecategory.category.name):
                    categories[articlecategory.category.name]=articlecategory.category
            page=page+1
        
        
        model.messages=["found "+str(len(categories))+" distinct categories "]
        now=time.time()
        total_records=0
        
        users=User.query().fetch(200)
        for user in users:
            #logging.info("processing user "+user.auth_ids[0])
            # for each category get 10 questions
            for tag,category in categories.items():
                questions=QuestionModel.all().filter("cats in",[category.key()]).fetch(10,0)
                for question in questions:
                    if random.randint(0,1)==1:
                        iscorrect=True
                    else:
                        iscorrect=False
                        
                    t1=now-random.randint(0,(86400*365))
                    updated=datetime.datetime.utcfromtimestamp(t1)
                    topa=datetime.datetime.utcfromtimestamp(t1-random.randint(0,86400*30))
                    delay=random.randint(1,360000)
                    useranswer=UserAnswerModel(question=question,iscorrect=iscorrect,username=user.auth_ids[0],updated=updated,topa=topa,delay=delay)
                    useranswer.save()
                    
                    total_records=total_records+1
    
        message="created "+str(total_records)+" answers"
        model.messages.append(message)
        logging.info(message)
        return DevView(model)
    
    def calculate_user_knowledgeAction(self,username=None,background=False):
        self.requireLoggedin("admin")
        model=DevModel()
        if background:
            r=taskqueue.add(url="/json/dev/calculate_user_knowledge"+username+"/false",task_retry_options=taskqueue.TaskRetryOptions(task_retry_limit=0))
            model.messages=[r]
            
        if username:
            user=User.get_by_auth_id(username)
        else:
            user=SparseUser()
        
        KnowledgeLib.calculate_user_knowledge(user)
        return DevView(model)
    
    
    
    def delete_orphaned_userknowledgeAction(self,page=1):
        page=int(page)
        
        model={"num_deleted":0,"total":0}
        deleted_records=[]
        records=UserKnowledgeModel.all()
        db_cursor = memcache.get('delete_orphaned_userknowledge_cursor')
        if db_cursor:
            records.with_cursor(start_cursor=db_cursor)
        
        for record in records:
            if model['total']>99:
                break
            model['total']=model['total']+1
            
            user=User.get_by_auth_id(record.username)
            if not user:
                deleted_records.append(record)
                model["num_deleted"]=model["num_deleted"]+1
                
        
        if model['total']==0:
            memcache.delete('delete_orphaned_userknowledge_cursor')
        else:
            # Get updated cursor and store it for next time
            db_cursor = records.cursor()
            memcache.set('delete_orphaned_userknowledge_cursor', db_cursor) 
        
        if deleted_records:
            db.delete(deleted_records)
            
        return model
    
    def delete_orphaned_articlecategoriesAction(self,page=1):
        page=int(page)
        
        model={"num_deleted":0,"total":0}
        deleted_records=[]
        records=ArticleCategoryModel.all()
        db_cursor = memcache.get('del_or_art_cat_cur')
        if db_cursor:
            records.with_cursor(start_cursor=db_cursor)
        
        for record in records:
            if model['total']>99:
                break
            model['total']=model['total']+1
            
            try:
                title=record.article.title
            except ReferencePropertyResolveError:
                deleted_records.append(record)
                model["num_deleted"]=model["num_deleted"]+1
                
        
        if model['total']==0:
            memcache.delete('del_or_art_cat_cur')
        else:
            # Get updated cursor and store it for next time
            db_cursor = records.cursor()
            memcache.set('del_or_art_cat_cur', db_cursor) 
        
        if deleted_records:
            db.delete(deleted_records)
            
        return model
    
    
    def delete_orphaned_useranswersAction(self,page=1):
        page=int(page)
        
        model={"num_deleted":0,"total":0}
        deleted_records=[]
        records=UserAnswerModel.all()
        db_cursor = memcache.get('delete_orphaned_useranswers_cursor')
        if db_cursor:
            records.with_cursor(start_cursor=db_cursor)
        
        for record in records:
            if model['total']>99:
                break
            model['total']=model['total']+1
            
            user=User.get_by_auth_id(record.username)
            
            if not user:
                deleted_records.append(record)
                model["num_deleted"]=model["num_deleted"]+1
                
        
        if model['total']==0:
            memcache.delete('delete_orphaned_useranswers_cursor')
        else:
            # Get updated cursor and store it for next time
            db_cursor = records.cursor()
            memcache.set('delete_orphaned_useranswers_cursor', db_cursor) 
        
        if deleted_records:
            db.delete(deleted_records)
            
        return model
    
    def recount_all_article_commentsAction(self):
        model={"messages":[]}
        page=0
        limit=100
        articles=[1]
        num_articles=0
        while articles:
            articles=ArticleModel.all().fetch(limit,page*limit)
            for article in articles:
                numcomments=0
                #logging.info("scanning article "+article.title) 
                if article.comment:
                    numcomments=CommentsLib.countComments(article.comment.key())
                    #if article.numcomments > 0:
                    #    logging.info("quitting because numcomments="+str(article.numcomments))
                        #return DevView(DevModel())
                if article.numcomments!=numcomments:
                    article.numcomments=numcomments
                    article.save()
                    num_articles=num_articles+1
            
            page=page+1
        model['messages']=["processed "+str(num_articles)+" articles"]
        logging.info(model['messages'][0])
                    
        return DevView(model)
    
    def recount_all_article_approvalsAction(self):
        model={"messages":[]}
        page=0
        limit=100
        articles=[1]
        num_articles=0
        while articles:
            articles=ArticleModel.all().fetch(limit,page*limit)
            for article in articles:
                numapprovals=0
                q=db.Query(ArticleApproveModel, projection=['username'],distinct=True).filter("article =",article)
                
                numapprovals=q.count()
                
                if article.numapprovals!=numapprovals:
                    article.numapprovals=numapprovals
                    article.save()
                    num_articles=num_articles+1
                    
            page=page+1
        model['messages']=["processed "+str(num_articles)+" articles"]
        logging.info(model['messages'][0])
                    
        return DevView(model)
    
    def set_question_catsAction(self):
        model={"messages":[]}
        page=0
        limit=100
        num_records=0
        questions=[1]
        while questions:
            questions=QuestionModel.all().fetch(limit,(page*limit))
            logging.info("processing page "+str(page))
            page=page+1
            for question in questions:
                logging.info("processing question "+str(question.key().id()))
                question.cats=[]
                num_records=num_records+1
                if question.sentences:
                    for sentence_key in question.sentences:
                        sentence=SentenceModel.get(sentence_key)
                        if sentence:
                            if sentence.wiki:
                                wikicat_keys=sentence.wiki.categories
                                if not wikicat_keys:
                                    logging.warn("sentence "+str(sentence_key)+" has no categories")
                                for wikicat_key in wikicat_keys:
                                    wikicat=WikiCategoryModel.get(wikicat_key)
                                    if wikicat:
                                        cat=CategoryLib.getByWikiName(wikicat.name)
                                        if cat:
                                            logging.info("appending category "+cat.name)
                                            question.cats.append(cat.key())
                                        else:
                                            logging.warn("cant find category having wikiname "+wikicat.name)
                                    else:
                                        logging.warn("cant find wikicat having key "+str(wikicat_key))
                            else:
                                logging.warn("sentence "+str(sentence_key)+" has no wiki attached")
                        else:
                            logging.warn("cant find sentence having key "+str(sentence_key))
                else:
                    logging.warn("no sentences found for question "+str(question.key()))
                question.save()
                
               
                
        model['messages']=["processed "+str(num_records)+" records"]
        logging.info(model['messages'][0])
                    
        return DevView(model)
    
    def find_missing_wiki_categoriesAction(self,page=0,deletethem=False):
        i=int(page)
        page=i
        limit=100
        records=[1]
        num_questions=0
        num_sentences=0
        while records:
            records=SentenceModel.all().fetch(limit,page*limit)
            page=page+1
            for sentence in records:
                if sentence.wiki:
                    wikicat_keys=sentence.wiki.categories
                    if not wikicat_keys:
                        logging.warn("sentence "+str(sentence.key())+" has no categories")
                    for wikicat_key in wikicat_keys:
                        wikicat=WikiCategoryModel.get(wikicat_key)
                        if wikicat:
                            cat=CategoryLib.getByWikiName(wikicat.name)
                            if not cat:
                                #logging.warn("cant find category having wikiname "+wikicat.name)
                      
                                #logging.warn("cant find wikicat having key "+str(wikicat_key))
                                #delete this sentence. delete all questions attached to this sentence
                                questions=[1]
                                p2=0
                                while questions:
                                    questions=QuestionModel.all().filter("sentences in ",[sentence.key()]).fetch(limit,p2*limit)
                                    p2=p2+1
                                    for question in questions:
                                        num_questions=num_questions=+1
                                        if deletethem!=False:
                                            question.delete()
                                num_sentences=num_sentences+1
                                if deletethem!=False:
                                    sentence.delete()
                else:
                    logging.warn("sentence "+str(sentence.key())+" has no wiki attached")
            records=[]   
        logging.info("deleted "+str(num_sentences)+" sentences")
        logging.info("deleted "+str(num_questions)+" question")
        
        model={}
        return DevView(model)
        
    def set_archive_propertyAction(self):
        self.checkEnv()
        model=DevModel()
        page=0
        limit=100
        total=0
        records=[1]
        while records:
            records=ArticleModel.all().fetch(limit,page*limit)
            page=page+1
            for record in records:
                record.archived=False
                record.save()
                total=total+1
        model.messages=["processed "+str(total)+" records"]
        
        return DevView(model)
    
    
    def article_update_numapprovalsAction(self,page=0,limit=100):
        self.checkEnv()
        model=DevModel()
        total=0
        
        page=int(page)
        
        records=ArticleModel.all().fetch(limit,page*limit)
       
        for record in records:
            if record.numapprovals==None:
                record.numapprovals=0
                record.save()
                total=total+1
            
        model.messages=["processed "+str(total)+" records"]
        
        return DevView(model)
