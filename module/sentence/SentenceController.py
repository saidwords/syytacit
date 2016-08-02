# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.sentence.view.SentenceView import SentenceView
from module.natlang.model.SentenceModel import SentenceModel
from module.wiki.model.WikiModel import WikiModel
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
from random import random
from module.home.view.NullView import NullView
from module.sentence.model.SentenceViewModel import SentenceViewModel
from module.sentence.model.QuestionViewModel import QuestionViewModel
from common.models.QuestionModel import QuestionModel
import hashlib
from module.sentence.model.AnswerViewModel import AnswerViewModel
from common.models.AnswerModel import AnswerModel
import logging


class SentenceController(Controller):
    def deleteAction(self,tag=None):
        self.requireLoggedin('admin')
        model=SentenceViewModel();
        
        sentences=self.getSentences(1, tag)
        while sentences:
            for sentence in sentences:
                sentence.delete()
            sentences=self.getSentences(1, tag)
        
        
        return NullView(model)
    def defaultAction(self,segments,qs):
        return self.indexAction()
    
    def indexAction(self,page=1,tag=None):
        return self.browseAction(page, tag)
    
    #sends a list of sentences to mturk for evaluation as declarative sentences
    # send no more than $15 per week
    def sendsentences2mturk(self):
        model=SentenceViewModel()
        
        cost_per_hit=0.05
        max_hits=300
        
        #get the oldest wiki that has sentences that have not been processed by mturk
        
        wiki=WikiModel.all().filter("numsentences").order("date_updated").fetch()
        
        #model.tag=cat.name
        
        return NullView(model)
    
    def getsentencesAction(self,page=1,tag=None,limit=10):
        model=SentenceViewModel();
        
        try:
            tmp=int(page)
            if tmp <1:
                page=1
            else:
                page=tmp
            tmp=int(limit)
            if tmp <1:
                limit=1
            else:
                limit=tmp
        except ValueError:
            page=1
            limit=10
            
        model.page=page
        model.tag=tag
        try:
            model.sentences= self.getSentences(page, tag,limit)
        except Exception,e:
            model.exception=e
            
            
        return NullView(model);
    
    def rejectsentenceAction(self,signature):
        self.requireLoggedin('admin')
        
        model=None
        
        s=SentenceModel.all().filter('signature =',signature).get()
        if s:
            s.score=s.score-1
            if s.score<0:
                s.score=0
                s.status=2
            s.status=2
            s.save()
        else:
            raise Exception('Sentence not found')
        
        return NullView(model)
    
    def browseAction(self,page=1,tag=None):
        self.requireLoggedin('admin')
        model=SentenceViewModel()
        
        model.tags=WikiCategoryModel.all().order("name").fetch(2046)
        
        try:
            tmp=int(page)
            if tmp <1:
                page=1
            else:
                page=tmp
        except ValueError:
            page=1
            
        model.previouspage=page-1
        model.nextpage=page+1
        
        if not tag: # get a random category
            q=WikiCategoryModel.all()
            maxrecords=q.count()
            offset=int(random()*maxrecords)
            cat=q.fetch(1,offset)
            tag=cat[0].name
        model.tag=tag
            
        try:
            model.sentences= self.getSentences(page, tag)
        except Exception,e:
            model.exception=e
    
        return SentenceView(model)
    
    def getSentences(self,page,tag,limit=10):
        sentences=[]
        
        if tag=="":
            q=SentenceModel.all()
            foo=q.fetch(limit,(page-1)*limit)
            sentences.extend(foo)
            numsentences=len(sentences)
            return sentences
            
        else:
            # get the categorymodel having the given tag
            cat=WikiCategoryModel.all().filter("name =",tag).get()
            if not cat:
                raise Exception("cant find tag: "+tag)
            # get all wikimodels having the given tag
            wikis=WikiModel.all().filter("categories =",cat.key()).fetch(limit,0)
        
      
            if not wikis:
                return sentences
            
            # get sentences for the given wiki
            for wiki in wikis:
                q=SentenceModel.all()
                q.order("order")
                q.filter("wiki =",wiki.key()).filter('status =',0)
                logging.info('fetching from wiki '+wiki.url)
                foo=q.fetch(limit,(page-1)*limit)
                sentences.extend(foo)
                numsentences=len(sentences)
                if numsentences>limit:
                    return sentences
                
        return sentences
    
    def getquestionsAction(self,sentences=None):
        model = QuestionViewModel()
        if not sentences:
            raise Exception('missing required parameter')
        model.questions=[]
        is_array = lambda var: isinstance(var, (list, tuple))
        if not is_array(sentences):
            sentences=[sentences]

        for signature in sentences:
            s=SentenceModel.all().filter('signature =',signature).get()
            if s:
                qs=QuestionModel.all().filter('sentences =',s.key()).fetch(12)
                for q in qs:
                    q.id=q.key().id()
                    model.questions.append(q)
            
        return NullView(model)
    
    def savequestionAction(self,id=None,question=None,sentences=None,tag=None):
        self.requireLoggedin('admin')
        
        model = QuestionViewModel()
        if not question:
            raise Exception('missing required parameter')
        if not sentences:
            raise Exception('missing required parameter')
        
        is_array = lambda var: isinstance(var, (list, tuple))
        if not is_array(sentences):
            sentences=[sentences]
            
        # get category for the given tag
        cat = None
        cats=[]
        if tag:
            cat=WikiCategoryModel.all().filter("name =",tag).get()
            if cat:
                cats.append(cat.key())
                
        signature=hashlib.md5(question).hexdigest()
        if id==None or id=='null' or id=='0': # create a new question
            q = QuestionModel(signature=signature,question=question,cats=cats)
            q.user=self.user
            #update the sentence.numquestions value
            for signature in sentences:
                s=SentenceModel.all().filter('signature =',signature).get()
                if s:
                    if s.numquestions:
                        s.numquestions=s.numquestions+1
                    else:
                        s.numquestions=1
                    s.save()
        else: #update an existing question
            try:
                q=QuestionModel.get_by_id(int(id))
                if q:
                    if q.question!=question:
                        q.question=question
                        q.signature=signature
                        q.cats=cats
                #TODO: update the question text if it has changed
            except ValueError:
                raise Exception('invalid id')
                
            #TODO: update the question if it has changed
        if q:
            dbsentences=[]
            for signature in sentences:
                s=SentenceModel.all().filter('signature =',signature).get()
                if s:
                    dbsentences.append(s.key())
            q.sentences=dbsentences
            q.cats=cats
            q.save()
            
        if q.key():
            model.question_id=q.key().id()
            
        return NullView(model)
    
    def deletequestionAction(self,id):
        self.requireLoggedin('admin')
        model = QuestionViewModel()
        try:
            tmp=int(id)
            q=QuestionModel.get_by_id(tmp)
        except ValueError:
            raise Exception('invalid id')
            
        if q:
            #delete all the answers attached to this question
            for answer in q.answers:
                answer.delete()
            q.delete()
            #TODO: update the value in sentencemodel.numquestions
            for key in q.sentences:
                s=SentenceModel.get(key)
                if s:
                    if s.numquestions:
                        s.numquestions=s.numquestions-1
                        if s.numquestions<0:
                            s.numquestions=0
                    else:
                        s.numquestions=0
                    s.save()
        else:
            raise Exception('cant find question')
            
        return NullView(model)
    
    def saveanswerAction(self,question_id,answer_id,answer,is_correct):
        self.requireLoggedin('admin')
        model=AnswerViewModel();
       
        if not question_id:
            raise Exception('missing required parameter')
        if not answer_id:
            raise Exception('missing required parameter')
        if not answer:
            raise Exception('missing required parameter')
        if not is_correct:
            raise Exception('missing required parameter')
        if is_correct=='true':
            is_correct=True
        else:
            is_correct=False
        
        q=QuestionModel.get_by_id(int(question_id))
        
        if not q:
            raise Exception('invalid question id')
        
        signature=hashlib.md5(answer).hexdigest()
        if answer_id==None or answer_id=='null' or answer_id=='0': # create a new answer
            a = AnswerModel(signature=signature,answer=answer,question=q,iscorrect=is_correct)
        else: #update an existing answer
            try:
                a=AnswerModel.get_by_id(int(answer_id))
                if a:
                    a.answer=answer
                    a.signature=signature
                    a.question=q
                    a.iscorrect=is_correct
            except ValueError:
                raise Exception('invalid id')
        
        a.save()
        if a.key():
            model.answer_id=a.key().id()
            model.answer=a
            
        model.question_id=question_id
        
        return NullView(model)
    
    def getanswersAction(self,question_id):
        self.requireLoggedin('admin')
        model = QuestionViewModel()
        if not question_id:
            raise Exception('missing required parameter')
        
        try:
            q=QuestionModel.get_by_id(int(question_id))
            model.question_id=int(question_id)
            if not q:
                raise Exception('Cant find question')
        except ValueError:
            raise Exception('invalid id')
        
        model.answers=AnswerModel.all().filter('question =',q.key()).fetch(21)

        for i, value in enumerate(model.answers):
            model.answers[i].id=model.answers[i].key().id();
        
        return NullView(model)
    
    def deleteanswerAction(self,id):
        self.requireLoggedin('admin')
        try:
            a=AnswerModel.get_by_id(int(id))
            if a:
                a.delete()
            else:
                raise Exception('invalid id')
        except ValueError:
            raise Exception('invalid id')
        
        return NullView(True)