# coding=UTF-8
# -*- coding: UTF-8 -*-
import logging

from google.appengine.api import taskqueue, memcache
from google.appengine.api.search import search

from common.lib.CategoryLib import CategoryLib
from common.lib.Controller import Controller
from common.lib.KnowledgeLib import KnowledgeLib
from common.models.CategoryModel import CategoryModel
from module.api.view.JSONView import JSONView
from module.article.lib.ArticleLib import ArticleLib
from module.article.model.ArticleCategoryModel import ArticleCategoryModel
from module.category.model.AdminCategoryModel import AdminCategoryModel
from module.category.model.CategoryHomeModel import CategoryHomeModel
from module.category.model.SearchCategoryModel import SearchCategoryModel
from module.category.view.AdminCategoryView import AdminCategoryView
from module.category.view.CategoryHomeView import CategoryHomeView
from module.category.view.SearchCategoryView import SearchCategoryView
from module.home.HomeController import HomeController
from module.home.view.NullView import NullView
from module.wiki.lib.WikiLib import WikiLib


class CategoryController(Controller):
    
    def set_category_levelAction(self,tag,level=0,leaf=None):
        model={"numcats":0}
        
        if level>32:
            logging.error("Too many levels deep! ("+str(leaf)+")")
            return model
        
        if tag==leaf:
            logging.info("Infinite loop")
            return model
        if leaf==None:
            leaf=tag
        
        logging.info(tag+":"+str(level))
        wikicategories=WikiLib.getPageCategories('Category:'+tag)
        
        for wikicat in wikicategories:
            if wikicat.name==WikiLib.ROOT_CATEGORY or wikicat.name==WikiLib.ROOT_CATEGORY2:
                logging.info("SUCCESS")
                cat=CategoryLib.getByWikiName(leaf)
                if cat:
                    cat.level=level
                    cat.save()
                
                else:
                    logging.error("category not found for "+leaf)
                    
                #TODO: set the level of leaf category to level
                return model
            
        if wikicategories:
            for wikicat in wikicategories:
        
                if wikicat.name in WikiLib.EXCLUDE_CATEGORIES:
                    continue
                model=self.set_category_levelAction(wikicat.name,level+1,leaf)
                break
                
        return model
    
    def set_category_level_method1Action(self,tag='Main_topic_classifications',level=0):
        model={"subcategories":[]}
        
        # the following code is to prevent infinite recursion
        semaphore=memcache.get('set_category_level_'+tag)
        if semaphore==True:
            logging.info("already processed "+tag)
            return model
        else:
            memcache.set('set_category_level_'+tag,True)
        level=int(level)
        
        if level>7:
            logging.error("exceeded maximum depth ("+str(level)+" processing "+tag)
            return model
        
        
        subcategories=WikiLib.getSubCategories(tag)
        if not subcategories:
            logging.info("no subcategories for "+tag)
        #model["subcategories"]=subcategories
        
        for wikicatname in subcategories:
            #wikicat=WikiLib.getCategory(wikicatname)
            wikicat=WikiLib.getCategoryByName(wikicatname)
            
            if wikicat:
                cat=CategoryLib.getByWikiName(wikicatname)
                
                if cat and cat.level==None:
                    logging.info("setting level = "+str(level)+" for category "+cat.name)
                    cat.level=level
                    cat.save()
                    # now for this category get all its subcategories!
                #else:
                #    logging.warn("no category "+wikicatname)
            #else:
            #    logging.warn("not wikicat "+wikicatname)
            semaphore=memcache.get('set_category_level_'+wikicatname)
            if not semaphore:
                taskqueue.add(url="/json/category/set_category_level/"+wikicatname,params={"tag":wikicatname,"level":level+1})
            else:
                logging.warn("2. already processed "+wikicatname)
            #self.set_category_levelAction(wikicatname, level+1)
                
        return model
    
    
    def defaultAction(self,qs=None,segments=None):
        model={}
        
        return model
    
    def homeAction(self,tag=None,page=1):
        model=CategoryHomeModel()
        
        try:
            model.page=int(page)
        except ValueError:
            model.page=1      
        
        if tag:
            model.metadescription=model.metadescription+" about "+tag
            model.metakeywords=tag+","+model.metakeywords
            model.page_subtitle='Articles about '+tag
            
        if model.page>1:
            model.metadescription=model.metadescription+' - page '+str(model.page)
            model.metakeywords=model.metakeywords+',page '+str(model.page)
            if model.page_subtitle:
                model.page_subtitle=model.page_subtitle+" - "
            model.page_subtitle=model.page_subtitle+'Page '+str(model.page)
        
        model.articles=[]
        model.category_name=tag
        
        category=CategoryLib.getByTag(tag)
        if category:
            acs=ArticleCategoryModel.all().filter("archived =",False).filter("category =",category).order("-sortkey").fetch(10,0)
            for ac in acs:
                acats = ArticleLib.getArticleCategories(ac.article)
                ac.article.tags=[]
                for acat in acats:
                    ac.article.tags.append(acat.category.name)
                model.articles.append(ac.article)
                        
            #(model.leaderboard,model.userstats,model.greater_userstats,model.lesser_userstats)=HomeController.getLeaderBoard(self.user,1,[category])
            
            model.leaderboard=KnowledgeLib.getTopUsers(category)
            model.greater_userstats=KnowledgeLib.getRelativeUserStats(self.user,True,False,[category]);
            model.lesser_userstats=KnowledgeLib.getRelativeUserStats(self.user,False,True,[category]);
            model.userstats=KnowledgeLib.getUserStats(self.user,[category])
            
      
        #List of parent categories
        #List of child categories
        model.user=self.user
        
        return CategoryHomeView(model)
    
    def queue_removeduplicatesAction(self):
        taskqueue.add(url="/category/removeduplicates")
        return NullView(None)
    
    def removeduplicatesAction(self):
       
        allcats={}
        duplicates={}
        offset=0
        cats=CategoryModel.all().fetch(50,offset)
        while cats:
            for c in cats:
                if allcats.has_key(c.name):
                    if duplicates.has_key(c.name):
                        duplicates[c.name].append(c)
                    else:
                        duplicates[c.name]=[c]
                else:
                    allcats[c.name]=1
            offset=offset+50
            cats=CategoryModel.all().fetch(50,offset)
                    
        for d in duplicates.values():
            for c in d:
                c.delete();
            
        return NullView(None)
    
    def adminAction(self,page=1,haswikiname=None):
        
        model=AdminCategoryModel()
        try:
            p=int(page)
        except (TypeError,ValueError):
            return HomeController.fourzerofourAction()
        
        #get a list of all categories
        if p <1:
            p=1
        limit=10
        offset=(p-1)*limit
        
        model.haswikiname=haswikiname
        model.page=p
        
        if haswikiname:
            model.categories=CategoryModel.all().filter("wikiname !=",None).fetch(limit,offset)
        else:
            model.categories=CategoryModel.all().fetch(limit,offset)
        
        
        model.previouspage=p-1
        model.nextpage=p+1
        
        return AdminCategoryView(model)
    
    def setwikinameAction(self,name,wikiname):
        self.requireLoggedin('admin')

        cats=CategoryModel.all().filter("name =",name).fetch(10,0)
        
        if not cats:
            logging.info('no category found named '+name)
            return JSONView(False)
        
        if len(cats) >0:
            logging.info('too many categories named '+name)
            
        for cat in cats:
            cat.wikiname=wikiname
            cat.save()
            
        return JSONView(True)
    
    def searchAction(self,terms=None,sort='articles',sort_order='descending',page=1):
        try:
            page=int(page)
        except (TypeError,ValueError):
            page=1
        
        if page<1:
            page=1
        
        limit=20
        offset=(page-1)*limit
        
        if sort_order=='descending':
            direction=search.SortExpression.DESCENDING
        elif sort_order=='ascending':
            direction=search.SortExpression.ASCENDING
        else:
            sort_order='descending'
            direction=search.SortExpression.DESCENDING
            
        if sort=='alphabetical':
            expression='name'
            default_value='a'
        elif sort=='articles':
            expression='number_of_articles'
            default_value=0
        else:
            sort='articles'
            expression='number_of_articles'
            default_value=0
        
        model=SearchCategoryModel()
        model.categories=[]
        model.terms=terms
        model.sort=sort
        model.sort_order=sort_order
        model.page=page
        model.limit=limit
        model.user=self.user
        
        if terms:
            model.metadescription='Community Search Results for '+terms
            model.metakeywords='Communities,'+terms
            model.page_subtitle=model.metadescription
        else:
            model.metadescription='Search for Communities'
            model.metakeywords='community,search'
            model.page_subtitle=model.metadescription
            
        if model.page>1:
            model.metadescription=model.metadescription+' - page '+str(model.page)
            model.metakeywords=model.metakeywords+',page '+str(model.page)
            if model.page_subtitle:
                model.page_subtitle=model.page_subtitle+" - "
            model.page_subtitle=model.page_subtitle+'Page '+str(model.page)
            
        
        index = search.Index(name="categories")
        
        sort1 = search.SortExpression(expression=expression, direction=direction, default_value=default_value)
        sort_opts = search.SortOptions(expressions=[sort1])
        query_options = search.QueryOptions(offset=offset,limit=limit,sort_options= sort_opts)
        
        
        if terms:
            query = search.Query(query_string="name: "+terms, options=query_options)    
        else:
            model.terms=""
            query = search.Query(query_string="number_of_articles >= 0", options=query_options)
            
        search_result = index.search(query)
        if search_result:
            model.num_records=search_result.number_found
            
            #logging.info("found "+str(search_result.number_found)+" results for terms:"+terms);
            for document in search_result:
                model.categories.append({
                 "name":document.fields[0].value,
                 "number_of_articles":document.fields[1].value
                 })
           
        model.num_records=len(model.categories)
        
        if model.categories:
            model.nextpage=page+1
        if page > 1:
            model.previouspage=page-1
        
        
        return SearchCategoryView(model)