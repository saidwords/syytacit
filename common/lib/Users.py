#from google.appengine.api import users
from webapp2_extras import auth
from webapp2_extras.appengine.auth.models import User
import logging
from google.appengine.api import memcache
from module.comments.model.Comments import Comments
from module.article.model.ArticleModel import ArticleModel
from common.models.UserKnowledgeModel import UserKnowledgeModel
from common.models.SparseUser import SparseUser
from webapp2_extras.auth import AuthError

class Users():
    
        
    def get_current_user(properties=False):
        user=auth.get_auth().get_user_by_session()
        
        return SparseUser(user)
    
    def signup(username,password,email_address=None):
        
        user=User.get_by_auth_id(username)
        if user:
            raise AuthError('Username already taken')
        
        user_data = User.create_user(username,email_address=email_address, password_raw=password,verified=False)
        
        if not user_data[0]:
            raise Exception('Unable to create user')
        else:
            
            return SparseUser(user_data[1])
        
    def login(username,password):
        user=auth.get_auth().get_user_by_password(username, password)
        #user1=User.get_by_auth_id(username)
        
        return SparseUser(user)
        
    def logout():
        auth.get_auth().unset_session()
             
    def createUserId(username):
        import binascii
        import datetime
        x= datetime.datetime.now()
        return hex(abs(binascii.crc32(username+str(x))))[2:].upper()
    
    def assertLoggedIn():
        if not Users.get_current_user():
            raise Exception("User is not logged in")
        return True
    
    def getUserKnowledge(username,category=None):
        if not username:
            return {}
        if category:
            mkey='getUserKnowledge_'+username+"_"+category.name
        else:
            mkey='getUserKnowledge_'+username
        knowledge=memcache.get(mkey)
        if knowledge:
            return knowledge
        
        knowledge={}
        if category:
            records=UserKnowledgeModel.all().filter("username =",username).filter("category =",category)
        else:
            records=UserKnowledgeModel.all().filter("username =",username)
        
        for record in records:
            if not knowledge.has_key(record.category.name):
                knowledge[record.category.name]=record
                
        memcache.set(mkey,knowledge)
        
        return knowledge
    
    def getNumComments(username):
        mkey='getNumComments'+str(username)
        data=memcache.get(mkey)
        logging.info("TODO: invalidate cache when a user makes a comment")
        if data:
            return data
        
        data=Comments.all().filter("username =",username).count()
        if not data:
            data=0
                
        memcache.set(mkey,data)
        return data
    
    def getNumArticles(username):
        mkey='getNumArticles'+str(username)
        data=memcache.get(mkey)
        if data:
            return data
        
        data=ArticleModel.all().filter("username =",username).count()
        if not data:
            data=0
                
        memcache.set(mkey,data)
        return data

    createUserId=staticmethod(createUserId)
    get_current_user=staticmethod(get_current_user)
    signup=staticmethod(signup)
    logout=staticmethod(logout)
    login=staticmethod(login)
    assertLoggedIn=staticmethod(assertLoggedIn)
    getUserKnowledge=staticmethod(getUserKnowledge)
    getNumComments=staticmethod(getNumComments)
    getNumArticles=staticmethod(getNumArticles)
    
    
        
        
        