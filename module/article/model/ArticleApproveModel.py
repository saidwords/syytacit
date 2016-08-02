from google.appengine.ext import db
from common.models.CategoryModel import CategoryModel
from module.article.model.ArticleModel import ArticleModel

class ArticleApproveModel(db.Model):
    article=db.ReferenceProperty(ArticleModel,required=True)
    username=db.StringProperty(required=True)
    category=db.ReferenceProperty(CategoryModel,required=True)
    score=db.FloatProperty(required=True)
    approve=db.BooleanProperty(default=True)
    