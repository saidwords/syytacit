# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.home.HomeController import HomeController
from module.article.ArticleController import ArticleController

class ArticlesController(Controller):
    
    def defaultAction(self,page=1,category=None):
        return HomeController().articlesAction(page, category)
    
    def newAction(self,page=1,category=None):
        return HomeController().newAction(page,category)
    
    def topAction(self,page=1,category=None):
        return HomeController().articlesAction(page,category)
    
    def submitAction(self,community=None):
        return ArticleController().submitAction(community)
            