from google.appengine.ext import db
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
from module.wiki.model.WikiModel import WikiModel


class MturkModel(db.Model):
    wiki=db.ReferenceProperty(WikiModel)
    category=db.ReferenceProperty(WikiCategoryModel)
    date_wiki_processed=db.DateTimeProperty()
    date_category_processed=db.DateTimeProperty()