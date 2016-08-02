from google.appengine.ext import db
from common.models.QuestionModel import QuestionModel

class UserAnswerModel(db.Model):
    question=db.ReferenceProperty(QuestionModel)
    username=db.StringProperty(required=True)
    iscorrect=db.BooleanProperty()
    updated=db.DateTimeProperty(auto_now_add=True) # the date when the answer was submitted
    topa=db.DateTimeProperty(auto_now_add=True)# the date at which the previous answer was submitted
    delay=db.IntegerProperty(default=3600) # how long in milliseconds it took the user to answer the question
    #leitner=db.IntegerProperty(default=0)
    
    