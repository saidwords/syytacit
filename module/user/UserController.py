# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from common.lib.DateLib import DateLib
from common.lib.KnowledgeLib import KnowledgeLib
from common.models.BaseModel import BaseModel
from common.models.Registrations import Registrations
from module.article.model.ArticleModel import ArticleModel
from module.comments.lib.CommentsLib import CommentsLib
from module.comments.model.Comments import Comments
from module.home.view.ComingSoonView import ComingSoonView
from module.user.model.UserHome import UserHome
from module.user.view.UserView import UserView
from webapp2_extras import auth
from webapp2_extras.appengine.auth.models import User
from common.lib.Users import Users
from common.models.SparseUser import SparseUser
from common.models.UserProperties import UserProperties
from module.user.view.UserPreferencesView import UserPreferencesView
from common.lib.CategoryLib import CategoryLib
from module.article.lib.ArticleLib import ArticleLib

class UserController(Controller):
    
    def indexAction(self,username=None):
        
        return self.defaultAction(username)
    
    def defaultAction(self,username=None):
        
        if not username:
            user=Users.get_current_user()
        else:
            user=User().get_by_auth_id(username)
            #user=User.all().filter("username =",username).get()
        
        model={"user1":user}
        if model["user1"]:
            return UserView(model)
        
        return model
    
    def signupAction(self,username,password,vpassword):
        
        #raise Exception('Sorry, signups are disabled while in beta mode. Please email us for access');
        
        model={"user":None}
        
        #try:
        model['user']=Users.signup(username,password)
        #except Exception as e:
        #    model['exception']=e 
             
        return UserView(model)
    
    def loginAction(self,username=None,password=None):
        
        model={"user":None}
        
        
        try:
            model["user"] = Users.login(username,password)
        except (auth.InvalidAuthIdError, auth.InvalidPasswordError) as e:
            self.error(403)
            raise e
            
        return UserView(model)
   
    
    def logoutAction(self):
         
        model={"user":None}
        Users.logout()
        
        return UserView(model)
    
    def registerAction(self,email=None,username=None):
        
        model=BaseModel()
        model.message="";
        
        if email and not username:
            registration=Registrations.all().filter("email =",email).get()
            if not registration:
                registration=Registrations(email=email)
                registration.save()
        
        model.email=email
        
               
        return ComingSoonView(model)
    
    def preferencesAction(self):
        model={"user":None,'user_date_established':None,'email_address':'','user_date_elapsed':None,'page_subtitle':'Preferences','metakeywords':'Preferences','metadescription':'Preferences'}
        
        model['user']=self.user
        
        if self.user:
            model['page_subtitle']=model['page_subtitle']+' for '+self.user.username
            model['metakeywords']=model['metakeywords']+','+self.user.username
            model['metadescription']=model['page_subtitle']
            model['user_date_established']=self.user.getCreated()
            model['email_address']=self.user.getEmail()
            if not model['email_address']:
                model['email_address']=''
            model['user_date_elapsed']=DateLib.humanizeTimeDiff(self.user.getCreated())
        
         
        return UserPreferencesView(model)
    
    """
    @param section - one of articles,comments,rejected_articles,approved_articles,rejected_comments,approved_comments,knowledge
    """
    def homeAction(self,username=None,section=None,page=1):
        
        model = UserHome()
        
        try:
            ipage = int(page)
            if ipage < 1:
                ipage = 1
        except ValueError:
            ipage = 1
        
        limit=10
        offset=(ipage-1)*limit
        
        model.nextpage=ipage+1
        model.prevpage=ipage-1
            
        if section==None:
            section='articles'
            
        model.section=section
        
        if username:
            u=User().get_by_auth_id(username)
            model.user1=SparseUser(u)
        else:
            u=Users.get_current_user()
            model.user1=u
            
        if model.user1 and model.user1.username:
            # if the logged in user is the same as the user being viewed then get the email address
            if self.user and self.user.username==model.user1.username:
                self.user.email_address=model.user1.getEmail()
           
            model.user_date_established=model.user1.getCreated()
            if not model.user1.getCreated():
                model.user_date_elapsed=""
            else:
                model.user_date_elapsed=DateLib.humanizeTimeDiff(model.user1.getCreated())
                
            model.numcomments=Users.getNumComments(username)
            model.numarticles=Users.getNumArticles(username)
            if section=='articles':
                model.metadescription='Articles Submitted By '+model.user1.username
                model.page_subtitle=model.metadescription
                model.metakeywords=model.user1.username+',articles'
       
                # get all articles submitted by the user
                model.articles=ArticleModel.all().filter("username =",model.user1.username).fetch(limit,offset)
                if not model.articles:
                    model.nextpage=None
                i=0
                for article in model.articles:
                    acats=ArticleLib.getCategories(article)
                    article.tags=[]
                    for acat in acats:
                        article.tags.append(acat.name)
                    """
                    if self.user and self.user.isloggedin:
                        approved=ArticleLib.getApproval(model.articles[i],self.user) 
                        if approved==True:
                            model.articles[i].approved='1'
                        elif approved==False:
                            model.articles[i].approved='0'
                        else:
                            model.articles[i].approved=None
                    """
                    i=i+1
                        
            if section=='knowledge':
                #model.categories=UserKnowledgeModel.all().filter("user =",user).order("-score").fetch(10,0)
                model.metadescription='Knowledge Stats for '+model.user1.username
                model.page_subtitle=model.metadescription
                model.metakeywords=model.user1.username+',knowledge'
                model.userknowledge=KnowledgeLib.getUserStats(model.user1,None,limit,offset)
                if not model.userknowledge:
                    model.nextpage=None
                # get all categorys that the user knows about                
                """
                maxscore=0
                minscore=99999
                for record in model.userknowledge:
                    if record.score > maxscore:
                        maxscore=record.score
                    if record.score < minscore:
                        minscore=record.score
                        
                for record in model.categories:
                    record.pct=math.ceil(((record.score-minscore)/(maxscore-minscore))*10000)/100
                """
            if section=='comments': 
                # get all comments made by the user
                model.metadescription='Comments Submitted By '+model.user1.username
                model.page_subtitle=model.metadescription
                model.metakeywords=model.user1.username+',comments'
                model.comments=Comments.all().filter("username =",model.user1.username).fetch(limit,offset)
                for comment in model.comments:
                    article_key=CommentsLib.getArticleKey(comment)
                    comment.article=ArticleModel.get(article_key)
                if not model.comments:
                    model.nextpage=None
                    
            if section=='rejected_articles':
                model.rejected_articles=[]
            if section=='approved_articles':
                model.approved_articles=[]
            if section=='rejected_comments':
                model.rejected_comments=[]
            if section=='approved_comments':
                model.approved_comments=[]
                
     
        model.user=self.user
        cat=CategoryLib.getByTag('sports')
        cats=[cat]
        model.leaderboard=KnowledgeLib.getLeaderBoard(cats)
        model.lesser_userstats=KnowledgeLib.getRelativeUserStats(self.user,False,True,cats)
        model.greater_userstats=KnowledgeLib.getRelativeUserStats(self.user,True,False,cats)
        
        return UserView(model)
    
    def set_emailAction(self,email):
        if self.user:
            current_email=self.user.getEmail()
            if current_email!=email:
                user=User().get_by_auth_id(self.user.username)
                user.email_address=email
                user.put()
                
        model={"email":email}
        return model 
    
    def add_roleAction(self,username,role):
        self.requireLoggedin('admin')
        
        user=User().get_by_auth_id(username)
        
        if not user:
            raise Exception('user '+username+' does not exist')
        
        model={"properties":None}
        model['properties']=UserProperties.all().filter("username =",username).get()
        if not  model['properties']:
            model['properties']=UserProperties(username=username)
             
        model['properties'].addRole(role)
         
        return model
             
         
    