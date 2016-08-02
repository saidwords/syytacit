from google.appengine.ext import db

class UserProperties(db.Model):
    username=db.StringProperty(required=True)
    roles=db.StringListProperty()
    
    def addRole(self,role):
        if role not in self.roles:
            self.roles.append(role)
            self.save()