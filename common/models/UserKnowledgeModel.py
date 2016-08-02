from google.appengine.ext import db
from common.models.CategoryModel import CategoryModel

"""
Stores the users strength of knowledge of a category
"""
class UserKnowledgeModel(db.Model):
    username=db.StringProperty(required=True)
    category=db.ReferenceProperty(CategoryModel,required=True)
    score=db.FloatProperty()
    pct=db.FloatProperty()
    updated=db.DateTimeProperty(auto_now_add=True)