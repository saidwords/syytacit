from google.appengine.ext import db

class WikiModel(db.Model):
    title=db.StringProperty(required=False)
    url=db.LinkProperty()
    rank=db.IntegerProperty()
    date_updated=db.DateTimeProperty(auto_now=True)
    categories = db.ListProperty(db.Key)
    numsentences=db.IntegerProperty(default=0)