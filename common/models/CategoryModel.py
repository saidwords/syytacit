from google.appengine.ext import db

class CategoryModel(db.Model):
    name=db.StringProperty(required=True)
    wikiname=db.StringProperty()
    level=db.IntegerProperty(default=None)