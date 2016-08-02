# coding=UTF-8
# -*- coding: UTF-8 -*-
#!/usr/bin/env python

# Import libraries
import time
import hmac
import sha
import base64
import xml.dom.minidom
import logging
from module.natlang.model.SentenceModel import SentenceModel
from common.models.AnswerModel import AnswerModel
import urllib
from google.appengine.api import urlfetch
import datetime

"""
https://requester.mturk.com/mturk/manageHITs
http://docs.amazonwebservices.com/AWSMechTurk/latest/AWSMturkAPI/Welcome.html?r=7649
"""
class MturkLib:
    # Define constants
    AWS_ACCESS_KEY_ID = 'AKIAJW4KELWD3KUPIPBQ'
    AWS_SECRET_ACCESS_KEY = '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'
    SERVICE_NAME = 'AWSMechanicalTurkRequester'
    SERVICE_VERSION = '2011-10-01'
    SERVICE_URL = 'https://mechanicalturk.amazonaws.com/onca/xml?' # production
    HIT_TYPE_SENTENCE_CLASSIFY='25AOVR14IXKO5KN4UD3WH6X3YPH98O' # production
    HIT_TYPE_WRITE_QUESTION='3BH55VSCCHEA2IOOOIFIL67IKT6JBU' # production
    HIT_TYPE_WRITE_FIB_QUESTION='30FN99Y3EUYXXO2D8UGYA2W3J7447J' # production
    #SERVICE_URL='https://mechanicalturk.sandbox.amazonaws.com' # sandbox
    #HIT_TYPE_SENTENCE_CLASSIFY='34PM2WU5W9DMHW29Q9MGHPXSESVRAI' # sandbox
    #HIT_TYPE_WRITE_QUESTION='3XA69K8C5XNVV46VTK3TTNC62D51W8' # sandbox
    #HIT_TYPE_WRITE_FIB_QUESTION='35EE6WR8LG2G5P5ULCVH17DP9M617G' # sandbox
    #HIT_TYPE_WRITE_CORRECT_ANSWER='2P1MQU6L5OBVFHFTAWVAPJF7GV9EXE'
    #HIT_TYPE_WRITE_WRONG_ANSWER='26LI2KYEPLSPA4YNZ5NJAOAHQF2OU4'
        
        
    def ApproveRejectedAssignment(self,AssignmentId,RequesterFeedback=None):
        operation = 'ApproveRejectedAssignment'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'AssignmentId':AssignmentId
        }
        
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return False
        
        node = result_xml.getElementsByTagName('ApproveRejectedAssignmentResult')
        if node:
            isvalid=node[0].getElementsByTagName('Request')[0].getElementsByTagName('IsValid')[0].childNodes[0].data
            if isvalid=='True':
                return True
        
        return False
    def DisposeHIT(self,HITId):
        # Calculate the request authentication parameters
        operation = 'DisposeHIT'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'HITId':HITId
        }
        
        # Make the request
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        # Check for and print results and errors
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return False
        
        node = result_xml.getElementsByTagName('DisposeHITResult')
        if node:
            isvalid=node[0].getElementsByTagName('Request')[0].getElementsByTagName('IsValid')[0].childNodes[0].data
            if isvalid=='True':
                return True
        
        return False
    
    def RegisterHITType(self,Title,Description,Reward,AssignmentDurationInSeconds,Keywords):
        operation = 'RegisterHITType'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        
        #http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_QualificationRequirementDataStructureArticle.html
        
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'Title':Title,
            'Description':Description,
            'Reward.1.Amount':Reward,
            'Reward.1.CurrencyCode':'USD',
            'AssignmentDurationInSeconds':AssignmentDurationInSeconds,
            'Keywords':Keywords,
            'QualificationRequirement.1.QualificationTypeId':'00000000000000000040',
            'QualificationRequirement.1.Comparator':'GreaterThan',
            'QualificationRequirement.1.IntegerValue':100,
            'QualificationRequirement.2.QualificationTypeId':'000000000000000000L0',
            'QualificationRequirement.2.Comparator':'GreaterThan',
            'QualificationRequirement.2.IntegerValue':95,
        }
        
        # Make the request
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        # Check for and print results and errors
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return False
        
        RegisterHITTypeResult = result_xml.getElementsByTagName('RegisterHITTypeResult')
        if RegisterHITTypeResult:
            return RegisterHITTypeResult[0].getElementsByTagName('HITTypeId')[0].childNodes[0].data
        else:
            return None 
            
    # Define authentication routines
    def generate_timestamp(self,gmtime):
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", gmtime)
    
    def generate_signature(self,service, operation, timestamp, secret_access_key):
        my_sha_hmac = hmac.new(secret_access_key, service + operation + timestamp, sha)
        my_b64_hmac_digest = base64.encodestring(my_sha_hmac.digest()).strip()
        return my_b64_hmac_digest
    
    def getAccountBalance(self):
        # Calculate the request authentication parameters
        operation = 'GetAccountBalance'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
        }
        
        # Make the request
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return 0 
        availbalance_nodes = result_xml.getElementsByTagName('AvailableBalance')
        if availbalance_nodes:
            amount=float(availbalance_nodes[0].getElementsByTagName('Amount')[0].childNodes[0].data)
            return amount
        else:
            return 0
    
    def createHit(self,title,description,question,reward,AssignmentDurationInSeconds,LifetimeInSeconds,Keywords,MaxAssignments,QualificationRequirement,HITTypeId):
        # Calculate the request authentication parameters
        operation = 'CreateHIT'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'Title':title,
            'Description':description,
            #'Question':'<![CDATA['+question+']]>',
            'Question':question,
            'Reward.1.Amount':reward,
            'Reward.1.CurrencyCode':'USD',
            'AssignmentDurationInSeconds':AssignmentDurationInSeconds,
            'LifetimeInSeconds':LifetimeInSeconds,
            'Keywords':Keywords,
            'MaxAssignments':MaxAssignments,
            'QualificationRequirement.1.QualificationTypeId':'00000000000000000040',
            'QualificationRequirement.1.Comparator':'GreaterThan',
            'QualificationRequirement.1.IntegerValue':5,
            'HITTypeId':HITTypeId
        }
        
        # Make the request
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        #TODO: verify that the hit actually got created 
        
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return False
        return True
   
        
    def classify_sentences(self,sentences):
        # create hits which ask the worker to determine of the given sentence is a complete declarative sentence
        for sentence in sentences:
            question="""\
            <QuestionForm xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd">
            <Question>
            <QuestionIdentifier>%s</QuestionIdentifier>
            <DisplayName>Is the Sentence Declarative?</DisplayName>
            <IsRequired>true</IsRequired>
            <QuestionContent>
            <Title>Read the phrase below and answer yes if it is declarative and is reasonably well formed English. (See http://en.wikipedia.org/wiki/Declarative_sentence#By_purpose )</Title>
            <Text><![CDATA[%s]]></Text>
            </QuestionContent>
            <AnswerSpecification>
            <SelectionAnswer>
            <StyleSuggestion>radiobutton</StyleSuggestion>
            <Selections>
              <Selection>
                <SelectionIdentifier>yes</SelectionIdentifier>
                <Text>Yes</Text>
              </Selection>
              <Selection>
                <SelectionIdentifier>no</SelectionIdentifier>
                <Text>No</Text>
              </Selection>
            </Selections>  
            </SelectionAnswer>
            </AnswerSpecification>
            </Question>
            </QuestionForm>
            """ % (sentence.signature,sentence.sentence)
            
            title="Is This Sentence Declarative?"
            description="Read an English sentence and answer yes if the sentence is complete and declares information"
            reward=0.05
            AssignmentDurationInSeconds=30
            LifetimeInSeconds=86400*2
            Keywords="English Grammar"
            MaxAssignments=1
            QualificationRequirement=None
            self.createHit(title, description, question, reward, AssignmentDurationInSeconds, LifetimeInSeconds, Keywords, MaxAssignments, QualificationRequirement,self.HIT_TYPE_SENTENCE_CLASSIFY)
            sentence.status=1 # mark the sentence as being processed so that we dont process it twice
            sentence.updated=datetime.datetime.now()
            sentence.save()
        
        #publish the hits
        return True

    def create_question(self,sentence,price,categories):
        title="Rewrite a sentence in the form of a question"
        description="Rewrite an English sentence in the form of a question."

        tags=[]
        for category in categories:
            tags.append(category.name)
        
        question="""\
<HTMLQuestion xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd\">
  <HTMLContent><![CDATA[
<!DOCTYPE html>
<html>
 <head>
  <meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
  <script type='text/javascript' src='https://s3.amazonaws.com/mturk-public/externalHIT_v1.js'></script>
 </head>
 <body>
 <form name='mturk_form' method='post' id='mturk_form' action='https://www.mturk.com/mturk/externalSubmit'>
  <input type='hidden' value='' name='assignmentId' id='assignmentId'/>
<ol>
  <li>Rewrite the sentence in the form of a quiz question. Try to write the question so that it asks about the most relevant fact in the sentence.</li>
        <li>Write the answer to the question. Try to keep the answer as short as possible and please try to avoid using either 'yes' or 'no' as answers.</li>
        <li>If the sentence is not able to be effectively rewritten as a question then just mark the checkbox below and submit the HIT</li>
</ol>
  <p>The Sentence: <b>%s</b></p>
  <p>Categories: %s</p>
  <p>Rewrite the sentence as a question here:<br><textarea name='question' cols='80' rows='3'></textarea></p>
  <p>Write the answer to the question here:<br><input type='text' name='answer' size='64'></p>
  <p><input type='submit' id='submitButton' value='Submit' /></p>
  <input type='hidden' name='question_identifier' value='%s'>
<p><input type='checkbox' name='cant_rewrite'>This sentence is not able to be effectively rewritten as a question.</p>
 </form>
  <script language='Javascript'>turkSetAssignmentID();</script>
 </body>
</html>
]]>
  </HTMLContent>
  <FrameHeight>450</FrameHeight>
</HTMLQuestion>
""" % (sentence.sentence,' | '.join(tags),sentence.signature)
        
        
        #logging.info(question)
        #return True
        
        AssignmentDurationInSeconds=3*60
        LifetimeInSeconds=86400*2
        Keywords="English Writing Question"
        MaxAssignments=1
        QualificationRequirement=None
        self.createHit(title, description, question, price, AssignmentDurationInSeconds, LifetimeInSeconds, Keywords, MaxAssignments, QualificationRequirement,self.HIT_TYPE_WRITE_QUESTION)
        
        return True

    def create_fib_question(self,sentence,price,categories,previous_sentence,following_sentence):
        title="Write a quiz question"
        description="Rewrite an English sentence in the form of a 'fill in the blank' question."
        
        if not previous_sentence:
            previous_sentence=""
        if not following_sentence:
            following_sentence=""
        if not sentence:
            logging.error("sentence is empty")
            return False
        tags=[]
        for category in categories:
            tags.append(category.name)
        
        question="""\
<HTMLQuestion xmlns=\"http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2011-11-11/HTMLQuestion.xsd\">
  <HTMLContent><![CDATA[
<!DOCTYPE html>
<html>
 <head>
  <meta http-equiv='Content-Type' content='text/html; charset=UTF-8'/>
  <script type='text/javascript' src='https://s3.amazonaws.com/mturk-public/externalHIT_v1.js'></script>
 </head>
 <body>
 <form name='mturk_form' method='post' id='mturk_form' action='https://www.mturk.com/mturk/externalSubmit'>
  <input type='hidden' value='' name='assignmentId' id='assignmentId'/>
<ol>
  <li>Read the sentence in the box below and determine which word should be turned into a blank in order to make it a good question. Simply replace the word or words with at least two underscores.</li>
  <li>For example, the sentence: 'Mechanical Turk gives businesses and developers access to an on-demand, scalable workforce' would be rewritten like this: 'Mechanical __ gives businesses and developers access to an on-demand, scalable workforce' In this example the word 'Turk' was replaced with underscores. (use at least two underscores to make a blank.) </li>
  <li>If the sentence is not able to be effectively rewritten as a question then just mark the checkbox below and submit the HIT</li>
</ol>
  %s<br>
  <textarea name='question' cols='80' rows='3'>%s</textarea><br>
  %s<br>
  <p><input type='submit' id='submitButton' value='Submit' /></p>
  <input type='hidden' name='question_identifier' value='%s'>
<p><input type='checkbox' name='cant_rewrite'>This sentence is not able to be effectively rewritten as a 'fill in the blank' question.</p>
 </form>
  <script language='Javascript'>turkSetAssignmentID();</script>
 </body>
</html>
]]>
  </HTMLContent>
  <FrameHeight>450</FrameHeight>
</HTMLQuestion>
""" % (previous_sentence.encode('ascii', 'xmlcharrefreplace'),sentence.sentence.encode('ascii', 'xmlcharrefreplace'),following_sentence.encode('ascii', 'xmlcharrefreplace'),sentence.signature)
        
        
        #logging.info(question)
        #return True
        
        AssignmentDurationInSeconds=3*60
        LifetimeInSeconds=86400*2
        Keywords="Quiz Question"
        MaxAssignments=1
        QualificationRequirement=None
       
        self.createHit(title, description, question, price, AssignmentDurationInSeconds, LifetimeInSeconds, Keywords, MaxAssignments, QualificationRequirement,self.HIT_TYPE_WRITE_FIB_QUESTION)
        
        return True

    def create_question_correct_answer(self,question,price):
        # create hits which ask the worker to determine of the given sentence is a complete declarative sentence
        title="Extract the answer to a question from a given sentence"
        description="Read the question and extract the answer from the given sentence."
        sentences=SentenceModel.get(question.sentences)
        if not sentences:
            logging.error("no sentences found!")
            return None
        
        text="Question: "+question.question+"\n (The answer to the question MUST be extracted from the following sentence): "
        for sentence in sentences:
            text=text+sentence.sentence+" "
        question="""\
        <QuestionForm xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd">
        <Question>
        <QuestionIdentifier>%s</QuestionIdentifier>
        <DisplayName>%s</DisplayName>
        <IsRequired>true</IsRequired>
        <QuestionContent>
        <Title>%s</Title>
        <Text><![CDATA[%s]]></Text>
        </QuestionContent>
        <AnswerSpecification>
        <FreeTextAnswer>
        </FreeTextAnswer>
        </AnswerSpecification>
        </Question>
        </QuestionForm>
        """ % (question.signature,title,description,text)
        
        logging.info(question)
        AssignmentDurationInSeconds=60*20
        LifetimeInSeconds=86400*2
        Keywords="English Writing Question"
        MaxAssignments=1
        QualificationRequirement=None
        self.createHit(title, description, question, price, AssignmentDurationInSeconds, LifetimeInSeconds, Keywords, MaxAssignments, QualificationRequirement,self.HIT_TYPE_WRITE_CORRECT_ANSWER)
        
        return True


    def create_question_wrong_answer(self,question,price):
        Title="Write a wrong answer for a quiz question"
        Description="Read a question and answer, then write another answer to the question that is wrong."
        sentences=SentenceModel.get(question.sentences)
        if not sentences:
            logging.error("no sentences found!")
            return None
        
        text="Question: "+question.question+"\n"
        text=text+"Correct Answer: "+question.correct_answer.answer+"\n"
        i=1
        for wanswer in question.wrong_answers:
            answer=AnswerModel.get(wanswer)
            if not answer:
                logging.error("wrong answer not found for question "+question.signature)
                return False
            text+="Wrong answer "+str(i)+": "+answer.answer
            i=i+1
    
        text+="Wrong answer "+str(i)+": ???"
        

        text=text+"\n\nYou can use the following sentence to base your wrong answer on: \""
        for sentence in sentences:
            text=text+sentence.sentence;
            text=text+"\"\n"
            
        text=text+"You may also use this wiki page to read more about the topic related to the question: "+sentence.wiki.url

        question="""\
        <QuestionForm xmlns="http://mechanicalturk.amazonaws.com/AWSMechanicalTurkDataSchemas/2005-10-01/QuestionForm.xsd">
        <Question>
        <QuestionIdentifier>%s</QuestionIdentifier>
        <DisplayName>%s</DisplayName>
        <IsRequired>true</IsRequired>
        <QuestionContent>
        <Title>%s</Title>
        <Text><![CDATA[%s]]></Text>
        </QuestionContent>
        <AnswerSpecification>
        <FreeTextAnswer>
        </FreeTextAnswer>
        </AnswerSpecification>
        </Question>
        </QuestionForm>
        """ % (question.signature,Title,Description,text)
        
        logging.info(question)
        AssignmentDurationInSeconds=60*20
        LifetimeInSeconds=86400*2
        Keywords="English Writing Quiz Answer"
        MaxAssignments=1
        QualificationRequirement=None
        self.createHit(Title, Description, question, price, AssignmentDurationInSeconds, LifetimeInSeconds, Keywords, MaxAssignments, QualificationRequirement,self.HIT_TYPE_WRITE_WRONG_ANSWER)
        
        return True
    
    def GetReviewingHITs(self,HITTypeId=None,page=1,pagesize=20):
        return self.GetReviewableHITs(HITTypeId, page, pagesize,'Reviewing')
    
    """
    http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_GetReviewableHITsOperation.html
    """
    def GetReviewableHITs(self,HITTypeId=None,page=1,pagesize=20,status='Reviewable'):
        hits=[]
        operation = 'GetReviewableHITs'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'Status':status,
            'PageSize':pagesize,
            'PageNumber':page
        }
        
        if HITTypeId:
            parameters['HITTypeId']=HITTypeId
        
        # Make the request
       
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return hits
        
        # get NumResults
        element=result_xml.getElementsByTagName('NumResults')
        NumResults=0
        if element:
            NumResults=element[0].childNodes[0].data
            #logging.info("NumResults="+str(NumResults))
        else:
            logging.info("Unexpected response format")
            return False
        
        if int(NumResults)==0:
            return hits
        
        # get TotalNumResults
        element=result_xml.getElementsByTagName('TotalNumResults')
        if element:
            TotalNumResults=element[0].childNodes[0].data
            #logging.info("TotalNumResults="+str(TotalNumResults))
        else:
            logging.info("Unexpected response format")
            return False
        
        # get PageNumber
        element=result_xml.getElementsByTagName('PageNumber')
        if element:
            PageNumber=element[0].childNodes[0].data
            #logging.info("PageNumber="+str(PageNumber))
        else:
            logging.error("Unexpected response format")
            return False
        
        #iterate over each hit
        hits_nodes=result_xml.getElementsByTagName('HIT')
        if not hits_nodes:
            logging.error("Unexpected response format")
            return False
        for hit_node in hits_nodes:
            element=hit_node.getElementsByTagName('HITId')
            if not element:
                logging.error("Unexpected response format")
                return False
            hit_id=element[0].childNodes[0].data
            hits.append(hit_id)
            
        return hits
    
    def GetHIT(self,hit_id ):
        operation = 'GetHIT'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'HITId':hit_id
        }
        
        # Make the request
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
       
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return False
        # get HITReviewStatus
        element=result_xml.getElementsByTagName('HITReviewStatus')
        if element:
            HITReviewStatus=element[0].childNodes[0].data
            #logging.info("HITReviewStatus="+str(HITReviewStatus))
        else:
            logging.error("Unexpected response format")
            return False
    
        return True
 
    """
    http://docs.aws.amazon.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_SetHITAsReviewingOperation.html
    """
    def SetHITAsReviewing(self,hit_id):
        operation = 'SetHITAsReviewing'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'HITId':hit_id,
            'Revert':False
        }
        
        # Make the request
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
       
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return False
       
          
        return True
    
    def getXmlResponseErrors(self,result_xml):
        errors=[]
        errors_nodes = result_xml.getElementsByTagName('Errors')
        if errors_nodes:
            for errors_node in errors_nodes:
                for error_node in errors_node.getElementsByTagName('Error'):
                    errors.append(error_node.getElementsByTagName('Code')[0].childNodes[0].data+':'+error_node.getElementsByTagName('Message')[0].childNodes[0].data)
        return errors
    
  
    def getQuestionHit(self,hit_id):
        operation = 'GetAssignmentsForHIT'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        Question=None
        Answer=None
        AssignmentId=None
        cant_rewrite=None
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'HITId':hit_id
        }
        
        # Make the request
        #TODO: use urlfetch instead of urlopen
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
       
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return (AssignmentId,Question,Answer,signature,cant_rewrite)
        record={}
        
        elements = result_xml.getElementsByTagName('AssignmentId')
        AssignmentId=elements.item(0).childNodes[0].data
        
        elements = result_xml.getElementsByTagName('WorkerId')
        WorkerId=elements.item(0).childNodes[0].data

        biganswer=result_xml.getElementsByTagName('Answer')
        answerxml=biganswer.item(0).childNodes[0].data
        
        result_xml = xml.dom.minidom.parseString(answerxml)
        answers=result_xml.getElementsByTagName('Answer')
         
        for answer in answers:
            qi=answer.getElementsByTagName('QuestionIdentifier')
            if qi and qi.item(0) and qi.item(0).childNodes:
                fieldname= qi.item(0).childNodes[0].data
                ft=answer.getElementsByTagName('FreeText')
                if ft and ft.item(0) :
                    if ft.item(0).childNodes:
                        fieldvalue=ft.item(0).childNodes[0].data
                        record[fieldname]=fieldvalue
                else:
                    logging.error( "unexpected xml format")
    
            else:
                logging.error( "unexpected xml format")
                
                
        if not record.has_key('question_identifier'):
            logging.error( "unable to get the question identifier from the xml")
            return (AssignmentId,WorkerId,Question,Answer,signature,cant_rewrite)
        
        if record.has_key('cant_rewrite') and record['cant_rewrite']=='on':
            return (AssignmentId,WorkerId,Question,Answer,record['question_identifier'],True)
            
        if not record.has_key('question'):
            logging.error( "unable to get the question from the xml")
            return (AssignmentId,WorkerId,Question,Answer,signature,cant_rewrite)
        if not record.has_key('answer'):
            logging.error( "unable to get the answer from the xml")
            return (AssignmentId,WorkerId,Question,Answer,signature,cant_rewrite)
        
        
        if not record.has_key('cant_rewrite'):
            record['cant_rewrite']=False
        
        
        return (AssignmentId,WorkerId,record['question'],record['answer'],record['question_identifier'],record['cant_rewrite'])
    
    def getFibQuestionHit(self,hit_id):
        operation = 'GetAssignmentsForHIT'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        Question=None
        Answer=None
        AssignmentId=None
        cant_rewrite=None
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'HITId':hit_id
        }
        
        # Make the request
        #TODO: use urlfetch instead of urlopen
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return (AssignmentId,Question,Answer,signature,cant_rewrite)
        record={}
        
        elements = result_xml.getElementsByTagName('AssignmentId')
        AssignmentId=elements.item(0).childNodes[0].data
        
        elements = result_xml.getElementsByTagName('WorkerId')
        WorkerId=elements.item(0).childNodes[0].data

        biganswer=result_xml.getElementsByTagName('Answer')
        answerxml=biganswer.item(0).childNodes[0].data
        
        result_xml = xml.dom.minidom.parseString(answerxml)
        answers=result_xml.getElementsByTagName('Answer')
         
        for answer in answers:
            qi=answer.getElementsByTagName('QuestionIdentifier')
            if qi and qi.item(0) and qi.item(0).childNodes:
                fieldname= qi.item(0).childNodes[0].data
                ft=answer.getElementsByTagName('FreeText')
                if ft and ft.item(0) :
                    if ft.item(0).childNodes:
                        fieldvalue=ft.item(0).childNodes[0].data
                        record[fieldname]=fieldvalue
                else:
                    logging.error( "unexpected xml format")
    
            else:
                logging.error( "unexpected xml format")
                
                
        if not record.has_key('question_identifier'):
            logging.error( "unable to get the question identifier from the xml")
            return (AssignmentId,WorkerId,Question,Answer,signature,cant_rewrite)
        
        if record.has_key('cant_rewrite') and record['cant_rewrite']=='on':
            return (AssignmentId,WorkerId,Question,Answer,record['question_identifier'],True)
            
        if not record.has_key('question'):
            logging.error( "unable to get the question from the xml")
            return (AssignmentId,WorkerId,Question,Answer,signature,cant_rewrite)
        
        if not record.has_key('cant_rewrite'):
            record['cant_rewrite']=False
        
        import re
        record['question']=re.sub('\s{2,}', ' ', record['question']).strip().replace("\n"," ").replace("\r"," ")
        return (AssignmentId,WorkerId,record['question'],None,record['question_identifier'],record['cant_rewrite'])
    
    def getSentenceHit(self,hit_id):
        operation = 'GetAssignmentsForHIT'
        timestamp = self.generate_timestamp(time.gmtime())
        aws_signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        turk_answer=None
        assignmentId=None
        signature=None
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': aws_signature,
            'Operation': operation,
            'HITId':hit_id
        }
        
        # Make the request
        
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
       
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
        
                return (assignmentId,None,turk_answer,signature)
        
        
        elements = result_xml.getElementsByTagName('AssignmentId')
        assignmentId=elements.item(0).childNodes[0].data
        
        elements = result_xml.getElementsByTagName('WorkerId')
        WorkerId=elements.item(0).childNodes[0].data
        
        biganswer=result_xml.getElementsByTagName('Answer')
        answerxml=biganswer.item(0).childNodes[0].data
        
        result_xml = xml.dom.minidom.parseString(answerxml)
        answers=result_xml.getElementsByTagName('Answer')
        
        for answer in answers:
            element=answer.getElementsByTagName('QuestionIdentifier')
            if element and element.item(0) and element.item(0).childNodes:
                signature= element.item(0).childNodes[0].data
                element=answer.getElementsByTagName('SelectionIdentifier')
                if element and element.item(0) and element.item(0).childNodes:
                    turk_answer= element.item(0).childNodes[0].data
                    
                else:
                    logging.error( "unexpected xml format")
            
            else:
                logging.error( "unexpected xml format")
            
       
        return (assignmentId,WorkerId,turk_answer,signature)
        
    def GetAssignmentIdForHIT(self,hit_id):
        operation = 'GetAssignmentsForHIT'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        AssignmentId=None
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'HITId':hit_id
        }
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return AssignmentId
                
        element=result_xml.getElementsByTagName('AssignmentId')
        if element:
            AssignmentId=element[0].childNodes[0].data
        else:
            logging.error("Unexpected response format")
            
        return AssignmentId
    
    """
    http://docs.amazonwebservices.com/AWSMechTurk/latest/AWSMturkAPI/ApiReference_GetAssignmentsForHITOperation.html
    """
    def GetAssignmentsForHIT(self,hit_id):
        operation = 'GetAssignmentsForHIT'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        Answer=None
        AssignmentId=None
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'HITId':hit_id
        }
        
        # Make the request
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return (AssignmentId,Answer,signature)
        
         # get AssignmentId
        AssignmentId=None
        element=result_xml.getElementsByTagName('AssignmentId')
        if element:
            AssignmentId=element[0].childNodes[0].data
        else:
            logging.error("Unexpected response format")
        
       
            
    
        return (AssignmentId,Answer,signature)
    
    def ApproveAssignment(self,AssignmentId):
        operation = 'ApproveAssignment'
        timestamp = self.generate_timestamp(time.gmtime())
        signature = self.generate_signature('AWSMechanicalTurkRequester', operation, timestamp, self.AWS_SECRET_ACCESS_KEY)
        
        # Construct the request
        parameters = {
            'Service': self.SERVICE_NAME,
            'Version': self.SERVICE_VERSION,
            'AWSAccessKeyId': self.AWS_ACCESS_KEY_ID,
            'Timestamp': timestamp,
            'Signature': signature,
            'Operation': operation,
            'AssignmentId':AssignmentId
        }
        
        # Make the request
        #result_xmlstr = urllib2.urlopen(self.SERVICE_URL, urllib.urlencode(parameters)).read()
        result_xmlstr=urlfetch.fetch( self.SERVICE_URL, urllib.urlencode(parameters), urlfetch.POST ).content
        result_xml = xml.dom.minidom.parseString(result_xmlstr)
        
        # Check for and print results and errors
        errors=self.getXmlResponseErrors(result_xml)
        if errors:
            for error in errors:
                logging.error(error)
            return False
        return True
    
    def remove_old_approved_hits(self):
        num_hits=0
        page=1
        hit_ids=self.GetReviewingHITs(None,page)
        while hit_ids:
            for hit_id in hit_ids:
                assignment_id=self.GetAssignmentIdForHIT(hit_id)
                if assignment_id: 
                    self.DisposeHIT(hit_id)
                    num_hits=num_hits+1
                
            page=page+1
            hit_ids=self.GetReviewableHITs(None,page)
            
        return num_hits
    """
    Given a sentence, returns the main subject of the sentence
    """
    def get_main_subject(self,sentence):
        
        subject="Japan"
        return subject
    
    """
    if the main subject was determined, then set the sentence as declarative
    """
    def get_main_subject_hits(self,sentence):
        
        num_hits=0
        return num_hits