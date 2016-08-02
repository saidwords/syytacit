# coding=UTF-8
# -*- coding: UTF-8 -*-
import datetime
import hashlib
import logging

from common.lib.CategoryLib import CategoryLib
from common.lib.Controller import Controller
from common.lib.KnowledgeLib import KnowledgeLib
from common.lib.Session import Session
from common.models.AnswerModel import AnswerModel
from common.models.CategoryModel import CategoryModel
from common.models.QuestionModel import QuestionModel
from common.models.UserAnswerModel import UserAnswerModel
from module.article.lib.ArticleLib import ArticleLib
from module.article.model.GetQuestionViewModel import GetQuestionViewModel
from module.article.model.SparseQuestion import SparseQuestion
from module.home.view.NullView import NullView
from module.natlang.model.SentenceModel import SentenceModel
from module.question.lib.QuestionLib import QuestionLib
from module.question.model.QuestionViewModel import QuestionViewModel
from module.question.view.QuestionBrowseView import QuestionBrowseView
from module.question.view.QuestionCreatorView import QuestionCreatorView
from module.question.view.QuestionView import QuestionView
from module.wiki.lib.WikiLib import WikiLib
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
from module.wiki.model.WikiModel import WikiModel
from common.lib.NatLangLib import NatLangLib
from module.question.view.FibQuestionCreatorView import FibQuestionCreatorView
from google.appengine.api import memcache, taskqueue
from module.article.model.ArticleModel import ArticleModel
from common.lib.AlreadyExistsException import AlreadyExistsException


class QuestionController(Controller):
    def defaultAction(self,segments,qs):
        return self.indexAction()
    
    def indexAction(self,page=1,limit=20):
        self.requireLoggedin('admin')
        
        try:
            page_int=int(page)
            
            if page_int < 1: page_int=1
            
            limit_int=int(limit)
        except ValueError,TypeError:
            raise Exception('invalid datatype for parameters')
        
        model = QuestionViewModel()
        
        offset=(page-1)*limit_int
        logging.info("limit:"+str(limit_int)+" offset:"+str(offset))
        model.questions=QuestionModel.all().fetch(limit_int, offset)
        
        for question in model.questions:
            question.wikicats=[]
            question.wranswers=[]
            if question.cats:
                for key in question.cats:
                    cat = WikiCategoryModel.get(key)
                    question.wikicats.append(cat)
            if question.wrong_answers:
                for key in question.wrong_answers:
                    answer=AnswerModel.get(key)
                    question.wranswers.append(answer)
        
        return QuestionView(model)
    
    def fibcreateAction(self,question_text,answer_text=None,tags=None,sentence_key=None):
        self.requireLoggedin('admin')
        model={"key":None}
        
        question=QuestionLib.createFibQuestion(question_text,answer_text,tags,sentence_key,self.user.username)
        
        model['key']=str(question.key())
        
        return model
    
    def createAction(self,question_text,answer_text=None,tags=None,sentence_key=None,question_type='fib'):
        self.requireLoggedin('qc')
        model={"key":None}
        
        if question_type=='fib':
            question_type=1
        elif question_type=='tf':
            question_type=2
        else:
            raise Exception('invalid question type')
        try:
            question=QuestionLib.createQuestion(question_text,answer_text,None,tags,sentence_key,self.user.username,question_type)
        except AlreadyExistsException:
            #update the question
            question=QuestionLib.updateQuestion(question_text,answer_text,None,tags,sentence_key,self.user.username,question_type)
            
        model['key']=str(question.key())
        
        return model
    
    def add_categoryAction(self,key,tag):
        
        self.requireLoggedin('admin')
        model={}
        
        question=QuestionModel.get(key)
        
        if not question:
            raise Exception("Question not found")
        
        cat=CategoryLib.getByTag(tag)
        if not cat:
            raise Exception("invalid tag")
        
        if cat.key() not in question.cats:
            question.cats.append(cat.key())
            question.save()
        
        return model
    
    def get_next_questionAction(self,question_id=None,tags=None):
        self.requireLoggedin()
        
        try:
            if question_id:
                qid=int(question_id)
            else:
                qid=None
        except ValueError,TypeError:
            raise Exception('invalid id')
        
        model=dict({"id":None,"question":None,"question_type":None})
        if tags:
            question=QuestionModel.get_by_id(qid)
            if not question:
                raise Exception("Invalid question id")
            cat_keys=QuestionLib.getCategories(question,True)
        else:
            cat_keys=None
        
        question=QuestionLib.getNextQuestion(qid, cat_keys)
            
        model['id']=str(question.key().id())
        model['question']=QuestionLib.toArray(question.question)
        if self.user:
            model['signature']=QuestionLib.getSignature(model['id'], Session.sessionid)
        else:
            model['signature']=None
            
        model['question_type']=question.question_type
            
        return model
    
    def get_related_questionAction(self,question_id):
        try:
            qid=int(question_id)
        except ValueError,TypeError:
            raise Exception('invalid id')
        
        model=dict({"id":None,"question":None})
        
        question=QuestionModel.get_by_id(qid)
        if question:
            #TODO: if the user is logged in then get a question that they have not answered yet or get the question least asked
            related_question=QuestionModel.all().filter("cats in",question.cats).get()
            if related_question:
                model['id']=str(question.key().id())
                model['question']=question.question
                if self.user:
                    model['signature']=QuestionLib.getSignature(model['id'], Session.sessionid)
                else:
                    model['signature']=None
        
        return NullView(model)
       
    
    """
    gets a question for the given tags
    """
    def get_questionAction(self,tags):
        model=GetQuestionViewModel()
        model.answers=[]
        the_cradle=[]
        
        for tag in tags:
            cat=WikiCategoryModel.all().filter("name =",tag).get()
            
            if not cat:
                cat=CategoryModel.all().filter("name =",tag).get()
                if cat:
                    tag=cat.wikiname
                    cat=WikiCategoryModel.all().filter("name =",tag).get()
            if cat:    
                the_cradle.append(cat.key())
        
        # get questions having the given tags
        #TODO: question should be one that the user does not already know or knows the least.
        question=QuestionModel.all().filter("cats in",the_cradle).get()
        if not question:
            question=QuestionLib.getRandomQuestion()
                
        if question:
            model.question=SparseQuestion()
            model.question.id=question.key().id()
            model.question.question=question.question
            model.question.question_type=question.question_type
            
            #get answers for the question
            #answers=AnswerModel.all().filter("question =",question.key()).fetch(21)
            #for answer in answers:
            #    foo=SparseAnswer()
            #    foo.id=answer.key().id()
            #    foo.answer=answer.answer
            #    model.answers.append(foo)
                
        return NullView(model)
    
    def get_random_questionAction(self,question_id=None,tags=None):
        try:
            if question_id:
                qid=int(question_id)
            else:
                qid=None
        except ValueError,TypeError:
            raise Exception('invalid id')
        
        model=dict({"id":None,"question":None,"signature":None})
        
        #TODO: generate a random non duplicating order of questions for each session
        question=QuestionLib.getRandomQuestion(tags)
        if question:
            model['id']=str(question.key().id())
            #TODO: if the question is a fill in the blank question then replace all underscores with an input text field
            model['question']=question.question
            #model['question']=["what is a ",None] #TODO: the ui template should loop through these pieces and where a piece is None then an input=text field should be rendered
            if self.user:
                model['signature']=QuestionLib.getSignature(model['id'], Session.sessionid)
        return model
    
    def browseAction(self,category=None,page=None,status=None):
        model={"questions":[],"category":None,"sentences":[],"status":""}
        if status:
            model['status']=status
            
        if not self.isLoggedInAs('admin'):
            model['exception']=Exception('You must be an admin to access this page')
            return QuestionBrowseView(model)
        
        
        limit=10
        if page:
            try:
                page=int(page)
                if page<1:
                    page=1
            except TypeError:
                page=1
        else:
            page=1
            
        if category:
            model['category']=CategoryLib.getByTag(category)
        
        
        if model['category']:
            query=QuestionModel.all().filter("cats in",[model['category'].key()])
        else:
            query=QuestionModel.all()
            
        if status:
            try:
                status=int(status)
                query=query.filter("status =",status)
                
        
            except ValueError:
                logging.error("invalid value for parameter status: "+str(status))
                
            
        model['questions']=query.fetch(limit, (page-1)*limit)
        for question in model['questions']:
            sentences=[]
            for sentence_key in question.sentences:
                sentence=SentenceModel.get(sentence_key)
                if sentence:
                    sentences.append(sentence)
            question.foosentences=sentences
            
            question.categories=[]
            for cat in question.cats:
                category=CategoryModel.get(cat)
                if category:
                    question.categories.append(category)
                else:
                    logging.error("question "+str(question.key())+" refers to nonexistent category")
        model['prevpage']=page-1
        model['nextpage']=page+1
        model['user']=self.user
       
        return QuestionBrowseView(model)
    
    def fibcreatorAction(self,category=None,page=1,wikititle=None):
        model={"category":None,"sentences":[],'user':self.user,"wikis":None,'wikititle':wikititle}
        if not self.isLoggedInAs('admin'):
            model['exception']=Exception('You must be an admin to access this page')
            return QuestionCreatorView(model)
        
        limit=10
       
        try:
            page=int(page)
            if page<1:
                page=1
        except TypeError:
            page=1
        except ValueError:
            page=1
            
        model['prevpage']=page-1
        model['nextpage']=page+1
        sentence=None
        sentences=[]
        
        
        if category:
            model['category']=CategoryLib.getByTag(category)
            if model['category']:
                model['wikis']=[1]
                cpage=0
                wikicat=WikiLib.getCategoryByName(model['category'].wikiname)
                if wikicat:
                    while model['wikis']:
                        model['wikis']=WikiModel.all().filter('categories =',wikicat.key()).fetch(10,(cpage*10))
                        cpage=cpage+1
                        for wiki in model['wikis']:
                            sentence=SentenceModel.all().filter("wiki =",wiki).filter("status =",0).order("order").get()
                            if sentence:
                                wikis=False
                                break;
             
        elif wikititle:
            wiki=WikiModel.all().filter("title =",wikititle).get()
            if wiki:
                sentence=SentenceModel.all().filter("wiki =",wiki).filter("status =",0).order("order").get()
                if sentence:
                    sentences=SentenceModel.all().filter("wiki =",wiki).filter("order >=",sentence.order).order("order").fetch(limit,(page-1)*limit)
        else:
            sentence=False
            cats=ArticleLib.getTopTags()
            
            l=len(cats);i=0
            while i<l and not sentence:
                cat=cats[i];i=i+1
                category=CategoryLib.getByTag(cat)
                if category and category.wikiname:
                    wikicat=WikiLib.getCategoryByName(category.wikiname)
                    if wikicat:
                        wikis=[1]
                        cpage=0
                        while wikis:
                            wikis=WikiModel.all().filter("categories =",wikicat.key()).fetch(10,(cpage*10))
                            cpage=cpage+1
                            for wiki in wikis:
                                sentence=SentenceModel.all().filter("wiki =",wiki).filter("status =",0).order("order").get()
                                if sentence:
                                    model['wikis']=wikis
                                    sentences=SentenceModel.all().filter("wiki =",wiki).filter("order >=",sentence.order).order("order").fetch(limit,(page-1)*limit)
                                    break;
                                #else:
                                #    logging.warn("no sentences found for wiki "+str(wiki.key()))
                    #else:
                    #    logging.warn("no wiki category found for "+cat)            
                #else:
                #    logging.warn("category has no wikiname")
                    
                            
            #sentence=SentenceModel.all().filter("status =",0).order("order").get()
        
        if sentences:
            sentence.updated=datetime.datetime.now()
            sentence.save()
        else:
            sentence=SentenceModel.all().filter("status =",0).order("updated").get()
            if sentence:
                sentences=SentenceModel.all().filter("wiki =",sentence.wiki).filter("order >=",sentence.order).order("order").fetch(limit,(page-1)*limit)
            
        
        for sentence in sentences:
            sentence.categories=[]
            
            for wikicatkey in sentence.wiki.categories:
                wikicat=WikiCategoryModel.get(wikicatkey)
                category=CategoryLib.getByWikiName(wikicat.name)
                if category:
                    sentence.categories.append(category)
                elif wikicat.name not in CategoryLib.IGNORE_CATEGORIES:
                    logging.error("sentence "+str(sentence.key())+" refers to nonexistent category "+wikicat.name)
    
        if not sentence.categories:
            logging.warn("sentence "+str(sentence.key())+" has no categories")
            
        model['sentences']=sentences
        
        
        return FibQuestionCreatorView(model)
   
    def creatorAction(self,category=None,page=1,wikititle=None,article_key=None):
        
        self.requireLoggedin('qc')
        model={"category":None,"sentences":[],'user':self.user,"wiki":None,'wikititle':wikititle,"article_key":article_key}
        
        key=None
        limit=10
       
        try:
            page=int(page)
            if page<1:
                page=1
        except TypeError:
            page=1
        except ValueError:
            page=1
            
        model['prevpage']=page-1
        model['nextpage']=page+1
        
        cats=[]
        if category:
            cats=[category]
            model['category']=category
            
        if article_key:
            article=ArticleModel.get(article_key)
            if not article:
                raise Exception("Invalid article key")
            if article.category and len(article.category)>1:
                cats=[article.category]
        
            # get all the categories for this article
            article_cats=ArticleLib.getCategories(article)
            
            for article_cat in article_cats:
                cats.append(article_cat.name)
            
        model['wiki']=True
        locking_user=True
        wpage=1
        while locking_user and locking_user != self.user.username and model['wiki']:
            model['wiki']=self.getWikiNeedingQuestions(cats,wpage)
            if model['wiki']:
                model['wiki'].tags=WikiLib.getTags(model['wiki'])
                wpage=wpage+1
                if not model['wiki'].title:
                    logging.error("no title for "+model['wiki'].url)
                    continue
                key='lock/'+model['wiki'].title
                locking_user=memcache.get(key)
        
        if key:
            memcache.set(key,self.user.username,3600)
        
        model['sentences']=SentenceModel.all().filter("wiki =",model['wiki']).order("order").fetch(limit,(page-1)*limit)
             
        return QuestionCreatorView(model)
     
    def getWikiNeedingQuestions(self,cats=None,page=1):
    
        wiki=None
        cpage=1
        if not cats:
            cats=ArticleLib.getTopTags()
        for cat in cats:
            category=CategoryLib.getByTag(cat)
            if category:
                if category.wikiname:
                    wikicat=WikiLib.getCategoryByName(category.wikiname)
                    if wikicat:
                        wikis=WikiModel.all().filter('categories =',wikicat.key()).filter("numsentences =",0).fetch(100)
                        if not wikis:
                            logging.warn("no wiki pages found having category "+wikicat.name)
                            # well then go get some!
                            taskqueue.add(url='/json/cron/acquire_wiki_pages/',params={'category':category.name})
                        for wiki in wikis:
                            if not wiki.title:
                                logging.error("not title for wikimodel: "+wiki.url)
                                continue
                            sentence=SentenceModel.all().filter("wiki =",wiki).filter("status =",0).get()
                            if sentence:
                                if cpage==page:
                                    return wiki
                                else:
                                    cpage=cpage+1
                            else:
                                logging.warn("no sentences found for wiki page "+wiki.title)
                                #well then go get some!
                                taskqueue.add(url="/json/cron/acquire_sentences/",params={'key':wiki.key()})
                                
                    logging.warn("no wikicat found having the name "+category.wikiname)
                            
                else:
                    logging.warn("category "+cat+" has no wikiname")
            else:
                logging.warn("category '"+cat+"' not found")
                
        
        # if we get this far then that means there are no sentences or wiki pages for the given categories so lets just pick one
        sentence=SentenceModel.all().filter("status =",0).order('-updated').get()
        if sentence and sentence.wiki:
            return sentence.wiki
        
        return None
            
    
    def set_answerAction(self,question_id,answer,signature,getanotherquestion=False,tags=None):
       
        self.requireLoggedin()
        
        try:
            qid=int(question_id)
            
        except ValueError,TypeError:
            raise Exception('invalid id')
        
        question=QuestionModel.get_by_id(qid)
        if not question:
            raise Exception('Invalid question id')
        
        # check the signature to determine if the question answered was the same one asked
        is_sig=QuestionLib.isSignature(signature,question_id,Session.sessionid)
        if not is_sig:
            raise Exception('Invalid question signature')
    
        model={"iscorrect":None}
        if question.question_type==2: # if its a true/false question
            logging.info("true false question")
            if question.correct_answer.answer==answer[0]:
                iscorrect=True
            else:
                iscorrect=False
        else:
            logging.info("fill in the blank question")
            import re
            useranswer=""
            for a in answer:
                useranswer=useranswer+" "+a
            
            useranswer=re.sub('\s{2,}', ' ', useranswer).strip().lower()
                
            if QuestionLib.is_integer(useranswer) and not QuestionLib.is_integer(question.correct_answer.answer):
                useranswer=NatLangLib.num2word(int(useranswer))
            
            if len(question.correct_answer.answer) <5:
                if question.correct_answer.answer.lower()==useranswer:
                    iscorrect=True
                else:
                    iscorrect=False
            else:
                # determine how "close" the users answer is to the correct answer
                import difflib
                foo=difflib.SequenceMatcher(None, question.correct_answer.answer.lower(), useranswer).ratio()
                if foo.real>0.85:
                    iscorrect=True
                else:
                    iscorrect=False
                
        useranswer=UserAnswerModel.all().filter("username =",self.user.username).filter("question =",question).get()
        if not useranswer:
            useranswer=UserAnswerModel(username=self.user.username,question=question,iscorrect=iscorrect)
        else:
            useranswer.topa=useranswer.updated
            useranswer.updated=datetime.datetime.now()    
            if useranswer.iscorrect!=iscorrect:
                useranswer.iscorrect=iscorrect
        
        useranswer.save()
        KnowledgeLib.calculate_user_knowledge(self.user,0,question,useranswer)
                
        #record this question as the latest question asked
        """
        q=LastUserQuestionModel.all()
        q.filter("user =",self.user)
        records=q.fetch(10,0)
        if len(records)==0:
            lyqm=LastUserQuestionModel(user=self.user.key(),question=question,cats=question.cats,updated=question.updated)
            lyqm.save();
        elif len(records)==1:
            lyqm=records[0]
            lyqm.question=question
            lyqm.cats=question.cats
            lyqm.updated=question.updated
            lyqm.save()
        else:
            #this is an error condition. reset the records
            for record in records:
                record.delete()
            lyqm=LastUserQuestionModel(user=self.user.key(),question=question,cats=question.cats,updated=question.updated)
            lyqm.save();
        """
                
        model['iscorrect']=iscorrect
        
        
        return NullView(model)
    
    def update_statusAction(self,key,status):
        self.requireLoggedin('admin')
        model={}
        
        question=QuestionModel.get(key)
        
        if not question:
            raise Exception("Question not found")
        
        
        i=int(status)
            
        question.status=i
        question.updated=datetime.datetime.now()
        question.save()

        return model
    
    def updateAction(self,key,question_text):
        self.requireLoggedin('admin')
        model={}
        
        question=QuestionModel.get(key)
        
        if not question:
            raise Exception("Question not found")
        import re
        question.question=re.sub('\s{2,}', ' ', question_text).replace("\n"," ").replace("\r"," ").strip()
        question.updated=datetime.datetime.now()
        question.signature=hashlib.md5(question.question).hexdigest()
        question.save()

        return model
    def update_answerAction(self,key,answer_text):
        self.requireLoggedin('admin')
        model={}
        
        question=QuestionModel.get(key)
        
        if not question:
            raise Exception("Question not found")
        
        answer_text=answer_text.strip()
        
        # find an answer that matches the given answer_text
        answer=AnswerModel.all().filter("answer =",answer_text).get()
        
        if not answer:
            answer=AnswerModel(answer=answer_text,iscorrect=True,signature=hashlib.md5(answer_text).hexdigest())
            answer.save()
            
        if question.correct_answer != answer:
            questions=QuestionModel.all().filter("correct_answer =",question.correct_answer).fetch(2,0)
            if len(questions)==1:
                question.correct_answer.delete()
            question.correct_answer=answer
            question.save()

        return model
    
    def set_sentence_statusAction(self,status,sentence_key):
        
        sentence=SentenceModel.get(sentence_key)
        if not sentence:
            raise Exception("Cant find sentence")
        model={"status":None}
        sentence.status=int(status)
        sentence.save()
        
        model['status']=status
        return model
    
    def deleteAction(self,key):
        self.requireLoggedin('admin')
        model={'deleted':False}
        
        question=QuestionModel.get(key)
        
        if not question:
            raise Exception("Question not found")
        
        model['deleted']=QuestionLib.delete(question)
        
        return model
    
    def delete_categoryAction(self,key,tag):
        self.requireLoggedin('admin')
        model={}
        
        question=QuestionModel.get(key)
        
        if not question:
            raise Exception("Question not found")
        
        category=CategoryLib.getByTag(tag)
        if category:
            if category.key() in question.cats:
                question.cats.remove(category.key())
                question.save()
            
        return model
    
   
        