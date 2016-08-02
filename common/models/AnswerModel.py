from google.appengine.ext import db

class AnswerModel(db.Model):
    answer=db.StringProperty(required=True)
    iscorrect=db.BooleanProperty(default=False)
    updated=db.DateTimeProperty(auto_now_add=True)
    signature=db.StringProperty(required=True) # md5sum of the answer text
    status=db.IntegerProperty(default=0) #reviewed =0,accepted=1,rejected=2