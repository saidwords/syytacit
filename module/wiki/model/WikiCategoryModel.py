from google.appengine.ext import db

class WikiCategoryModel(db.Model):
    name=db.StringProperty(required=True)
    url=db.LinkProperty(required=True)
    categories = db.ListProperty(db.Key)
    parentcategory = db.SelfReferenceProperty()
    numsentences=db.IntegerProperty(default=0)
    date_updated=db.DateTimeProperty(auto_now=True)