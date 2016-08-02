# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.home.view.NullView import NullView
from common.lib.MturkLib import MturkLib
import logging
from module.natlang.model.SentenceModel import SentenceModel
from common.lib.CategoryLib import CategoryLib
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
from common.models.QuestionModel import QuestionModel
import hashlib
from common.models.AnswerModel import AnswerModel
from google.appengine.api import mail
from module.question.lib.QuestionLib import QuestionLib

class MturkController(Controller):
    def defaultAction(self,segments,qs):
        return self.indexAction()
    
    def create_fib_questionAction(self,num_questions=10):
        
        #get oldest sentences that are approved and dont have questions attached
        sentences=SentenceModel.all().filter("status =",0).order("updated").fetch(num_questions,0)
        #sentences=SentenceModel.all().filter("signature =",'ead478082bd670463dadc20243566c1e').fetch(1,0)
        
        #logging.info("found "+str(len(sentences))+" sentences")
        
        if len(sentences)==0:
            logging.info('no sentences found')
        else:
            mturklib=MturkLib()
            price=0.10
            balance=mturklib.getAccountBalance()
            
            if balance < price*len(sentences):
                message="you dont have enough money to run MturkController.create_fib_questions";
                logging.error(message)
                mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'create_fib_question results',message)
            else:
                
                for sentence in sentences:
                    sentence.status=3 # mark the sentence as being processed so that we dont process it more than once
                    if sentence.wiki:
                        catkeys=sentence.wiki.categories
                        categories=[]
                        for key in catkeys:
                            categories.append(WikiCategoryModel.get(key))
                        
                        previous_sentence=None    
                        foo=SentenceModel.all().filter("wiki =",sentence.wiki).filter("order =",sentence.order-1).get()
                        if foo:
                            previous_sentence=foo.sentence
                        following_sentence=None
                        
                        foo=SentenceModel.all().filter("wiki =",sentence.wiki).filter("order =",sentence.order+1).get()
                        if foo:
                            following_sentence=foo.sentence
                        
                        mturklib.create_fib_question(sentence,price,categories,previous_sentence,following_sentence)
                        
                    else:
                        logging.error("sentence "+sentence.sentence+" is not attached to any wiki")
                    sentence.save()
                    
            
        return {"numsentences":len(sentences)}
        
    
    def create_questionAction(self,num_questions=10):
        
        #get oldest sentences that are approved and dont have questions attached
        sentences=SentenceModel.all().filter("numquestions =",None).filter("status =",2).order("updated").fetch(num_questions,0)
        #sentences=SentenceModel.all().filter("signature =",'ead478082bd670463dadc20243566c1e').fetch(1,0)
        
        #logging.info("found "+str(len(sentences))+" sentences")
        
        if len(sentences)==0:
            logging.info('no sentences found')
        else:
            mturklib=MturkLib()
            price=0.20
            balance=mturklib.getAccountBalance()
            if balance < price*len(sentences):
                message="you dont have enough money to run MturkController.create_questions";
                logging.error(message)
                mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'create_question results',message)
            else:
                
                for sentence in sentences:
                    sentence.status=3 # mark the sentence as being processed so that we dont process it more than once
                    if sentence.wiki:
                        catkeys=sentence.wiki.categories
                        categories=[]
                        for key in catkeys:
                            categories.append(WikiCategoryModel.get(key))
                        mturklib.create_question(sentence,price,categories)
                        sentence.numquestions=0
                        
                    else:
                        logging.error("sentence "+sentence.sentence+" is not attached to any wiki")
                    sentence.save()
                    
            
        return {"numsentences":len(sentences)}
    
    def create_hit_typeAction(self,hittype=None):
        m=MturkLib()
        model={"HITTypeId":None}
        
        if not hittype:
            return model
        
        if hittype=='sentence':
            Title="Is This Sentence Declarative?"
            Description="Read an English sentence and answer yes if it declares any useful facts."
            Reward=0.05
            AssignmentDurationInSeconds=30
            Keywords="English Grammar"
        elif hittype=='question':
            
            Title="Rewrite a sentence in the form of a question"
            Description="Rewrite an English sentence in the form of a question."
            Reward=0.20
            AssignmentDurationInSeconds=180
            Keywords="English Writing Question"
        elif hittype=='fibquestion':
            Title="Write a quiz question"
            Description="Rewrite an English sentence in the form of a 'fill in the blank' question."
            Reward=0.10
            AssignmentDurationInSeconds=180
            Keywords="English Writing Question"
        else:
            raise Exception('Invalid Hittype')
            
        
        """
        Title="Write the answer to a question"
        Description="Read a question in English and write the correct answer based on the given information."
        Reward=0.15
        AssignmentDurationInSeconds=60
        Keywords="English Writing Quiz Question Answer"
        """
        
        """
        Title="Write a wrong answer for a quiz question"
        Description="Read a question and answer, then write an answer to the question that is wrong."
        Reward=0.25
        AssignmentDurationInSeconds=60
        Keywords="English Writing Quiz Question Answer"
        """
        
        HITTypeId=m.RegisterHITType(Title,Description,Reward,AssignmentDurationInSeconds,Keywords);
        logging.info("hit type id = "+HITTypeId)
        model['HITTypeId']=HITTypeId
        
        return model
    def indexAction(self,tag=None):
        model=None
        return NullView(model)
    
    def remove_expired_hitsAction(self):
        model=None
        m=MturkLib()
        
        page=1
        hit_ids=m.GetReviewableHITs(MturkLib.HIT_TYPE_SENTENCE_CLASSIFY,page)
        
        while hit_ids:
            for hit_id in hit_ids:
                (assignment_id,answer,signature)=m.GetAssignmentsForHIT(hit_id)
                
                if not assignment_id or not answer or not signature:
                    logging.error("Failed to get data from MturkLib.GetAssignmentsForHIT")
                    continue
                
                sentence=SentenceModel.all().filter("signature =",signature).get()
                if sentence:
                    if answer=='yes':
                        sentence.type=1
                    else:
                        sentence.type=0
                    sentence.save()
                else:
                    logging.error('sentence not found for signature: '+signature)
                
                m.ApproveAssignment(assignment_id)
            page=page+1
            hit_ids=m.GetReviewableHITs(MturkLib.HIT_TYPE_SENTENCE_CLASSIFY,page)
    
        return NullView(model)
    
    def get_question_hitsAction(self):
        m=MturkLib()
        
        num_approvals=0
        
        page=1
        hit_ids=m.GetReviewableHITs(MturkLib.HIT_TYPE_WRITE_QUESTION,page)
        while hit_ids:
            for hit_id in hit_ids:
                m.SetHITAsReviewing(hit_id)
                (assignment_id,worker_id,question,foo,signature,cant_rewrite)=m.getQuestionHit(hit_id)
                
                sentence=SentenceModel.all().filter("signature =",signature).get()
                if not sentence:
                    logging.error("sentence signature:"+signature+" doest not exist")
                    continue
                
                if cant_rewrite:
                    #QuestionLib.removeMissingSentences(sentence.key())
                    #sentence.delete()
                    sentence.status=5# reject the sentence
                    sentence.save()
                    num_approvals=num_approvals+1
                    m.ApproveAssignment(assignment_id)
                    continue
                    
                if not assignment_id or not foo or not signature or not question:
                    logging.error("Failed to get data from MturkLib.getQuestionHit")
                    continue
                
                
                if sentence:
                    qsignature=hashlib.md5(question).hexdigest()
                    questionm=QuestionModel.all().filter("signature =",qsignature).get()
                    if questionm:
                        logging.error("question already exists!")
                    else:
                        questionm=QuestionModel(question=question,signature=qsignature,username=worker_id)
                        questionm.sentences.append(sentence.key())
                        questionm.question_type=0
                        questionm.status=1 # mark the question as created but unreviewed
                        
                        # find the categories associated with this sentence and attach them to the question
                        if sentence.wiki:
                            wikicat_keys=sentence.wiki.categories
                            if not wikicat_keys:
                                logging.warn("sentence "+str(sentence.key())+" has no categories")
                            for wikicat_key in wikicat_keys:
                                wikicat=WikiCategoryModel.get(wikicat_key)
                                if wikicat:
                                    cat=CategoryLib.getByWikiName(wikicat.name)
                                    if cat:
                                        questionm.cats.append(cat.key())
                                    else:
                                        logging.warn("cant find category having wikiname "+wikicat.name)
                                else:
                                    logging.warn("cant find wikicat having key "+str(wikicat_key))
                        else:
                            logging.warn("sentence "+str(sentence.key())+" has no wiki attached")
            
                        answer=foo.replace("\n"," ").replace("\r"," ")
                        
                        correct_answer=AnswerModel.all().filter("answer =",answer).get()
                        if not correct_answer:
                            correct_answer=AnswerModel(answer=answer,iscorrect=True,signature=hashlib.md5(answer).hexdigest())
                            correct_answer.save()
                        questionm.correct_answer=correct_answer
                        
                        questionm.save()
                        
                        if sentence.numquestions==None:
                            sentence.numquestions=1
                        else:
                            sentence.numquestions=sentence.numquestions+1
                        sentence.status=4 # mark the sentence as fully processed so that no more processing takes place
                        sentence.save()
                else:
                    logging.error('sentence not found for signature: '+signature)
                
                num_approvals=num_approvals+1
                m.ApproveAssignment(assignment_id)
                #m.DisposeHIT(hit_id)
            page=page+1
            hit_ids=m.GetReviewableHITs(MturkLib.HIT_TYPE_WRITE_QUESTION,page)
                
        
        return num_approvals
    
    def get_fibquestion_hitsAction(self):
        m=MturkLib()
        
        num_approvals=0
        
        page=1
        hit_ids=m.GetReviewableHITs(MturkLib.HIT_TYPE_WRITE_FIB_QUESTION,page)
        
        while hit_ids:
            for hit_id in hit_ids:
                m.SetHITAsReviewing(hit_id)
                (assignment_id,worker_id,question_text,foo,signature,cant_rewrite)=m.getFibQuestionHit(hit_id)
                
                sentence=SentenceModel.all().filter("signature =",signature).get()
                if not sentence:
                    logging.error("sentence signature:"+signature+" doest not exist")
                    continue
                
                if cant_rewrite:
                    sentence.status=5# reject the sentence
                    sentence.save()
                    num_approvals=num_approvals+1
                    m.ApproveAssignment(assignment_id)
                    continue
                
                if not assignment_id or not signature or not question_text:
                    logging.error("Failed to get data from MturkLib.getQuestionHit")
                    continue
                
                tags=[] # the question inherits the categories of the sentence
                if sentence.wiki:
                    wikicat_keys=sentence.wiki.categories
                    if not wikicat_keys:
                        logging.warn("sentence "+str(sentence.key())+" has no categories")
                    for wikicat_key in wikicat_keys:
                        wikicat=WikiCategoryModel.get(wikicat_key)
                        if wikicat:
                            cat=CategoryLib.getByWikiName(wikicat.name)
                            if cat:
                                tags.append(cat.name)
                            else:
                                logging.warn("cant find category having wikiname "+wikicat.name)
                        else:
                            logging.warn("cant find wikicat having key "+str(wikicat_key))
                else:
                    logging.warn("sentence "+str(sentence.key())+" has no wiki attached")
    
            
                question=QuestionLib.createQuestion(question_text,None,tags,sentence.key(),worker_id)
                if question:
                    sentence.status=4 # mark the sentence as fully processed so that no more processing takes place
                    sentence.save()
                
                num_approvals=num_approvals+1
                m.ApproveAssignment(assignment_id)
            page=page+1
            hit_ids=m.GetReviewableHITs(MturkLib.HIT_TYPE_WRITE_QUESTION,page)
                
        
        return num_approvals
    
    
    def getsentencehitsAction(self):
        model={"num_sentences":0}
        m=MturkLib()
        num_approvals=0
        page=1
        hit_ids=m.GetReviewableHITs(MturkLib.HIT_TYPE_SENTENCE_CLASSIFY,page)
        
        while hit_ids:
            for hit_id in hit_ids:
                m.SetHITAsReviewing(hit_id)
                (assignment_id,WorkerId,answer,signature)=m.getSentenceHit(hit_id)
                
                if not assignment_id or not answer or not signature:
                    logging.error("Failed to get data from MturkLib.GetAssignmentsForHIT")
                    continue
                
                sentence=SentenceModel.all().filter("signature =",signature).get()
                if sentence:
                    model['num_sentences']=model['num_sentences']+1
                    if answer=='yes':
                        sentence.status=2 # mark the sentence so that we can now rewrite it as a sentence
                    else:
                        sentence.status=5 # mark the sentence as rejected so that no more processing takes place ever.
                    sentence.username=WorkerId
                    sentence.save()
                else:
                    logging.error('sentence not found for signature: '+signature)
                
                
                m.ApproveAssignment(assignment_id)
                num_approvals=num_approvals+1
            page=page+1
            hit_ids=m.GetReviewableHITs(MturkLib.HIT_TYPE_SENTENCE_CLASSIFY,page)
        
        return model
 
    

  