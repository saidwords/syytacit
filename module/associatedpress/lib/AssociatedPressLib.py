# coding=UTF-8
# -*- coding: UTF-8 -*-
from module.associatedpress.lib.AssociatedPressWebService import AssociatedPressWebService
from module.associatedpress.model.AssociatedPressCategoryModel import AssociatedPressCategoryModel
from module.associatedpress.model.AssociatedPressHeadlineModel import AssociatedPressHeadlineModel
from module.article.model.ArticleModel import ArticleModel
from module.article.lib.ArticleLib import ArticleLib
from google.appengine.api import taskqueue
from common.models.CategoryModel import CategoryModel
import logging
from common.lib.CategoryLib import CategoryLib

class AssociatedPressLib:
    def save_latest_headlines(self):
        ap = AssociatedPressWebService()
        category = AssociatedPressCategoryModel()
        category.id=ap.CATEGORY_TOP_GENERAL_SHORT_HEADLINES
        articles=ap.getBreakingNews(category)
        articleModel = ArticleModel(title='null',ihref='null')
        q=articleModel.all();
        return None
    
        logging.info("found "+ str(len(articles))+" articles");
        categories=[]
        for article in articles:
            assert isinstance(article, AssociatedPressHeadlineModel)
            # do not insert the article if it already is in the db
            q=ArticleModel.all();
            q.filter("id =",article.id)
            total=q.count()
            if total == 0:
                xarticle = ArticleModel(title=article.title,id=article.id,href=article.href,updated=article.updated,ihref='null',tags=article.categories)
                xarticle.ihref=ArticleLib.createUrl(xarticle)
                xarticle.source=ArticleLib.SOURCE_AP
                for username in article.authors:
                    xarticle.authors.append(username)
                xarticle.put();
                # uncomment the following line to use the opencalais service to set the article categories
            
                taskqueue.add(queue_name="articleclassify",url='/article/classify/'+str(xarticle.key()))
            for category in article.categories:
                if category not in categories:
                    categories.append(category)
            
        for category in categories:
            # add the category to the datastore if it doesnt exist
            q=CategoryModel.all()
            q.filter("name =",category)
            total=q.count()
            if total == 0: # if the category doesnt exist then create it
                c=CategoryModel(name=category)
                logging.info('adding new category '+category)
                CategoryLib.addToSearchIndex(category)
                c.put()                
