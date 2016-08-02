from google.appengine.ext import db
from common.models.CategoryModel import CategoryModel
from module.comments.model.Comments import Comments
class CommentApproveModel(db.Model):
    comment=db.ReferenceProperty(Comments)
    username=db.StringProperty(required=True)
    category=db.ReferenceProperty(CategoryModel,required=True)
    score=db.FloatProperty(required=True)
    approve=db.BooleanProperty(default=True)