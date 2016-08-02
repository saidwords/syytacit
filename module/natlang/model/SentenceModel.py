from google.appengine.ext import db
from module.wiki.model.WikiModel import WikiModel

class SentenceModel(db.Model):
    wiki=db.ReferenceProperty(WikiModel,collection_name='sentences')
    score=db.IntegerProperty(required=True)
    order=db.IntegerProperty()
    sentence=db.StringProperty(required=True)
    status=db.IntegerProperty(default=0) #unprocessed =0,processing=1,accepted=2,processing=3,accepted=4,rejected=5
    updated=db.DateTimeProperty(auto_now_add=True)
    signature=db.StringProperty(required=True)
    numenglishwords=db.IntegerProperty()
    numnonenglishwords=db.IntegerProperty()
    numquestions=db.IntegerProperty()
    type=db.IntegerProperty() #unknown=0,declarative=1,interrogative=2,imperative=3
    username=db.StringProperty()