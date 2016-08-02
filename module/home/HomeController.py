# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from common.lib.KnowledgeLib import KnowledgeLib
from common.lib.Session import Session
from module.article.lib.ArticleLib import ArticleLib
from module.article.model.SparseQuestion import SparseQuestion
from module.home.model.HomeModel import HomeModel
from module.home.view.AboutView import AboutView
from module.home.view.HomeView import HomeView
from module.question.lib.QuestionLib import QuestionLib
from module.home.view.FourzerofourView import FourzerofourView
import datetime
from common.lib.DateLib import DateLib
from module.home.view.MaintenanceView import MaintenanceView

class HomeController(Controller):
    def maintenanceAction(self):
        self.error(503)
        model={"message":"Exceeded budget","eta":None,"metakeywords":"offline","metadescription":"website is offline for maintenance"}
        start_date_of_maintenace=datetime.datetime(2014,6,25,7,37,00)
        model['eta']=DateLib.humanizeTimeDiff(start_date_of_maintenace-datetime.timedelta(days=-1))
        
        return MaintenanceView(model)
    
    def defaultAction(self,page=1,category=None):
        return self.articlesAction(page, category)
    
    def fourzerofourAction(self):
        model={'user':self.user}
        
        self.error(404)
        
        return FourzerofourView(model)
    
    def indexAction(self,page=1,category=None):
        return self.articlesAction(page, category)
    
    def aboutAction(self):
        model={"user":self.user,"metakeywords":'about','metadescription':'About Syytacit','page_subtitle':'About'}
       
        return AboutView(model)
    
    def newAction(self,page=1,category=None):
        model=HomeModel()
        model.base_url='/articles/new'
        try:
            model.page=int(page)
        except ValueError:
            model.page=1

        if model.page<1:
            model.page=1
            
        model.community=category
        model.user=self.user
        
        model.page_subtitle='New Articles'
            
        model.articles=ArticleLib.getLatestNews(model.page,category)
        
        self.loadModel(model)
        model.sticky_articles=[]
        return HomeView(model)
    
    def articlesAction(self,page=1,category=None):
        model=HomeModel()
        
        try:
            model.page=int(page)
        except ValueError:
            model.page=1

        if model.page<1:
            model.page=1
        
        model.community=category
        model.category=category
        model.page_subtitle='merit based news and articles'
        model.base_url=''
        
        #logging.info("Remember to turn cache back on for ArticleLib.new_getTopNews")
        model.articles=ArticleLib.new_getTopNews(model.page,category)
        model.sticky_articles=[]
        if model.page==1:
            sticky_article=ArticleLib.getArticleBy("ihref","syytacit-feedback-post")
            if sticky_article:
                model.sticky_articles.append(sticky_article)
            
        self.loadModel(model)
        
        return HomeView(model)
   
    def loadModel(self,model):
        model.user=self.user
        
        model.metadescription='merit based news and articles'
        if model.category:
            model.metadescription=model.metadescription+" about "+model.category
            model.metakeywords=model.category+","+model.metakeywords
            model.page_subtitle=model.page_subtitle+' about '+model.category
            
        if model.page>1:
            model.metadescription=model.metadescription+' - page '+str(model.page)
            model.metakeywords=model.metakeywords+',page '+str(model.page)
            if model.page_subtitle:
                model.page_subtitle=model.page_subtitle+" - "
            model.page_subtitle=model.page_subtitle+'Page '+str(model.page)
        
        
        allcats={}
        i=0
        for article in model.articles:
            #cats=CategoryModel.get(article.cats)
            model.articles[i].tags=[]
            model.articles[i].usercats=[]
            model.articles[i].usercatscore=[]
            model.articles[i].approved=None
                
            if self.user:
                approved=ArticleLib.getApproval(model.articles[i],model.user) 
                if approved==True:
                    model.articles[i].approved='1'
                elif approved==False:
                    model.articles[i].approved='0'
                else:
                    model.articles[i].approved=None
                
            acats=ArticleLib.getCategories(article)
            stlen=0;
            for acat in acats:
                stlen=len(acat.name)+stlen
                if stlen < 64:
                    model.articles[i].tags.append(acat.name)
                    if not allcats.has_key(acat.name):
                        allcats[acat.name]=acat
            question=QuestionLib.getRandomQuestion( model.articles[i].tags)
            
            if question:
                if self.user:
                    signature=QuestionLib.getSignature(question.key().id(),Session.sessionid)
                else:
                    signature=None
                if question.question_type==1:
                    question_text=QuestionLib.toArray(question.question)
                else:
                    question_text=question.question
                model.articles[i].question=SparseQuestion(question_type=question.question_type,id=question.key().id(),question=question_text,signature=signature)
            else:
                model.articles[i].question=SparseQuestion()
            i=i+1
            
        #(model.leaderboard,model.userstats,model.greater_userstats,model.lesser_userstats)=HomeController.getLeaderBoard(self.user,model.page,allcats.values())
        cats=allcats.values()
        #cats.append(CategoryModel.all().filter("name =","computing").get())
        model.leaderboard=KnowledgeLib.getLeaderBoard(cats)
        model.userstats=KnowledgeLib.getUserStats(self.user,cats)
        model.lesser_userstats=KnowledgeLib.getRelativeUserStats(self.user,False,True,cats)
        model.greater_userstats=KnowledgeLib.getRelativeUserStats(self.user,True,False,cats)
        model.user.isadmin=self.isLoggedInAs('admin')
        
        if model.page>1:
            model.previouspage=model.base_url+'/'+str(model.page-1)
            if model.category:
                model.previouspage=model.previouspage+'/'+model.category
        if model.articles:
            model.nextpage=model.base_url+'/'+str(model.page+1)
            if model.category:
                model.nextpage=model.nextpage+'/'+model.category
        
        
        return model
    
    