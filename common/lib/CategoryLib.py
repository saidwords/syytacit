# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.models.CategoryModel import CategoryModel
from google.appengine.api.search import search
from module.article.model.ArticleCategoryModel import ArticleCategoryModel
from __builtin__ import UnicodeDecodeError
from google.appengine.api import memcache
import logging


class CategoryLib:
    
    IGNORE_CATEGORIES=['Unprintworthy redirects','Redirects from plurals']
    
    def addCategories(tags):
        #foreach tag, if it already exists, then ignore it, else add it
        #TODO: cache the lookup
        
        for tag in tags:
            c=CategoryModel.all().filter("name =",tag).get()
            if not c:
                c = CategoryModel(name=tag)
                c.save()
                
    def getByTag(tag,keys_only=False,cacheread=True,cachewrite=True):
        #try:
        #    utag=unicode(tag,errors="ignore")
        #except UnicodeDecodeError:
        #    utag=tag
       
        from google.appengine.api import memcache
        key='cat_getByTag_'+tag+str(keys_only)
        c=False
        if cacheread:
            c=memcache.get(key)
        if not c:
            try:
                c=CategoryModel.all(keys_only=keys_only).filter("name =",tag).get()
            except UnicodeDecodeError:
                utag=unicode(tag, 'utf-8')
                c=CategoryModel.all(keys_only=keys_only).filter("name =",utag).get()
                
        if cachewrite:
            memcache.set(key,c,(86400*8))
        
        return c
    
    def addToSearchIndex(category):
        index = search.Index(name="categories")
        num_articles=ArticleCategoryModel.all().filter("category =",category).count()
        document = search.Document(
                doc_id=None,
                fields=[
                    search.TextField(name='name', value=category.name),
                    search.NumberField(name='number_of_articles', value=num_articles), 
                    search.NumberField(name='number_of_users', value=0),
                ])
        index.put(document)
        return True
    
    def deleteSearchIndex(limit=100):
        total=0
        index = search.Index(name="categories")
        
        while True:
            if total>=limit:
                break
            
            # Get a list of documents populating only the doc_id field and extract the ids.
            document_ids = [document.doc_id for document in index.get_range(ids_only=True)]
            if document_ids:
                total=total+len(document_ids)
            if not document_ids:
                break
        # Delete the documents for the given ids from the Index.            
        if document_ids:
            index.delete(document_ids)
        return total
    
    def buildSearchIndex(page=1,limit=100):
        
        page=int(page)
        limit=int(limit)
        total=0
        # delete the current index
        index = search.Index(name="categories")
        
        # loop through all categories and add to index
        categories=CategoryModel.all()
        db_cursor = memcache.get('cat_search_index_cur')
        if db_cursor:
            categories.with_cursor(start_cursor=db_cursor)
            
        for category in categories:
            if total>=limit:
                break
            
            num_articles=ArticleCategoryModel.all().filter("category =",category).count()
            document = search.Document(
            doc_id=None,
            fields=[
                search.TextField(name='name', value=category.name),
                search.NumberField(name='number_of_articles', value=num_articles), 
                search.NumberField(name='number_of_users', value=0),
            ])
            index.put(document)
            total=total+1
            
        if total==0:
            logging.info("finished")
            memcache.delete('cat_search_index_cur')
        else:
            # Get updated cursor and store it for next time
            db_cursor = categories.cursor()
            memcache.set('cat_search_index_cur', db_cursor)
            
        return total
    
    def getByWikiName(wikiname):
        key='cat_getByWikiName_'+wikiname
        c=memcache.get(key)
        if not c:
            c=CategoryModel.all().filter("wikiname =",wikiname).get()
            memcache.set(key,c,(86400*8))
        
        return c
    
    addCategories = staticmethod(addCategories)
    getByTag=staticmethod(getByTag)
    addToSearchIndex=staticmethod(addToSearchIndex)
    buildSearchIndex=staticmethod(buildSearchIndex)
    getByWikiName=staticmethod(getByWikiName)
    deleteSearchIndex=staticmethod(deleteSearchIndex)
            
            
        