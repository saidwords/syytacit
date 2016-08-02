from google.appengine.ext import db
class Comments(db.Model):
    parent_comment=db.SelfReference()
    text=db.StringProperty(required=True,multiline=True)
    username=db.StringProperty()
    rank=db.FloatProperty(default=0.0)
    updated=db.DateTimeProperty(auto_now_add=True)
    deleted=db.BooleanProperty(default=False)
