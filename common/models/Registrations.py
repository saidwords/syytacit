from google.appengine.ext import db
class Registrations(db.Model):
    email=db.EmailProperty(required=True)
    date_established=db.DateTimeProperty(auto_now_add=True)