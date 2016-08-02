# coding=UTF-8
# -*- coding: UTF-8 -*-
import datetime
import logging
import math
import urllib2

from google.appengine.api import taskqueue, mail

from common.lib.CategoryLib import CategoryLib
from common.lib.Controller import Controller
from common.lib.MturkLib import MturkLib
from common.lib.RSSLib import RSSLib
from common.models.CategoryModel import CategoryModel
from module.article.lib.ArticleLib import ArticleLib
from module.article.model.ArticleModel import ArticleModel
from module.associatedpress.lib.AssociatedPressLib import AssociatedPressLib
from module.category.CategoryController import CategoryController
from module.comments.lib.CommentsLib import CommentsLib
from module.comments.model.Comments import Comments
from module.home.view.NullView import NullView
from module.mturk.MturkController import MturkController
from module.natlang.model.SentenceModel import SentenceModel
from module.usatoday.lib.UsaTodayLib import UsaTodayLib
from module.wiki.lib.WikiLib import WikiLib
from module.wiki.model.WikiCategoryModel import WikiCategoryModel
from module.wiki.model.WikiModel import WikiModel
from webapp2_extras.appengine.auth.models import User

class CronController(Controller):
    
    def generate_reportAction(self):
        model={'num_comments':0,'num_articles':0,'num_users':0}
        # number of new comments in the last 24 hours
        model['num_comments']=Comments.all().filter("created >",(datetime.datetime.now()-datetime.timedelta(days=1))).count()
        # number of new articles in the last 24 hours
        model['num_articles']=ArticleModel.all().filter("updated >",(datetime.datetime.now()-datetime.timedelta(days=1))).count()
        # number of new users in the last 24 hours
        
        qry = User.query(User.created > datetime.datetime.now()-datetime.timedelta(days=1))
        model['num_users']=qry.count()
        
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'Daily Activity Report',str(model)) 
        
        return model
        
    
    def set_category_levelAction(self):
        model={"total":0}
        
        category=CategoryModel.all().filter("level =",None).filter("wikiname !=",None).get()
        
        if category:
            CategoryController().set_category_levelAction(category.wikiname)
        
        return model
    
    def sort_articlesAction(self):
        model={"num_articles":0}
        model['num_articles']=ArticleLib.sort_articles()
        return model
    
    def reload_article_memcacheAction(self):
        model={"num_articles":0}
        model['num_articles']=ArticleLib.reload_memcache()
        #mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', '/cron/reload_article_memcache','loaded '+str(model['num_articles'])+" articles")
        return model
    
    def flush_article_memcache_to_dbAction(self):
        model={"total":0}
        model['total']=ArticleLib.flush_memcache_to_db()
        #mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', '/cron/flush_article_memcache_to_db','flushed '+str(model['total'])+" records") 
        return model
    
    def delete_category_search_indexAction(self,page=1,limit=100,rebuild=True):
        model={"total":0}
        
        model['total']=CategoryLib.deleteSearchIndex(limit)
        if model['total']>0:
            taskqueue.add(url="/json/cron/delete_category_search_index")
        elif rebuild:
            taskqueue.add(url="/json/cron/build_category_search_index")
        return model
    
    def build_category_search_indexAction(self,page=1,limit=100):
        model={"total":0}
        
        model['total']=CategoryLib.buildSearchIndex(page,limit)
        if model['total']>0:
            taskqueue.add(url="/json/cron/build_category_search_index")
    
        return model
    def acquire_rss_articlesAction(self,rss_url=None):
        model={'num_articles':0,"num_queued":0}
        if rss_url:
            rss_url=urllib2.unquote(rss_url)
            model['num_articles']=model['num_articles']+RSSLib.saveArticles(rss_url)
            logging.info("loaded "+str(model['num_articles'])+" new articles")
        else:
            
            rssfeeds=[
                      'http://news.stanford.edu/rss/grad.xml',
                      'http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/PressReleases/rss.xml',
                      'http://www.nist.gov/rss/math.xml',
                      'http://www.fda.gov/downloads/Drugs/ResourcesForYou/HealthProfessionals/UCM220293.xml',
                      'http://www.bea.gov/rss/rss.xml',
                      'http://news.stanford.edu/rss/humanities.xml',
                      'http://www.army.mil/rss/73/',
                      'http://www.loc.gov/rss/pao/news.xml',
                      'http://www.nist.gov/rss/nanotechnology.xml',
                      #'http://feeds.feedblitz.com/cbospublications&x=1',
                      'http://media.ca7.uscourts.gov/oralArguments/oar.jsp?rss=rss',
                      'http://news.stanford.edu/rss/health.xml',
                      'http://www.army.mil/rss/71/',
                      'http://www.humanrights.gov/feed/',
                      'https://www.cia.gov/news-information/your-news/cia-newsroom/RSS.xml',
                      'http://www.nist.gov/rss/physics.xml',
                      'http://www.state.gov/rss/channels/cec.xml',
                      'http://news.stanford.edu/rss/international.xml',
                      'http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/TDS/rss.xml',
                      'http://www.army.mil/rss/284/',
                      'http://www.state.gov/rss/channels/scrs.xml',
                      'http://travel.state.gov/_res/rss/TWs.xml',
                      'http://www.nist.gov/rss/transportation.xml',
                      'http://www.usaid.gov/rss/press-releases.xml',
                      'http://www.usgs.gov/rss/news.rss',
                      'http://ars.usda.gov/news/rss/rss.htm',
                      'http://travel.state.gov/_res/rss/TAs.xml',
                      'http://www.nist.gov/rss/chemistry.xml',
                      'http://www.state.gov/rss/channels/inl.xml',
                      'http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/PetHealth/rss.xml',
                      'http://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfTopic/cdrhnew-rss.cfm',
                      'http://www.nist.gov/rss/electronicsandtelecommunications.xml',
                      'http://www.state.gov/rss/channels/ct.xml',
                      "http://www.simonsfoundation.org/quanta-archive/feed/",
                      'http://www.state.gov/rss/channels/acis.xml',
                      "http://angeion.me/feed/",
                      "http://www.darpa.mil/Rss.aspx?Colid=24",
                      'http://www.state.gov/rss/channels/highlights.xml',
                      'http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/Drugs/rss.xml',
                      "https://www.thecsiac.com/aggregator/rss",
                      'http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/FoodAllergies/rss.xml',
                      'http://www.csrees.usda.gov/rss/research.xml',
                      'http://www.raconline.org/rss/pubs.xml',
                      'http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/Consumers/rss.xml',
                      'http://www.eia.gov/energy_in_brief/eibinfo.cfm',
                      'http://www.raconline.org/rss/news.xml',
                      'http://www.ferc.gov/xml/whats-new.xml',
                      'http://feeds.feedburner.com/NrelFeatureStories?format=xml',
                      'http://yosemite.epa.gov/opa/admpress.nsf/RSSByCategory?open&category=Air',
                      'http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/AnimalVeterinary/rss.xml',
                      'http://www.eia.gov/about/new/wntest3.cfm',
                      'http://yosemite.epa.gov/opa/admpress.nsf/RSSByCategory?open&category=Hazardous%20Waste',
                      'http://sanctuaries.noaa.gov/feed.xml',
                      'http://yosemite.epa.gov/opa/admpress.nsf/RSS/research?opendocument',
                      'http://www.nodc.noaa.gov/OC5/RSS/wod_updates.xml',
                      'http://oceanservice.noaa.gov/rss/oceanfacts.xml',
                      'http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/FoodSafety/rss.xml',
                      'http://yosemite.epa.gov/opa/admpress.nsf/RSSByCategory?open&category=Water',
                      'http://wwwnc.cdc.gov/travel/rss/notices.xml',
                      'http://publications.nigms.nih.gov/biobeat/rss/current.xml',
                      'http://www.nodc.noaa.gov/SatelliteData/pathfinder4km/pathfinder_news_rss.xml',
                      'http://www.nih.gov/news/feed.xml',
                      'http://www2c.cdc.gov/podcasts/createrss.asp?t=r&c=340',
                      'http://www.niehs.nih.gov/news/newsroom/rssfeed/rss_news.xml',
                      'http://www.us-cert.gov/ncas/all.xml',
                      'http://www2c.cdc.gov/podcasts/createrss.asp?t=r&c=20',
                      'http://www.nasa.gov/rss/dyn/image_of_the_day.rss',
                      'http://www2c.cdc.gov/podcasts/createrss.asp?t=r&c=513',
                      'http://www.sti.nasa.gov/scan/rss99-01.xml',
                      'http://www.us-cert.gov/ncas/tips.xml',
                      'http://earthobservatory.nasa.gov/Feeds/rss/eo.rss',
                      'http://library.bldrdoc.gov/news.xml',
                      'http://www.darpa.mil/Rss.aspx?Colid=24',
                      'http://www.nasa.gov/rss/dyn/breaking_news.rss',
                      'http://www.nij.gov/documents/rss-main.xml',
                      'http://www.nist.gov/rss/bioscienceandhealth.xml',
                      'http://rss.xerox.com/xerox-news',
                      'http://www.nist.gov/rss/forensics.xml',
                      'http://www.nsf.gov/rss/rss_www_news.xml',
                      "http://feeds.feedburner.com/TheHackersNews?format=xml",
                      'http://www.nist.gov/rss/buildingandfireresearch.xml',
                      'http://web.ornl.gov/ornlhome/rss/ornl_in_news.xml',
                      'http://apps1.eere.energy.gov/news/rss/enn.xml',
                      'http://www.nist.gov/rss/informationtechnology.xml',
                      'http://web.ornl.gov/ornlhome/rss/sns_news.xml',
                      'http://www.ntia.doc.gov/rss/updates.xml',
                      'http://news.stanford.edu/rss/arts.xml',
                      'http://www.stanford.edu/group/knowledgebase/cgi-bin/feed/',
                      'http://www.nist.gov/rss/manufacturing.xml',
                      'http://news.stanford.edu/rss/environment.xml',
                      'https://newsoffice.mit.edu/rss/school/architecture-and-planning',
                      'https://newsoffice.mit.edu/rss/research',
                      'http://www.nsf.gov/rss/rss_www_discoveries.xml',
                      'http://www.nsf.gov/rss/rss_www_news.xml',
                      'http://www.nsf.gov/rss/rss_www_news_field.xml',
                      'http://news.tamhsc.edu/feed/',
                      'http://www.nsbri.org/RSS/default.asp?ChannelTitle=Science%20and%20Technology&ChannelDesc=Science%20and%20Technology&Category=Science%20and%20Technology',
                      'http://www.janes.com/rss',
                      'http://www.justice.gov/rss/rss.opa.hp.xml',
                      'http://www.justice.gov/rss/rss.crm.hp.xml',
                      'http://www.justice.gov/atr/rss/atr_press.xml',
                      #'http://feeds.feedburner.com/WIREAwardsWatch?format=xml',
                      #'http://feeds.feedburner.com/indiewireTelevision?format=xml',
                      'http://feeds.feedburner.com/Criticwire?format=xml',
                      #'http://feeds.feedburner.com/sundancefest_all',
                      'http://feeds.feedburner.com/WUSTL-Top-Stories-News',
                      #'http://feeds.feedburner.com/indieWIREFesitvals?format=xml',
                      'http://rss.feedsportal.com/c/662/f/8410/index.rss',
                      'http://i.rottentomatoes.com/syndication/rss/top_news.xml',
                      'http://feeds.feedburner.com/alistapart/main?format=xml',
                      'http://www.pewresearch.org/feed/',
                      'http://feeds.feedburner.com/ncictresults?format=xml',
                      'http://feeds.feedburner.com/ncinewsreleases?format=xml',
                      'http://www.idiap.ch/the-institute/news/institute-news/RSS',
                      #'http://feeds.feedburner.com/indieWIRENews?format=xml',
                      'http://www.idiap.ch/scientific-research/news/news/RSS',
                      'http://feeds.feedburner.com/Ifpriupdate',
                      'http://feeds.feedburner.com/IfpriPressReleases',
                      'http://feeds.feedburner.com/ilrinews',
                      'http://jp.fujitsu.com/group/fri/en/rss/fri-message.rss',
                      'http://jp.fujitsu.com/group/fri/en/rss/fri-reserchreport.rss',
                      'http://feeds.feedburner.com/NhgriPressReleases?format=xml',
                      'http://feeds.feedburner.com/WUSTL-ArtSci-News',
                      
                      ];
            # feeds that require custom ingestor
            #'http://www.hopkinsmedicine.org/news/media/releases',
                      
            #http://www.ed.ac.uk/schools-departments/medicine-vet-medicine/news-events/all-news/latest-news
            #http://wcatwc.arh.noaa.gov/events/xml/PAAQAtom.xml
            #http://www.bnl.gov/bnlweb/rss.asp
            #http://ehp.niehs.nih.gov/feed/
            #http://www.nidcr.nih.gov/nidcr2.nih.gov/Rss/?Channel=/Research/ResearchResults/NewsReleases/
            #http://www.nidcr.nih.gov/nidcr2.nih.gov/Rss/?Channel=/Research/ResearchResults/ScienceBriefs/
            #http://apps3.eere.energy.gov/greenpower/gpn_rss.php
            #http://www.prh.noaa.gov/cphc/index-cp.xml
            #http://web.ornl.gov/ornlhome/rss/doepulse.xml
            #http://www.fda.gov/AboutFDA/ContactFDA/StayInformed/RSSFeeds/Food/rss.xml
            #http://app.feeddigest.com/digest3/HD4A0PA7ON.rss
            #http://www.ed.gov/feed
            #http://ies.ed.gov/ncer/whatsnew/whatsnew_rss.asp
            #http://www.state.gov/rss/channels/pending.xml
            #http://www.state.gov/rss/channels/whatsnew.xml
            #http://www.state.gov/rss/channels/treatyactions.xml
            #http://www.state.gov/rss/channels/tef.xml
            #http://www.state.gov/rss/channels/statecraft.xml 
            #http://www.state.gov/rss/channels/alldos.xml
            #http://www.state.gov/rss/channels/ds.xml
            #http://www.state.gov/rss/channels/opengov.xml
            #http://www.state.gov/rss/channels/social.xml
            #http://www.state.gov/rss/channels/eeati.xml
            #http://www.state.gov/rss/channels/gcj.xml
            num_feeds=len(rssfeeds)
            pagesize=int(math.ceil((0.0+num_feeds)/(0.0+24)))
            offset=(datetime.datetime.now().hour)*pagesize
            for i in range(offset,offset+pagesize):
                if i>=num_feeds:
                    break
                model['num_queued']=model['num_queued']+1
                logging.info("queued "+rssfeeds[i])
                rss_url=urllib2.quote(rssfeeds[i],"\n")
                taskqueue.add(url="/json/cron/acquire_rss_articles",params={'rss_url':rss_url},retry_options=taskqueue.TaskRetryOptions(task_retry_limit=0))
                
                
        return model
    
    
    """
    Archive articles that people are losing interest in
    """
    def archive_articlesAction(self):
        
        model={"total":[]}
        return model
    
        page=0
        limit=10
        total=0
        articles=[1]
        #articles=ArticleModel.all(keys_only=True).order("-sortkey").fetch(limit,100+(page*limit))
        while articles:
            articles=ArticleModel.all().filter("archived =",False).order("-updated").fetch(limit,(page*limit)+100)
            page=page+1
            for article in articles:
                article.archived=True
                total=total+1
                article.save()
                # also archive the article cateogories 
                article_categories=ArticleLib.getArticleCategories(article, False)
                for article_category in article_categories:
                    article_category.archived=True
                    article_category.save()
            
        
        
        # remove articles that have been in the top 10 more than a day
        articles=ArticleModel.all().filter("archived =",False).order("-sortkey").fetch(10,0)
        
        for article in articles:
            elapsed=datetime.datetime.now()-article.updated
            if elapsed.total_seconds()>86400: 
                article.archived=True
                total=total+1
                article.save() 
                # also archive the article cateogories 
                article_categories=ArticleLib.getArticleCategories(article, False)
                for article_category in article_categories:
                    article_category.archived=True
                    article_category.save()
                
        model['total']=total
        logging.info("archived "+str(total)+" articles")
        
        return model
    
   
        
    """
    finds HITS that have been approved and whose results have been saved and removed them from mechanical turk
    """
    def remove_old_approved_hitsAction(self):
        m=MturkLib()
        num_hits=m.remove_old_approved_hits();
            
        model={"num_hits":num_hits}
        message="removed "+str(num_hits)+" old approved hits"
        logging.info(message)
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'remove_old_approved_hits results',message)
        return NullView(model)

    def get_question_hitsAction(self):
        model={"approved_hits":0}
        model['approved_hits']=MturkController().get_question_hitsAction()
        message="got "+str(model['approved_hits'])+" new questions from mechanical turk"
        logging.info(message)
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'get_question_hits results',message)
        
        return model
    
    
    def get_fibquestion_hitsAction(self):
        model={"approved_hits":0}
        model['approved_hits']=MturkController().get_fibquestion_hitsAction()
        message="got "+str(model['approved_hits'])+" new questions from mechanical turk"
        logging.info(message)
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'get_fibquestion_hits results',message)
        
        return model
    
    def turk_creates_questionAction(self,num_questions=10):
        try:
            num_questions=int(num_questions)
            model =MturkController().create_questionAction(num_questions)
       
            message="sent "+str(model['numsentences'])+" sentences to mechanical turk for conversion to a question"
        except ValueError:
            message="invalid value for parameter num_questions: "+(str(num_questions)) 
        
        
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'turk_creates_question results',message)
        return model
    
    def turk_creates_fibquestionAction(self,num_questions=10):
        try:
            num_questions=int(num_questions)
            model =MturkController().create_fib_questionAction(num_questions)
            message="sent "+str(model['numsentences'])+" sentences to mechanical turk for conversion to a question"
        except ValueError:
            message="Invalid value for parameter num_questions: "+str(num_questions)
        
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'turk_creates_fibquestion results',message)
        return model
      
    def getsentencehitsAction(self):
        model=MturkController().getsentencehitsAction()
        message="got "+str(model['num_sentences'])+" sentences from mechanical turk"
        logging.info(message)
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'getsentencehits results',message)
        return model
    
    def remove_approved_turk_hitsAction(self):
        MturkLib().remove_old_approved_hits()
        return None
    
    def indexAction(self):

        return NullView()
    
    def acquire_latest_usatoday_headlinesAction(self):
        model={'message':None}
        articles=UsaTodayLib().save_latest_headlines()
        model['message']="got "+str(len(articles))+" new articles from usatoday"
        logging.info(model['message'])
        
        #mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'acquire_latest_usatoday_headlines results',model['message'])
        
        self.categorize_articlesAction()
        return model
    def acquire_ap_latest_headlinesAction(self):
        
        aplib=AssociatedPressLib()
        aplib.save_latest_headlines()
        #taskqueue.add(url="/json/cron/map_categories_to_wiki")
        
      
        
        #TODO: tasqueue.add(url="/cron/acquire_sentences");
        return NullView()
    
    """
    attempts to set the value for CategoryModel.wikiname.
    for all categorymodels having no wikiname it asks wikipedia if it knows of such category. 
    """
    def map_categories_to_wikiAction(self):
        model={'message':""}
        num_missing_cats=ArticleLib.map_categories_to_wiki()
        model['message']='Found '+str(num_missing_cats)+" categories that I cant find a page in wikipedia for"
        logging.info(model['message'])
        #mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'map_categories_to_wiki results',model['message'])
        
        return model
  
    """
    find the latest articles and get wiki pages that are related to them
    """
    def acquire_wiki_pagesAction(self,category=None):
        model={'message':"",'total':0}
        cats={}
        
        if category:
            cat=CategoryLib.getByTag(category)
            if not cat:
                logging.error("Category "+category+" not found")
                return None
            if not cat.wikiname:
                #cat.wikiname="Fashion"
                #cat.save()
                logging.error("no wiki category for "+category)
                return None
            
            cats[category]=cat
        else:
            # get categories from latest articles
            articles=ArticleModel.all().order("updated").fetch(10,0)
            for article in articles:
                article_cats=ArticleLib.getCategories(article)
                for cat in article_cats:
                    if not cats.has_key(cat.name):
                        cats[cat.name]=cat
            
        if not cats:
            model['message']='No articles have any categories!'
            
        for category_name in cats:
            if cats[category_name].wikiname:
                wikicat=WikiCategoryModel.all().filter("name =",cats[category_name].wikiname).get()
                if wikicat:
                    wikis=WikiModel.all().filter("category in",[wikicat.key()]).fetch(1,0)
                    if wikis:
                        logging.info("We already have pages for "+wikicat.name)
                    else:
                        wikis=WikiLib.getPages(wikicat);
                        model['total']=model['total']+len(wikis)
                        for wiki in wikis:
                            if not wiki.title:
                                logging.info("wiki record "+str(wiki.key())+" has no title")
                                continue
                        
                            pagecats=WikiLib.getPageCategories(wiki.title)
                            flag=False
                            for cat in pagecats:
                                if cat.key() not in wiki.categories:
                                    flag=True
                                    #logging.info("tagging wiki page "+wiki.title+" with category "+cat.name)
                                    wiki.categories.append(cat.key())
                                    
                            if flag:
                                
                                wiki.save()
                        
                        #model['message']="found "+str(len(wikis))+" wiki pages for category "+wikicat.name+"\n"
                        
                    
                        #if wikis:
                        #    for wiki in wikis:
                        #        taskqueue.add(url="/cron/acquire_sentences/"+str(wiki.key()))
                        #else:
                        #    logging.info("we dont have any pages for "+article_cat.category.name)
                else: 
                    logging.info('cant find wikicategory where name='+str(cats[category_name].wikiname))
            else:
                logging.info('category '+cats[category_name].name+' has no wikicategory')
                # its often the case that there will be a wiki page having the exact same name as the category.
                # so lets try to get it
                
        model['message']=model['message']+"\n"+"found "+str(model['total'])+" wiki pages"
        logging.info(model['message'])
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', "acquire_wiki_pages results",model['message'])  
            
        return model
    """
    gets sentences for the given page
    @param key: a datastore key for a wikimodel record 
    """
    def acquire_sentencesAction(self,key=None,category=None):
        model={'message':''}
        if key:
            wiki=WikiModel.get(key)
        
        elif category:
            cat=CategoryLib.getByTag(category)
            if not cat:
                logging.error("Category "+category+" not found")
                return None
            if not cat.wikiname:
                logging.error("no wiki category for "+category)
                return None
            wikicat=WikiLib.getCategoryByName(cat.wikiname)
            if not wikicat:
                logging.error("wiki category '"+cat.wikiname+"' not found")
                return None
            wiki=WikiModel.all().filter("categories =",wikicat).order("date_updated").get()
        else:
            wikis=WikiModel.all().order("date_updated").fetch(10,0)
            if wikis:
                wiki=wikis[0]
                key=wikis[0].key()
                
        
        #for all newly acquired pages, acquire sentences
        if wiki:
            t=wiki.url.split('/')
            if len(t)>0:
                title=t[len(t)-1]
                if not wiki.title:
                    #wiki.title=unicode(title,errors='ignore')
                    wiki.title=title.encode("utf-8")
                    wiki.save()
            
            sentencecount=WikiLib.getSentences(wiki)
            model['message']="acquired "+str(sentencecount)+" sentences for page "+wiki.url.encode("utf-8")
            wiki.numsentences=sentencecount
            wiki.date_updated=datetime.datetime.now()
            wiki.save()
        else:
            model['message']="no sentences found!"
           

        logging.info(model['message'])
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', "acquire_sentences results",model['message'])  
        
        return model
    
    def turk_classifies_sentencesAction(self):
        model={"numsentences":0}
        message=""
        
        sentences=SentenceModel.all().filter("status =",0).order("updated").fetch(5,0) # get all unprocessed sentences
        
        #for sentence in sentences:
        #    logging.info(sentence.sentence)
        #    logging.info("type="+str(sentence.type))
            
        if len(sentences)==0:
            logging.info('no sentences found')
        else:
            mt_lib=MturkLib()
            price=0.05
            balance=mt_lib.getAccountBalance()
            if balance < price*len(sentences):
                message=message+'you dont have enough money to run Mturk.classify_sentences()'+"\n"
            else:
                message="sent "+str(len(sentences))+" to mechanical turk for classification"+"\n"
                mt_lib.classify_sentences(sentences)
               
        model['numsentences']=len(sentences)
        
        logging.info(message)
        
        mail.send_mail('lexiconcept@gmail.com', 'admin@syytacit.net', 'turk_classifies_sentences results',message)
        return NullView(model)
    
    def turk_gets_sentence_subject(self):
        m=MturkLib()
        
        # get a list of sentences that have been classified but dont have any questions attached
        sentences=[]
        for sentence in sentences:
            m.get_main_subject(sentence);
            
        model={"num_sentences":len(sentences)}
        return NullView(model)
    
    
    """
    Attempt to categories the most recent articles that have no categories
    """    
    def categorize_articlesAction(self):
        
        page=1
        limit=100
        articles=[1]
        article_cats=None
        while articles and not article_cats:
            article_cats=None
            articles=ArticleModel.all().order("-created").fetch(limit,(page-1)*limit)
            page=page+1
            for article in articles:
                article_cats=ArticleLib.getCategories(article,False)
                if not article_cats:
                    taskqueue.add(queue_name="articleclassify",url='/json/article/classify/'+str(article.key()))
                
        return None
            
            
    def calculate_top_articlesAction(self):
        
        
        model={"records":[]}
        
        
        """
        from webapp2_extras.appengine.auth.models import User
        users=User.query().iter()
        user=users.next()        
        while user:
            logging.info(user.auth_ids[0])
            try:
                user=users.next()
            except StopIteration:
                user=None    
        """
        ArticleLib.recalculate_all_sortkeys()
        
        return model
    
    def calculate_top_commentsAction(self):
        model={}
        
        CommentsLib.calculateTopComments()
        
        return model
        
          