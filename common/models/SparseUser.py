from webapp2_extras.appengine.auth.models import User

class SparseUser():
    
    username=None
    isadmin=False
        
    def __init__(self, user=None,properties=False):
        
        if user:
            
            typ=type(user).__name__
            if typ=='User':
                self.username=user.auth_ids[0]
            else:
                self.username=user['auth_ids'][0]
            if properties==True:
                fuser=User().get_by_auth_id(self.username)
                if fuser:
                    self.created=fuser.created
                    self.email_address=fuser.email_address
                    
    def getCreated(self):
        if self.username:
            user=User().get_by_auth_id(self.username)
            if user:
                return user.created
            
    def getEmail(self):
        
        if self.username:
            user=User().get_by_auth_id(self.username)
            if user:
                
                return user.email_address

        return False               
            
            