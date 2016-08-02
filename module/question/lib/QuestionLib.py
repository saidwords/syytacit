# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.models.QuestionModel import QuestionModel
from google.appengine.api import memcache
from common.models.CategoryModel import CategoryModel
from module.article.model.SparseQuestion import SparseQuestion
from common.models.AnswerModel import AnswerModel
from module.article.model.SparseAnswer import SparseAnswer
import logging
import random
import hashlib
from common.lib.CategoryLib import CategoryLib
from google.appengine.ext import db
from module.natlang.model.SentenceModel import SentenceModel
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
import datetime
from common.lib.AlreadyExistsException import AlreadyExistsException
from common.models.UserAnswerModel import UserAnswerModel

class QuestionLib:
    """
    gets a random question from the database of questions
    """
    def getRandomQuestion(tags,cacheread=True,cachewrite=True):
        questions=None
        if not tags:
            return None
            totalquestions=memcache.get('totalquestions_None')
            if totalquestions==None:
                totalquestions=QuestionModel.all().filter("status =",2).count()
                memcache.set('totalquestions_None',totalquestions,3600)
            if totalquestions > 0:
                offset=random.randint(0,totalquestions-1)
                questions=QuestionModel.all().filter("status =",2).fetch(1,offset)
        else:
            for tag in tags:
                cat_key=CategoryLib.getByTag(tag,True)
                if cat_key:
                    totalquestions=memcache.get('totalquestions_'+tag)
                    if totalquestions==None:
                        totalquestions=QuestionModel.all().filter("cats =",cat_key).filter("status =",2).count()
                        memcache.set('totalquestions_'+tag,totalquestions,3600)
                    if totalquestions > 0:
                        offset=random.randint(0,totalquestions-1)
                        questions=memcache.get("rq_"+tag+"_"+str(offset))
                        if not questions:
                            questions=QuestionModel.all().filter("cats =",cat_key).filter("status =",2).fetch(1,offset)
                            memcache.set("rq_"+tag+"_"+str(offset),questions,3600)
                    if questions:
                        break
                else:
                    logging.warn("cant find category "+tag)  
        if questions:
            return questions[0]
        else:
            return None         
        
    """
    Get a question for the given user
    """
    def getQuestionForUser(user,tags):
        return False;
        ranswers=[]
        rquestion=SparseQuestion()
        
        #get the last question that was asked of the user
        q=None
        #q=LastUserQuestionModel.all()
        q.filter("user =",user)
        question=q.get()
        
        if question:
            logging.info("found question. now searching for newer question")
            q=QuestionModel.all()
            q.filter("updated >",question.updated)
            q.order("-updated")
            question=q.get()
            if question:
                logging.info("found newer question")
        else:
            logging.info("no question found")

        if not question: # get the oldest question
            logging.info("no question found")
            q=QuestionModel.all()
            q.order("updated")
            question=q.get()
                
        if question:
            rquestion=SparseQuestion()
            rquestion.id=question.key().id()
            rquestion.question=question.question
            rquestion.question_type=question.question_type
            rquestion.tags=QuestionLib.getTags(question);
            #get answers for the question
            
            canswer=SparseAnswer()
            canswer.id=question.correct_answer.key().id()
            canswer.answer=question.correct_answer.answer
            ranswers.append(canswer)
            
            answers=AnswerModel.get(question.wrong_answers)
            
            for answer in answers:
                foo=SparseAnswer()
                foo.id=answer.key().id()
                foo.answer=answer.answer
                ranswers.append(foo)
        
        random.shuffle(ranswers)
               
        return (rquestion,ranswers)
    
    def getTags(question):
        tags=[]
        cats=CategoryModel.get(question.cats)
        for cat in cats:
            tags.append(cat.name)
        return tags
    
    def getCategories(question,keys_only=False):
        tags=[]
            
        #cats=CategoryModel.get(question.cats)
        for cat_key in question.cats:
            cat = CategoryModel.get(cat_key)
            
            if keys_only:
                tags.append(cat.key())
            else:
                tags.append(cat)
        return tags
    
    def getSignature(question_id,user_id):
        salt='fda8c1a1d7a3fe36ce31fdb107e460e1';
        import datetime
        
        now = datetime.datetime.now()
        h=now.hour
        
        signature=hashlib.md5(str(question_id)+'_'+str(user_id)+'_'+str(h)+salt).hexdigest()
        
        return signature
    
    def isSignature(signature,question_id,user_id):
        prevsalt='fda8c1a1d7a3fe36ce31fdb107e460e1';
        salt='fda8c1a1d7a3fe36ce31fdb107e460e1';
        import datetime
        
        now = datetime.datetime.now()
        h=now.hour
        
        correct_signature=hashlib.md5(str(question_id)+'_'+str(user_id)+'_'+str(h)+salt).hexdigest()
        if signature==correct_signature:
            return True
        
        correct_signature=hashlib.md5(str(question_id)+'_'+str(user_id)+'_'+str(h)+salt).hexdigest()
        if signature==correct_signature:
            return True
        
        correct_signature=hashlib.md5(str(question_id)+'_'+str(user_id)+'_'+str(h)+prevsalt).hexdigest()
        if signature==correct_signature:
            return True
        
        correct_signature=hashlib.md5(str(question_id)+'_'+str(user_id)+'_'+str(h-1)+prevsalt).hexdigest()
        if signature==correct_signature:
            return True
        
        return False;
    
    def getNextQuestion(question_id=None,cat_keys=None):
        if question_id: # get the next question that follows this question_id
            current_question=QuestionModel.get_by_id(question_id)
            if not current_question:
                message="question not found for id "+question_id
                logging.error(message)
                raise Exception(message)
            if cat_keys:
                question=QuestionModel.all().filter("status =",2).filter("cats in",cat_keys).filter("updated >",current_question.updated).get()
                if not question:
                    question=QuestionModel.all().filter("status =",2).filter("cats in",cat_keys).filter("updated >",0).get()
            else:
                question=QuestionModel.all().filter("status =",2).filter("updated >",current_question.updated).get()
            if not question:
                question=QuestionModel.all().filter("status =",2).filter("updated >",0).get()
        else:
            question=QuestionModel.all().filter("status =",2).order("updated").get()
            
        return question
    
    def removeMissingSentences(sentence_key):
        num_references=0
        records=[1]
        page=1
        while records:
            records=QuestionModel.all().filter("sentences  =",sentence_key).fetch(100, (page-1)*100)
            page=page+1
            for record in records:
                record.sentences.remove(sentence_key)
                record.save()
                num_references=num_references+1
                
        logging.info("removed "+str(num_references)+" references to sentence")
        return num_references
    
    def toArray(question):
        result=[]
        phrase=""
        i=0
        l=len(question)
        while i < l:
            if question[i]=='_' and i<(l-1) and question[i+1]=='_':
                while i<(l-1) and question[i]=='_':
                    i=i+1
                if phrase !="":
                    result.append(phrase)
                    if question[i]=='_':
                        phrase=""
                    else:
                        phrase=question[i]
                result.append(None)
            else:
                phrase=phrase+question[i]
            i=i+1

        if phrase !="":
            result.append(phrase)

        return result
    
    def updateQuestion(question,answer_text,ignore=None,tags=None,sentence_key=None,username=None,question_type=1):
        raise Exception("function not implemented");
        return True
    
    def createQuestion(question_text,answer_text,ignore=None,tags=None,sentence_key=None,username=None,question_type=1):
        import re
        question_text=re.sub('\s{2,}', ' ', question_text).replace("\n"," ").replace("\r"," ").strip()
        
        signature=hashlib.md5(question_text).hexdigest()
        
        question=QuestionModel.all().filter("signature =",signature).get()
        
        if question:
            raise AlreadyExistsException('this question already exists')
            
        sentence=SentenceModel.get(sentence_key)
        if not sentence:
            raise Exception("Invalid sentence key")
        
        cats=[]
        if tags:
            for tag in tags:
                cat = CategoryLib.getByTag(tag)
                if not cat:
                    raise Exception('invalid tag '+tag)
                cats.append(cat.key())
        else: # get the categories from the sentence
            for wikicatkey in sentence.wiki.categories:
                wikicat=WikiCategoryModel.get(wikicatkey)
                category=CategoryLib.getByWikiName(wikicat.name)
                if not category:
                    catname=wikicat.name.replace('_',' ').lower()
                    category=CategoryLib.getByTag(catname,True);
                    if not category and wikicat.name not in CategoryLib.IGNORE_CATEGORIES:
                        logging.info("creating new category for "+wikicat.name)
                        new_category = CategoryModel(name=catname,wikiname=wikicat.name)                   
                        new_category.save()
                        category=new_category.key()
                        
                else:
                    cats.append(category.key())
        
        for i in range(0,len(answer_text)):
            answer_text[i]=answer_text[i].decode("UTF-8")
            
        if question_type==1: # fill in the blank
            canswer=" ".join(answer_text).strip()
        elif question_type==2: # true/false
            canswer=answer_text[0].strip().lower()
            
            if canswer=='true' or canswer=='false':
                pass
            else:
                raise Exception('invalid answer '+canswer)
        else:
            raise Exception('invalid question_type '+str(answer_text))
                
        correct_answer=AnswerModel.all().filter("answer =",canswer).get()
        if not correct_answer:
            signature=hashlib.md5(canswer.encode("ascii",errors="ignore")).hexdigest()
            correct_answer=AnswerModel(answer=canswer,iscorrect=True,signature=signature)
            correct_answer.save() 
    
        question_text=question_text.decode("UTF-8")
    
        #logging.info("question_Type="+str(question_type))        
        sentences=[sentence.key()]
        question=QuestionModel(question_type=question_type,status=1,question=question_text,signature=signature,correct_answer=correct_answer,cats=cats,username=username)
        question.sentences=sentences
        question.save()
        #logging.info("saved question "+question.question+" having type="+str(question.question_type)+" and status "+str(question.status))
        sentence.status=1
        sentence.updated=datetime.datetime.now()
        sentence.save()
            
        return question
    
    def createFibQuestion(question_text,answer_text,tags=None,sentence_key=None,username=None):
        import re
        question_text=re.sub('\s{2,}', ' ', question_text).replace("\n"," ").replace("\r"," ").strip()
        
        signature=hashlib.md5(question_text).hexdigest()
        
        question=QuestionModel.all().filter("signature =",signature).get()
        
        if question:
            raise Exception('This question already exists')
        
        sentence=SentenceModel.get(sentence_key)
        if not sentence:
            raise Exception("Invalid sentence key")
        
        
        cats=[]
        if tags:
            for tag in tags:
                cat = CategoryLib.getByTag(tag)
                if not cat:
                    raise Exception('invalid tag '+tag)
                cats.append(cat.key())
        else: # get the categories from the sentence
            for wikicatkey in sentence.wiki.categories:
                wikicat=WikiCategoryModel.get(wikicatkey)
                category=CategoryLib.getByWikiName(wikicat.name)
                if not category:
                    catname=wikicat.name.replace('_',' ').lower()
                    category=CategoryLib.getByTag(catname,True);
                    if not category and wikicat.name not in CategoryLib.IGNORE_CATEGORIES:
                        logging.info("creating new category for "+wikicat.name)
                        new_category = CategoryModel(name=catname,wikiname=wikicat.name)                   
                        new_category.save()
                        category=new_category.key()
                        
                else:
                    cats.append(category.key())
        
                    
        qtokens=sentence.sentence.split(" ")
        atokens=question_text.split(" ")
        stripchars="\",.'"
        canswer="";
        i=0
        for word in atokens:
            # is the word a blank?
            isblank = word.find('__')
            if isblank>=0:
                    # if the blank contains trailing characters then strip them
                    if word[-1:] in stripchars:
                            canswer=canswer+" "+qtokens[i].strip(stripchars)
                            atokens[i]=atokens[i].strip(stripchars)
                    else:
                            canswer=canswer+" "+qtokens[i]
                    atokens[i]='__'
            i=i+1

                        
        canswer=canswer.strip()
        question_text=" ".join(atokens).strip()
        correct_answer=AnswerModel.all().filter("answer =",canswer).get()
        if not correct_answer:
            correct_answer=AnswerModel(answer=canswer,iscorrect=True,signature=hashlib.md5(canswer).hexdigest())
            correct_answer.save()
        
        sentences=[sentence.key()]
        question=QuestionModel(question_type=1,status=1,question=question_text,signature=signature,correct_answer=correct_answer,cats=cats,username=username)
        question.sentences=sentences
        question.save()
        sentence.status=1
        sentence.updated=datetime.datetime.now()
        sentence.save()
            
        return question
    
    def is_integer(var):
        try:
            int(var)
            return True
        except ValueError:
            return False
        
    def delete(question):
        #delete all references to the question
        useranswers=UserAnswerModel.all().filter("question =",question)
        for useranswer in useranswers:
            useranswer.delete()
        
        # delete the questions answer
        if question.correct_answer:
            otherquestions=QuestionModel.all().filter("correct_answer =",question.correct_answer).fetch(2,0)
            if len(otherquestions)==1:
                # this means the answer is only referenced by this question, so its ok to delete the answer
                question.correct_answer.delete()
        
        question.delete()
        
        return True
    delete=staticmethod(delete)
    is_integer=staticmethod(is_integer)
    removeMissingSentences=staticmethod(removeMissingSentences)
    isSignature=staticmethod(isSignature)
    getSignature=staticmethod(getSignature)
    getTags=staticmethod(getTags)
    getCategories=staticmethod(getCategories)
    getRandomQuestion = staticmethod(getRandomQuestion)
    getQuestionForUser = staticmethod(getQuestionForUser)
    getNextQuestion = staticmethod(getNextQuestion)
    toArray = staticmethod(toArray)
    createQuestion=staticmethod(createQuestion)
    createFibQuestion=staticmethod(createFibQuestion)
    updateQuestion=staticmethod(updateQuestion);