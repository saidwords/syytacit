from google.appengine.ext import db

class MturkModel(db.Model):
    turk_id=db.StringProperty(required=True)