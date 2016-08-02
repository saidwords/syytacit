from google.appengine.ext import db
from module.comments.model.Comments import Comments

#from module.comments.model.Comments import Comments
    
#class ArticleModel(db.Model):
class ArticleModel(db.Model):
    id=db.StringProperty()
    title=db.StringProperty(required=True)
    subtitle=db.StringProperty()
    description=db.StringProperty()
    subdescription=db.StringProperty()
    updated=db.DateTimeProperty(auto_now_add=True)
    href=db.LinkProperty()
    ihref=db.StringProperty(required=True) # internal href
    authors=db.ListProperty(str)
    source=db.StringProperty()
    username=db.StringProperty() # the user that submitted the article
    comment=db.ReferenceProperty(Comments)
    signature=db.StringProperty()
    numcomments=db.IntegerProperty()
    numapprovals=db.IntegerProperty(default=0)
    archived=db.BooleanProperty(default=False)
    category=db.StringProperty(default=None)
    created=db.DateTimeProperty(auto_now_add=True)
    wilson = db.FloatProperty()
    r2=db.IntegerProperty(default=0)
    v2=db.IntegerProperty(default=1)