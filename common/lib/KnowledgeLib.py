# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.models.UserAnswerModel import UserAnswerModel
from common.models.QuestionModel import QuestionModel
import logging
from common.models.UserKnowledgeModel import UserKnowledgeModel
from google.appengine.api.datastore_errors import ReferencePropertyResolveError
import hashlib
from google.appengine.api import memcache
from common.models.CategoryModel import CategoryModel
from webapp2_extras.appengine.auth.models import User
class KnowledgeLib:
    
    
    
    def calculate_user_knowledge(user=None,userpage=0,question=None,useranswer=None):
        
        from datetime import datetime
        today = datetime.today()
        
        #get the total number of questions for each category
        categorycount={}
        limit=100
        page=0
        questions=[0]
        cats={}
           
        total_records=0
        if user and user.username:
            if userpage==0:
                users=[user]
            else:
                users=[]
        else:
            users=User.query().fetch(200)
            
        for user in users:
            # get all the answers that the user has submitted
            page=0
            useranswers=[1]
            userknowledges = {}
           
            while useranswers:
                if question:
                    if useranswer:
                        if page==0:
                            useranswers=[useranswer]
                        else:
                            useranswers=[]
                    else:
                        useranswers=UserAnswerModel.all().filter("username =",user.username).filter("question =",question).fetch(limit,page*limit)
                else:
                    useranswers=UserAnswerModel.all().filter("username =",user.username).fetch(limit,page*limit)
        
                page=page+1
                for answer in useranswers:
                    if answer.iscorrect:
                        # if the user got the question correct and a long time passed since they answered this question, then give them a bonus score
                        # bonus is between 0 and 1
                        
                        if answer.iscorrect:
                            elapsed=answer.updated-answer.topa
                            if elapsed.total_seconds()<1:
                                topa=0.0;
                            else:
                                topa=0.0+1-((0.0+1)/elapsed.total_seconds())
                        else:
                            topa=0.0
                       
                        #calculate a delay ( how long it took the user to answer the question after seeing it on the ui)
                        delay=(0.0+1)/answer.delay
                        
                        # calculate a decay (the score will decrease if a question has not been answered in a long time )
                        elapsed=today-answer.updated
                        if elapsed.total_seconds()<1:
                            decay=0.0;
                        else:
                            decay=0.0+1-((0.0+1)/elapsed.total_seconds())
                        
                        point =1.0 + topa -delay-decay #maximum point value is 2
                        
                        """
                        logging.info(today)
                        logging.info(answer.topa)
                        logging.info(answer.updated)
                        
                        logging.info("topa="+str(topa))
                        logging.info("delay="+str(delay))
                        logging.info("decay="+str(decay))
                        """
                        #logging.info("point =1.0+  "+str(topa)+"-"+str(delay)+"-"+str(decay)+"="+str(point))
                        
                        
                    else:
                        point=0.0
                        
                    for cat_key in question.cats:
                        if userknowledges.has_key(cat_key):
                            userknowledges[cat_key]=userknowledges[cat_key]+point
                        else:
                            userknowledges[cat_key]=point
                            
                    #for catkey in userknowledges:
                    #    logging.info("changing score for "+str(catkey))
            
            for cat_key in userknowledges:
                category=CategoryModel.get(cat_key)
                userknowledge=UserKnowledgeModel.all().filter("username =",user.username).filter("category =",category).get()
                maxscore=KnowledgeLib.getMaxScore(category)
                if not userknowledge:
                    userknowledge=UserKnowledgeModel(username=user.username,category=category)
                    total_records=total_records+1
                userknowledge.score=userknowledges[cat_key] 
                userknowledge.pct=(0.0+userknowledge.score/maxscore)
                userknowledge.save()
               
        
        return None
    
    def getLeaderBoard(cats,limit=10):
        results=[]
        if not cats:
            return results;
        
        key='kl_getLB'+hashlib.md5(str(limit)+str(cats)).hexdigest()
        data=memcache.get(key)
        if data:
            return data
        
        page=0
        alen=0
        records=[1]
        found=True
        while alen < 10 and found:
            found=False
            for cat in cats:
                records=UserKnowledgeModel.all().filter("category =",cat).order("-pct").fetch(1,page)
                if records:
                    found=True
                for record in records:
                    results.append(record)
                    alen=alen+1
                    if alen>limit:
                        break;
            page=page+1
            
            
        data=sorted(results, key=lambda result: result.pct,reverse=True)
        memcache.set(key,results,360)
        return data
    
    def getUserStats(user,cats=None,limit=10,offset=0):
       
        results=[]
        if not user or not user.username:
            return results
       
        """     
        key='kl_getustats'+hashlib.md5(user.username+"_"+str(limit)+"_"+str(offset)+str(cats)).hexdigest()
        userstats=memcache.get(key)
        if userstats:
            return userstats
        """
        if cats:
            for cat in cats:
                records=UserKnowledgeModel.all().filter("username =",user.username).filter("category =",cat).order("-pct").fetch(limit,offset)
                for record in records:
                    results.append(record)
        else:
            results=UserKnowledgeModel.all().filter("username =",user.username).order("-pct").fetch(limit,offset)
            
        userstats=sorted(results, key=lambda result: result.pct,reverse=True)   
        
        #memcache.set(key,userstats,3600)
        
        return userstats
    
    def getRelativeUserStats(user,greater=False,lesser=False,categories=None,limit=10):
        
        results=[]
        
        if not user or not user.username:
            return results
        
        key='kl_getRUS'+hashlib.md5(user.username+"_"+str(limit)+str(greater)+str(lesser)+str(categories)).hexdigest()
        data=memcache.get(key)
        if data:
            return data
        
        records=[]
        
        if categories:
            for cat in categories:
                uks=UserKnowledgeModel.all().filter("username =",user.username).filter("category =",cat).fetch(limit,0)
                for uk in uks:
                    records.append(uk)
        else:
            records=UserKnowledgeModel.all().filter("username =",user.username).fetch(limit,0)
            
        for record in records:
            if greater:
                condition=">"
                sortorder=""
            if lesser:
                condition="<"
                sortorder="-"
                
            uk=UserKnowledgeModel.all().filter("category =",record.category).filter("score "+condition,record.score).order(sortorder+"score").get()
            if uk:
                results.append(uk)
                
       
            #record.pct=math.ceil((record.score/(KnowledgeLib.getMaxScore(record.category)))*10000)/100
            
        #data=sorted(results, key=lambda result: result.pct,reverse=True)
        
        memcache.set(key,results,3600)
        return results
    """
    def oldgetRelativeUserStats(user,greater=False,lesser=False,category=None,limit=10):
        results=[]
        
        if not user:
            return results
        
        if category:
            uks=UserKnowledgeModel.all().filter("user =",user).filter("category =",category).fetch(limit,0)
        else:
            uks=UserKnowledgeModel.all().filter("user =",user).fetch(limit,0)
            
        for uk in uks:
            if greater:
                condition=">"
                sortorder=""
            if lesser:
                condition="<"
                sortorder="-"
                
            record=UserKnowledgeModel.all().filter("category =",uk.category).filter("score "+condition,uk.score).order(sortorder+"score").get()
            if record:
                results.append(record)
                
        foo=sorted(results, key=lambda result: result.score,reverse=True)
        
        for record in foo:
            #logging.info(stat.category.name)
            record.suser=SparseUser(record.user)
            record.user=None
            record.pct=math.ceil((record.score/(KnowledgeLib.getMaxScore(record.category)))*10000)/100
        
        return foo
    """
    
    """
    return the highest possible score for this category
    : the sum of all points for all questions tagged with this category (one question can have a maximum of 3 points)
    """
    def getMaxScore(category):
        #TODO: cache invalidate
        key='kl_getMS_'+category.name
        data=memcache.get(key)
        #data=False
        if data:
            return data
        
        numquestions=QuestionModel.all().filter("cats in",[category]).count()
        
        if numquestions:
            maxscore=numquestions*2 # where two is the maximum number of points that a question can have
        else:
            maxscore=0
            
        #logging.info("maxscore for category "+category.name+" is "+str(maxscore))
        memcache.set(key,maxscore,3600)
        
        return maxscore
        
        """
        if records:
            return records[0].score
        else:
            return 0
        """
        
    def getTopUsers(category,limit=10):
        key='kl_getTU'+category.name
        data=memcache.get(key)
        if data:
            return data
        records=UserKnowledgeModel.all().filter("category =",category).order("-score").fetch(limit,0)
        
            #record.pct=math.ceil((record.score/(KnowledgeLib.getMaxScore(record.category)))*10000)/100
            
        #data=sorted(records, key=lambda record: record.pct,reverse=True)
        
        memcache.set(key,records,3600)
        
        return records
    
    def getUserCategoryScore(username,category):
        key='kl_getUCS2'+category.name
        score=memcache.get(key)
        if score:
            return score
        record=UserKnowledgeModel.all().filter("username =",username).filter("category =",category).get()
        
        if record:
            score= record.score
        else:
            score=0.0
            
        memcache.set(key,score,3600)
        
        return score
    
    getTopUsers=staticmethod(getTopUsers)
    calculate_user_knowledge=staticmethod(calculate_user_knowledge)
    getLeaderBoard=staticmethod(getLeaderBoard)
    getUserStats=staticmethod(getUserStats)
    getRelativeUserStats=staticmethod(getRelativeUserStats)
    getMaxScore=staticmethod(getMaxScore)
    getUserCategoryScore=staticmethod(getUserCategoryScore)
    
    