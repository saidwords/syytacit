from google.appengine.ext import db
from common.models.CategoryModel import CategoryModel
from module.article.model.ArticleModel import ArticleModel

#from module.comments.model.Comments import Comments
    
class ArticleCategoryModel(db.Model):
    article = db.ReferenceProperty(ArticleModel,required=True)
    category = db.ReferenceProperty(CategoryModel,required=True,collection_name='article_category_set') 
    catscore=db.FloatProperty() # this should be a float between 0 and 1
    updated=db.DateTimeProperty(auto_now_add=True)
    sortkey=db.FloatProperty()
    usercategoryscore=db.FloatProperty() # this is for development only. It can be deleted once the algorithms are figured out.
    numcats=db.IntegerProperty() # the total number of categories that are tagged to this article. (useful for specificity)
    archived=db.BooleanProperty(default=False)
    rank=db.FloatProperty(default=0.0)
    v=db.FloatProperty(default=1.0)
    r2=db.IntegerProperty(default=0)
    v2=db.IntegerProperty(default=1)