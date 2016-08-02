from google.appengine.ext import db
from common.models.AnswerModel import AnswerModel

class QuestionModel(db.Model):
    correct_answer = db.ReferenceProperty(AnswerModel,default=None)
    sentences = db.ListProperty(db.Key)
    question=db.StringProperty(required=True)
    question_type=db.IntegerProperty(default=0) #short answer=0,fillinblank=1,true/false=2,multiple choice=3
    updated=db.DateTimeProperty(auto_now_add=True)
    signature=db.StringProperty(required=True) #md5sum of the text 
    status=db.IntegerProperty(default=0) #unprocessed =0,unreviewed=1,accepted=2,rejected=3
    cats = db.ListProperty(db.Key)
    username=db.StringProperty()# the name of the user that created the question