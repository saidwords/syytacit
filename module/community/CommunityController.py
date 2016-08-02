# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.home.HomeController import HomeController
from common.lib.CategoryLib import CategoryLib
from module.articles.ArticlesController import ArticlesController
from module.article.lib.ArticleLib import ArticleLib
from module.article.ArticleController import ArticleController
import logging
from module.category.CategoryController import CategoryController

class CommunityController(Controller):
    
    def defaultAction(self,category=None,action=None,page=1):
        
        if not category:
            return CategoryController().searchAction()
            
        c = CategoryLib.getByTag(category)
        
        if not c:
            return HomeController().fourzerofourAction()
        
        try:
            p=int(page)
            page=p
        except ValueError:
            return HomeController().fourzerofourAction()
        
        if action:
            if action=='new':
                logging.info("new! "+category)
                view= ArticlesController().newAction(p,category)
            else:
                try:
                    p=int(action)
                    page=p
                    view=ArticlesController().topAction(p, category)
                except ValueError:
                    # ation might be an article ihref
                    article=ArticleLib.getByIhref(action)
                    if article:
                        view=ArticleController().detailAction(action,p)
                    else:
                        logging.warn("article not found "+action)
                        return HomeController().fourzerofourAction()
        else:
            view=ArticlesController().topAction(p, category)
            
        if p>1:
            view.model.previouspage='/community'
            if category:
                view.model.previouspage=view.model.previouspage+'/'+category
            view.model.previouspage=view.model.previouspage+'/'
            if action:
                view.model.previouspage=view.model.previouspage+'/'+action
            view.model.previouspage=view.model.previouspage+'/'+str(p-1)
        else:
            view.model.previouspage=None
        
        if hasattr(view.model, 'articles') and view.model.articles:
            view.model.nextpage='/community'
            if category:
                view.model.nextpage=view.model.nextpage+'/'+category
            view.model.nextpage=view.model.nextpage
            if action:
                view.model.nextpage=view.model.nextpage+'/'+action
            
            view.model.nextpage=view.model.nextpage+'/'+str(p+1)
        else:
            view.model.nextpage=None
            
        if category:
                view.model.community=category
                
        view.model.sticky_articles=[]
        return view 
    
    def searchAction(self,terms=None,sort='alphabetical',sort_order='ascending',page=1):
        return CategoryController().searchAction(terms, sort, sort_order, page)
        
        