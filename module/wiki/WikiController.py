# coding=UTF-8
# -*- coding: UTF-8 -*-
# -*- coding: utf-8 -*-
from common.lib.Controller import Controller
from module.home.view.NullView import NullView
from common.models.CategoryModel import CategoryModel
import datetime
from module.wiki.lib.WikiLib import WikiLib
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
from module.wiki.model.GetSentencesModel import GetSentencesModel
from module.wiki.model.GetPagesModel import GetPagesModel
from module.natlang.model.SentenceModel import SentenceModel
from module.wiki.model.WikiModel import WikiModel
import logging



class WikiController(Controller):
    
    def deleteAction(self,key):
        self.requireLoggedin('admin')
        model={"deletions":0}
        
        wiki=WikiModel.get(key)
        
        if not wiki:
            raise Exception('wiki not found')
        
        model['deletions']=WikiLib.delete(wiki)                                                                               
        
        return model
    
    def fooAction(self):
        return None
        from module.wiki.model.WikiModel import WikiModel
        #get a list of all pages in category Art
        #http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Arts&format=jsonhttp://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Arts&format=json&cmcontinue=page|4152544953544943204d455249540a4152544953544943204d45524954|2482029
        #http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Arts&format=json&cmcontinue=page|4152544953544943204d455249540a4152544953544943204d45524954|2482029
        #cat=CategoryModel(name="Arts")
        #pages=WikiLib.getPages(cat)
        #return None
        #pagecategories=WikiLib.getPageCategories('Art')
        
        
        #wtitle=unicode('Wikipedia_talk:Articles_for_creation/José_Veiga_(football_agent)')
        
        
        #wiki=WikiModel(title=wtitle.encode('utf-8',errors='ignore'))
        
        #WikiLib.getSentences(wiki)
        
        #foo=1
        
        #url = WikiLib.BASE_URL+"/"+WikiLib.API_ENDPOINT+"?action=query&prop=info&format=json&inprop=url&titles=Category"+category
        #urlFetchResult = urlfetch.fetch(url,None,urlfetch.GET,{},False,True,30)
        #data = simplejson.loads(urlFetchResult.content)

        
        wikis=WikiModel.all().fetch(5000,0)
        for wiki in wikis:
            t=wiki.url.split('/')
            if len(t)>0:
                title=t[len(t)-1]
                print("title='"+title+'"<HR>')
                wiki.title=title
                wiki.save()
            else:
                print(" no title for "+wiki.url)
        
        return None
    
    def deletesentencesAction(self):
        key="ag1kZXZ-c2FpZHdvcmRzchALEglXaWtpTW9kZWwYiC8M"
        if self.authenticate():
            wiki=WikiModel.get(key)
            for sentence in SentenceModel.all().filter("wiki = ",wiki).fetch(500,0):
                sentence.delete()
        else:
            raise Exception("you must be an admin to do that!")
    
    def getpagecategoriesAction(self,title):
        model={'result':None}
        model['result']=WikiLib.getPageCategories(title)
        
        return model
    
    def viewcategoryAction(self,tag):
        cat = CategoryModel.all().filter("name =",tag).get()
        
        return NullView(cat)
    
    def deletecategoryAction(self,tag):
        cat = CategoryModel.all().filter("name =",tag).get()
        if cat:
            cat.delete()
        return NullView(cat)
    
    
    """
    add a wiki category to the database.
    optionally add a mapping from wikicategoryname to regular categoryname
    """
    def addcategoryAction(self,name,wikiname):
        
        cat=WikiCategoryModel.all().filter("name =",wikiname).get()
        if not cat:
            cat = WikiCategoryModel(name=wikiname,url=WikiLib.getCategoryUrl(wikiname));
            cat.save()
        
        if name:
            rcat=CategoryModel.all().filter("name =",name).get()
            if rcat:
                rcat.wikiname=wikiname
            else:
                rcat=CategoryModel(name=name,wikiname=wikiname)
        
            rcat.save()
            
                
        return NullView(None)
    
    def acquirepagesAction(self,category=None):
        model=GetPagesModel()
        
        c= CategoryModel.all().filter("name =",category).get()
        
        if c:
            if c.wikiname:
                category=c.wikiname
        else:
            pass
            #TODO: generate an error message that notifies me immediately so that I can add the category
        
        cat=WikiCategoryModel.all().filter("name =",category).get()
        if cat:
            model.pages=WikiLib.getPages(cat);
        else:
            raise Exception("category not found")
        
        return NullView(model)
    
    # fetchs categories from wikipedia
    #todo: if a name is specified, then get the subcategories for that name
    def acquirecategoriesAction(self,name=None):
        logging.info("I do not think this function does what you think it should")
        return None
    
        model=GetPagesModel()
        
        i=0
                
        wikicategories = WikiLib.getMainTopicClassifications()
        
        for cat in wikicategories:
            c=WikiCategoryModel.all().filter("name =",cat.name).get()
            cat.date_updated=datetime.datetime.now()
            if not c:
                i=i+1
                cat.save()
            else:
                c.put()
           
        model.message="saved "+str(i)+" new categories"
        return NullView(model)
        
    def acquiresentencesAction(self,tag=None):
        model = GetSentencesModel()
        
        sentencecount=WikiLib.acquireSentences(tag)
        
        model.message="added "+str(sentencecount)+" new sentences for tag "+tag
            
        return NullView(model)
