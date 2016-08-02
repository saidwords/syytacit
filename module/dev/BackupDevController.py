# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
import datetime

import logging
import os
#from module.natlang.model.SentenceModel import SentenceModel
import hashlib
#from common.models.QuestionModel import QuestionModel
#from common.models.CategoryModel import CategoryModel
#from common.models.AnswerModel import AnswerModel
#from common.models.UserAnswerModel import UserAnswerModel
from common.lib.KnowledgeLib import KnowledgeLib
from module.article.lib.ArticleLib import ArticleLib
from module.article.model.ArticleModel import ArticleModel
#from common.models.UserKnowledgeModel import UserKnowledgeModel
from module.article.model.ArticleCategoryModel import ArticleCategoryModel
from module.usatoday.lib.UsaTodayLib import UsaTodayLib
import random
from module.dev.view.DevView import DevView
from module.dev.model.DevModel import DevModel
from module.article.model.ArticleApproveModel import ArticleApproveModel
from module.comments.model.Comments import Comments
from common.lib.Users import Users
from module.comments.lib.CommentsLib import CommentsLib
from module.comments.model.CommentApproveModel import CommentApproveModel
from common.lib.CategoryLib import CategoryLib
import time
from module.question.lib.QuestionLib import QuestionLib
from webapp2_extras.appengine.auth.models import User, Unique
from google.appengine.ext import ndb
from common.models.CategoryModel import CategoryModel
#from google.appengine.api.users import User


class DevController(Controller):
    def checkEnv(self):
        if os.environ['SERVER_SOFTWARE'].find('Development') != 0:
            raise Exception("dev functions only available in Dev environment")
        
    def defaultAction(self,segments,qs):
        return self.indexAction()
    
    def delete_all_questionsAction(self):
        page=0
        limit=100
        questions=[1]
        num_deleted=0
        while len(questions) > 0:
            questions=QuestionModel.all().fetch(limit,page*limit)
            for question in questions:
                if len(question.wrong_answers)==0:
                    question.delete()
                    num_deleted=num_deleted+1
            logging.info("deleted "+str(num_deleted)+" records")
            page=page+1
        return DevView(DevModel())
    
    def delete_all_comment_approvalsAction(self):
        page=0
        limit=100
        records=[1]
        num_deleted=0
        while records:
            records=CommentApproveModel.all().fetch(limit,page*limit)
            for record in records:
                record.delete();
                num_deleted=num_deleted+1
            logging.info("deleted "+str(num_deleted)+" records")
            page=page+1
        return DevView(DevModel())
    
    
    
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
    
    def indexAction(self):
        
        self.checkEnv()
            
        return DevView(DevModel)
        """
        model=AdminModel()
        if not self.authenticate("admin"):
            return HomeController().indexAction()
            
        model.todaydate=datetime.datetime.now()
        return AdminView(model)
        """

    """
    creates random sentences and questions
    """
    def create_random_questionsAction(self,amount=1000):
        self.checkEnv()
        
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
                question.save()
                if sentence.numquestions==None:
                    sentence.numquestions=1
                else:
                    sentence.numquestions=sentence.numquestions+1
                sentence.save()
        
        return DevView(DevModel())
    
    def create_random_answersAction(self,amount=10):
        self.checkEnv()
        
        i = int(amount)
        amount=i
    
        import string
        
        page=0
        limit=100
        questions=[1]
        while questions:
            questions=QuestionModel.all().fetch(limit,page*limit)
            for question in questions:
                if not question.correct_answer: # if the question doesnt have an answer specified, then create one
                    answer_text=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
                    signature=hashlib.md5(answer_text).hexdigest()
                    canswer=AnswerModel(answer=answer_text,iscorrect=True,signature=signature)
                    canswer.save()
                    question.correct_answer=canswer
                else:
                    answer_text=question.correct_answer.answer
                    
                question.question=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))+':'+answer_text
                
                """
                for j in range(3):
                    answer_text=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
                    signature=hashlib.md5(answer_text).hexdigest()
                    answer=AnswerModel(answer=answer_text,iscorrect=False,signature=signature)
                    answer.save()
                    question.wrong_answers.append(answer.key())
                    
                """
                question.num_wrong_answers=0
                question.save()
            page=page+1
        
        
        allcats=CategoryModel.all().fetch(100,0)
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
                # how many categories to attach?
                maxcats=random.randint(1,numcats)
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
                question.save()
                if sentence.numquestions==None:
                    sentence.numquestions=1
                else:
                    sentence.numquestions=sentence.numquestions+1
                sentence.save()
        
        return DevView(DevModel())
    
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
                #user=user(type="fake",nickname=userdata[0],first_name=userdata[1],last_name=userdata[2],email=userdata[0]+"@syytacit.com")
                #user.save()
        logging.info("created "+str(num_new_users)+" new users");
        model.messages.append("created "+str(num_new_users)+" new users")
        return DevView(model)
        
       
    def recount_all_article_commentsAction(self):
        page=0
        limit=100
        articles=[1]
        while articles:
            articles=ArticleModel.all().fetch(limit,page*limit)
            for article in articles:
                numcomments=0
                #logging.info("scanning article "+article.title) 
                if article.comment:
                    numcomments=CommentsLib.countComments(article.comment.key())
                    logging.info("numcomments for article "+article.title+"="+str(numcomments))
                    #if article.numcomments > 0:
                    #    logging.info("quitting because numcomments="+str(article.numcomments))
                        #return DevView(DevModel())
                if article.numcomments!=numcomments:
                    article.numcomments=numcomments
                    article.save()
            
            page=page+1
                    
        return DevView(DevModel())
    
    def create_random_user_answersAction(self,nickname=None):
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
            logging.info("page: "+str(page))
            page=page+1
        
        model=DevModel()
        model.messages=["found "+str(len(categories))+" distinct categories "]
        now=time.time()
        total_records=0
        
        users=[1]
        upage=0
        while users:
            
            users=User.all().fetch(100,upage*limit)
            upage=upage+1
            for user in users:
                logging.info("processing user "+user.nickname)
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
                        useranswer=UserAnswerModel(question=question,iscorrect=iscorrect,user=user,updated=updated,topa=topa,delay=delay)
                        useranswer.save()
                        
                        total_records=total_records+1
        
        message="created "+str(total_records)+" answers"
        model.messages.append(message)
        logging.info(message)
        return DevView(model)
        
        
    def calculate_user_knowledgeAction(self,nickname=None):
        self.checkEnv()
        if nickname:
            user=User.all().filter("nickname =",nickname).get()
        else:
            user=None
        KnowledgeLib.calculate_user_knowledge(user)
        return DevView(DevModel())
    
    def reset_user_knowledgeAction(self):
        self.checkEnv()
        limit=100
        page=0
        records=[1]
        while records:
            records=UserKnowledgeModel.all().fetch(limit,page*limit)
            for record in records:
                record.score=0.0;
                record.pct=0.0
                record.save()
            logging.info("reset "+str(page*limit)+" records")
            page=page+1
            
        return DevView(DevModel())
    
    def map_categories_to_wikiAction(self):
        self.checkEnv()
        # get any categories that do not have an associated wiki category
        ArticleLib.map_categories_to_wiki()

    def submit_fake_articlesAction(self):
        self.checkEnv()
        import string
        from datetime import timedelta
        
        
        #delete all article categories
        limit=500
        page=0
        records=[1]
        while records:
            records=ArticleCategoryModel.all().fetch(limit,page*limit)
            for record in records:
                record.delete()
            page=page+1
            
        # delete all articles
        page=0
        articles=[1]
        while articles:
            articles=ArticleModel.all().fetch(limit,page*limit)
            for article in articles:
                article.delete()
            page=page+1
        # get list of all possible categories
        catmodels=CategoryModel.all().fetch(100,0)
        numcats=len(catmodels)
        cats=[]
        for cat in catmodels:
            cats.append(cat.key())
        
        #have each user create a fake article
        today=datetime.datetime.today()
        limit=10
        users=[1]
        while users:
            users=User.all().fetch(limit,page*limit)
            logging.info("processing "+str(page*limit)+ " records")
            page=page+1
            for user in users:
                article=ArticleModel(title=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32)),ihref=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32)))
                article.subtitle=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
                article.description=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(64))
                article.href='http://'+''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
                article.user=user
                days=timedelta(days=random.randint(1,30))
                article.updated=today-days # a random date between now and 1 month ago
                article.save()
                
                randcats=random.sample(catmodels,random.randint(1,4))
                for randcat in randcats:
                    #article_cat=ArticleCategoryModel(article=article,category=randcat)
                    #article_cat=ArticleCategoryModel(article=article)
                    article_cat=ArticleCategoryModel(article=article,category=randcat)
                    article_cat.catscore=(0.0+random.randint(1,100) ) / 100.0
                     
                    userknowledges=UserKnowledgeModel.all().filter("user =",user).filter("category =",randcat).fetch(100,0)
                    if len(userknowledges) == 1:
                        article_cat.usercategoryscore=userknowledges[0].score
                        article_cat.updated=article_cat.article.updated
                        article_cat.sortkey=(article_cat.catscore*100)+(userknowledges[0].score/100) #TODO: tweak this
                        article_cat.save()
                
        return DevView(DevModel())
    
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
    def delete_all_articlesAction(self):
        self.checkEnv()
        page=0
        limit=100
        articles=[1]
        while articles:
            articles=ArticleModel.all().fetch(limit,page*limit)
            for article in articles:
                article.delete()
            logging.info("deleted "+str(page*limit)+" records")
            page=page+1
        
        return DevView(DevModel())
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
    
    def delete_all_sentencesAction(self):
        self.checkEnv()
        page=0
        limit=100
        records=[1]
        while records:
            records=SentenceModel.all().fetch(limit,page*limit)
            for record in records:
                record.delete()
            logging.info("deleted "+str(page*limit)+" records")
            page=page+1
            
        return DevView(DevModel())
       
    def delete_all_usersAction(self):
        self.checkEnv()
        page=0
        limit=100
        records=[1]
        while records:
            records=User.all().fetch(limit,page*limit)
            for record in records:
                record.delete()
            logging.info("deleted "+str(page*limit)+" records")
            page=page+1
        
        return DevView(DevModel())
    
    
    def delete_questionsAction(self):
        self.checkEnv()
        # delete all questions having more than 10 categories attached
        page=0
        limit = 100
        questions=[1]
        while questions:
            questions=QuestionModel.all().fetch(limit,page*limit)
            for question in questions:
                if len(question.cats) > 10:
                    question.delete()
            
            page=page+1
        return DevView(DevModel())
    
   
    
    def apply_approvals_to_articlesAction(self):
        model=DevModel()
        
        ArticleLib.setArticleSortKey()
        
        return DevView(model)
    
    """
    for each article that a user has submitted, apply the users current category knowledge to article
    """
    def apply_user_knowledgeAction(self):
        self.checkEnv()
        page=0
        limit=100
        
        articles=[1]
        while articles:
            articles=ArticleModel.all().fetch(limit,page*limit)
            
            for article in articles:
                article_cats=ArticleCategoryModel.all().fetch(100)
                i=0
                for article_cat in article_cats:
                    userknowledges=UserKnowledgeModel.all().filter("user =",article.user).filter("category =",article_cat.category).fetch(100)
                    #article_cat.usercategoryscore=0.1
                    if userknowledges:
                        logging.info("user knows "+article_cat.category.name)
                        userknowledge=userknowledges[0]
                        article_cat.usercategoryscore=userknowledge.score
                        logging.info("score="+str(article_cat.usercategoryscore))
                        article_cat.sortkey=(article_cat.catscore*100)+(userknowledge.score/100) #TODO: tweak this
                        i=i+1
                    article_cat.save()
                if i==0:
                    logging.info("user has no knowledge in any categories for article "+str(article.key()))
            page=page+1
        
            
        return DevView(DevModel())
    
    def create_random_article_approvalsAction(self):
        self.checkEnv()
        all_articles=ArticleModel.all().fetch(100)
        
        page=0
        limit=100
        users=[1]
        while users:
            logging.info("processing page "+str(page))
            users=User.all().fetch(limit,page*limit)
            for user in users:
                logging.info("processing user: "+user.nickname)
                articles=random.sample(all_articles,3)
                
                for article in articles:
                    if article.user != user:
                        article_cats=ArticleCategoryModel.all().filter("article =",article).fetch(100)
                        approval_count=0
                        for article_cat in article_cats:
                            userknowledges=UserKnowledgeModel.all().filter("user =",user).filter("category =",article_cat.category).fetch(1)
                            article_approval=ArticleApproveModel.all().filter("user =",user).filter("category =",article_cat.category).get()
                            if not article_approval:
                                article_approval=ArticleApproveModel(user=user,article=article,category=article_cat.category,score=0.01)
                            if userknowledges:
                                article_approval.score=userknowledges[0].score
                            article_approval.save()
                            approval_count=1
                        if article_approval > 0:
                            article.numapprovals=article.numapprovals+1
                            article.save();
            page=page+1
        
                
        return DevView(DevModel())
    
    
        
    def calculate_article_cat_sortkeyAction(self):
        self.checkEnv()
        page=0
        limit=100
        records=[1]
        num_records=0
        approvals=0
        while records:
            logging.info("processing page "+str(page))
            records=ArticleCategoryModel.all().fetch(limit,page*limit)
            for record in records:
                sortkey=record.catscore*100;
                apage=0
                article_approvals=[1]
                while article_approvals:
                    article_approvals=ArticleApproveModel.all().ancestor(record.article).filter("category =",record.category).fetch(limit,apage*limit)
                    apage=apage+1
                    for article_approval in article_approvals:
                        sortkey=sortkey+(article_approval.score/100)
                        approvals=approvals+1
                    record.sortkey=sortkey
                    record.save()
                    num_records=num_records+1
            page=page+1
        logging.info("found "+str(approvals)+" approvals")
        return DevView(DevModel())
    
    def calculate_article_sortkeyAction(self):
        ArticleLib.setArticleSortKey()
        return DevView(DevModel())
    
    def test_1Action(self):
        
        if not self.user:
            logging.info("you must be logged in");
            return DevView(DevModel())
        
        article_id=5169010320605184
        a=ArticleModel.get_by_id(int(article_id))
        articlecats=ArticleLib.getCategories(a);
        
        rank=0
        userknowledge=Users.getUserKnowledge(self.user)
        for cat in articlecats:
            if userknowledge.has_key(cat.name):
                rank=int(rank+(articlecats[cat].catscore*userknowledge[cat.name].score))
                if rank > 4223372036854775807:
                    rank=4223372036854775807
                    logging.ERROR("rank exceeds maxint")
                    
        logging.info("final rank = "+"{0:d};".format(rank))
        
        return DevView(DevModel())
    
    """
    Delete any questions that dont have answers
    """
    def cleanup_questionsAction(self):
        self.checkEnv()
        page=0
        limit=100
        questions=[1]
        t=0
        while questions:
            logging.info("processing page "+str(page))
            questions=QuestionModel.all().fetch(limit,page*limit)
            for question in questions:
                if not question.correct_answer or not question.wrong_answers:
                    question.delete()
                else:
                    if question.correct_answer.answer[0] !='C':
                        question.correct_answer.answer="C"+question.correct_answer.answer;
                        question.correct_answer.save();
                    t=t+1
            page=page+1
        logging.info("deleted "+str(t)+" questions")
                    
        return DevView(DevModel())
    
    def create_random_article_commentsAction(self):
        import string
        
        page=0
        limit=100
        articles=[1]
        while articles:
            #articles=ArticleModel.all().fetch(limit,page*limit)
            articles=ArticleModel.all().filter("ihref =",'google-earnings-clipped-mobile-headwinds').fetch(limit,page*limit)
            for article in articles:
                logging.info("generating comments for article "+article.title)
                existing_comments=[] # this is a lifo stack of the most recent 100 comments on the article
                
                # every user will comment between 1 or 10 times on either the article or another users comment
                upage=0
                users=[1]
                while users:
                    users=User.all().fetch(limit,upage*limit)
                    for user in users:
                        if not article.comment:
                            
                            comment_text=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
                            #comment=Comments(parent_comment=None,text=comment_text,user=user,rank=0.0)
                            #comment.save()
                            comment=CommentsLib.saveComment(article.key().id(),comment_text,user=user)
                            article.comment=comment
                            article.save()
                            existing_comments.append(article.comment)
                            logging.info("creating parent comment "+str(comment))
                            
                        numcomments=random.randint(1,10)
                        for c in range(1,numcomments):
                            # pick between commenting on the article and commenting on another users comment
                            target=random.randint(0,1)
                            if target==1:
                                parent=article.comment
                            else:
                                parent=random.choice(existing_comments)
                                
                                #logging.info("parent=");
                                #logging.info(parent);
                                
                            comment_text=''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
                            comment=CommentsLib.saveComment(article.key().id(),comment_text,parent_id=parent.key().id(),user=user)
                            #comment=Comments(parent_comment=parent,text=comment_text,user=user,rank=0.0)
                            #comment.save()
                            
                            existing_comments.append(comment);
                            if len(existing_comments) > 100:
                                # pop the oldest comment off the stack
                                existing_comments.pop(0)
                    logging.info("processing user page "+str(upage))
                    upage=upage+1
                return None
            logging.info("processing page "+str(page))
            page=page+1
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
            comments=Comments.all().fetch(limit,page*limit)
            logging.info("processing page "+str(page))
            for comment in comments:
                comment.delete()
            page=page+1
            
        return DevView(DevModel())

    def delete_orphaned_article_approvalsAction(self):
        page=0
        limit=100
        records=[0]
        num_deleted=0
        total_records=0
        
        while records:
            records=ArticleApproveModel.all().fetch(limit,page*limit)
            for record in records:
                total_records=total_records+1
                if not record.parent():
                    record.delete()
                    num_deleted=num_deleted+1
                    
                else:
                    category=CategoryModel.get(record.category.key())
                    if not category:
                        record.delete()
                        num_deleted=num_deleted+1
                    else:
                        user=User.get(record.user.key())
                        if not user:
                            record.delete()
                            num_deleted=num_deleted+1
                
            page=page+1
        return DevView(DevModel())
    
   
        
   
    
    def attach_random_user_to_articlesAction(self):
        model=DevModel()
        page=0
        upage=0
        limit=100
        records=[0]
        total_records=0
        while records:
            records=ArticleModel.all().fetch(limit,page*limit)
            users=User.all().fetch(limit,upage*limit)
            if len(users)< len(records) and upage>0:
                upage=0
            else:
                upage=upage+1
            page=page+1
            i=0;
            for record in records:
                record.user=users[i].nickname
                record.save()
                total_records=total_records+1
                i=i+1
                
        
        return DevView(model)
            
    
    def get_random_questionAction(self,tag=None):
        
        model=DevModel();
        model.question=QuestionLib.getRandomQuestion([tag])
            
        return DevView(model)
    
    
    def get_article_approversAction(self,ihref):
        model=DevModel();
        
        model.approvers=[]
        article=ArticleModel.all().filter("ihref =",ihref).get()
        
        if article:
            approvals=ArticleApproveModel.all().filter("article =",article).fetch(10,0)
            for approval in approvals:
                model.approvers.append(approval.user.nickname)
            
        
        return DevView(model)
    
    def increase_user_knowledge(self,nickname,tag=None):
        model=DevModel();
        youse=UserKnowledgeModel.all().fetch(100,0)
        
        return DevView(model)