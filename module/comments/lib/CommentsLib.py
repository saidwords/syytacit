# coding=UTF-8
# -*- coding: UTF-8 -*-
from module.article.model.ArticleModel import ArticleModel
from module.comments.model.CommentThread import CommentThread
from module.comments.model.Comments import Comments
import logging
from common.models.UserKnowledgeModel import UserKnowledgeModel
from module.comments.model.CommentApproveModel import CommentApproveModel
from common.lib.Users import Users
from google.appengine.api import memcache

class CommentsLib:
    def v1_getComments(self,comment,level=0,maxlevel=3):
        comments=Comments.all().filter("parent_comment =",comment.key()).fetch(10)
        return comments
    
    def getComments(parent_comment,user,page=0,limit=10):
        #logging.info("page="+str(page)+" limit="+str(limit))
        
        comments=[]
       
        p=Comments.all().filter("parent_comment =",parent_comment.key()).order("-rank").fetch(limit,page*limit)
        #logging.info("2 there are "+str(len(p))+" responses to "+str(parent_comment.key()))
        for comment in p:
            response=CommentThread()
            if comment.deleted:
                response.comment='deleted'
            else:
                response.comment=comment.text
                
            response.rank=comment.rank
            #response.comment_key=comment.key().id()
            response.comment_key=comment.key()
            response.username=comment.username
            response.date=comment.updated.strftime("%A %d. %B %Y")
            if user:
                approved=CommentsLib.getApproval(comment,user)
                if approved==True:
                        response.approved='1'
                elif approved==False:
                    response.approved='0'
                else:
                    response.approved=None
            else:
                response.approved=None
                
            #logging.info(str(parent_comment.key())+" -> "+str(comment.key()))
           
            response.responses=CommentsLib.getComments(comment,user,0,limit)
            
           
            comments.append(response)
        return comments
    
    def saveComment(article_key,comment,parent_key=None,user=None):
        comment=unicode(comment,"UTF-8")
        # if the user has already commented on this article then dont let him comment again. He should just append to his existing comment.
        # calculate rank based on users knowledge in each category matching the categories of the article.
        if parent_key:
            parent_comment=Comments.get(parent_key)
            if parent_comment:
                existing_comment=Comments.all().filter("parent_comment =",parent_comment).filter("username =",user.username).get()
                if existing_comment:
                    logging.warn("user has already commented")
                    return existing_comment;
          
                
        a=ArticleModel.get(article_key)
        
        if not a:
            raise Exception("Article not found")
        """            
        
        existing_comment=Comments.all().filter("parent_comment =",a.comment).filter("user =",user).get()
        if existing_comment:
            logging.info("2. user has already commented")
            return existing_comment;
        """
        from module.article.lib.ArticleLib import ArticleLib
        articlecats=ArticleLib.getArticleCategories(a);
        rank=0.0
        userknowledge=Users.getUserKnowledge(user.username)
        for acat in articlecats:
            if userknowledge.has_key(acat.category.name):
                rank=0.0+rank+(acat.catscore*userknowledge[acat.category.name].score)
                if rank > 4223372036854775807:
                    rank=65535.0
                    logging.ERROR("rank exceeds maxint")
                    
        if rank==0.0:
            rank=0.1
                       
        c=None
        if parent_key:
            p=Comments.get(parent_key)
            if p:
                c=Comments(parent_comment=p,text=comment,rank=rank,username=user.username)
                c.save()
        elif a:
            if a.comment:
                
                c=Comments(parent_comment=a.comment,text=comment,rank=rank,username=user.username)
                c.save()
            else:# if the article has no comments then create a NULL comment for the article
                nr=Comments(text="null",rank=rank,username=user.username)
                nr.save();
                
                c=Comments(parent_comment=nr,text=comment,rank=rank,username=user.username)
                c.save()
                a.comment=nr
            if a.numcomments==None:
                a.numcomments=0
                
        if a and c:
            a.numcomments=a.numcomments+1
            a.save()
            memcache.incr("ncomments_"+article_key,1,None,a.numcomments-1)
        
        return c
    
    def countComments(parent_comment,page=0,limit=10):
        
        numcomments=0
        #p=Comments.all().filter("parent_comment =",comment.key()).order("updated").fetch(limit,page*limit)
        #TODO: find a way to prevent the top commenter from filling the front page of comments with only his comments
        comments=True
        
        while comments:
            comments=Comments.all(keys_only=True).filter("parent_comment =",parent_comment).fetch(limit,page*limit)
            for comment in comments:
                numcomments=1+numcomments+CommentsLib.countComments(comment,0,limit)
            page=page+1
               
        return numcomments
    
    def approveComment(user,article_key,comment_key,approve=True):
        
        comment=Comments.get(comment_key)
        if not comment:
            return False
        
        article=ArticleModel.get(article_key)
        if not article:
            return False
        
        if user.username == comment.username:
            raise Exception("you cannot approve/reject your own comment!")
            
        from module.article.lib.ArticleLib import ArticleLib
        article_cats=ArticleLib.getCategories(article)
        rank=0.0
        for category in article_cats:
            comment_approval=CommentApproveModel.all().filter("comment =",comment).filter("username =",user.username).filter("category =",category).get()
            if not comment_approval: # Do not allow a user to re-approve the comment once the user has already approved the comment
                comment_approval=CommentApproveModel(username=user.username,comment=comment,category=category,score=0.01,approve=approve)
                userknowledges=UserKnowledgeModel.all().filter("username =",user.username).filter("category =",category).fetch(1)
                if userknowledges:
                    comment_approval.score=userknowledges[0].score
                
                    if approve==True:
                        rank=rank+comment_approval.score;
                    else:
                        rank=rank-comment_approval.score
                        
                    
                comment_approval.save()
                    
        if rank==0.0:
            rank=0.1
        if comment.rank!=rank:
            comment.rank=comment.rank+rank
            comment.save()
            
        memcache.delete_multi(['cga_'+str(comment_key)+user.username])
                       
        return True
    
    def calculateTopComments():
        
        return None
    
    def getApproval(comment,user):
        if not user or not user.username:
            return None
        
        key='cga_'+str(comment.key())+user.username
       
        approval=memcache.get(key)
        if approval==None:
            approval=CommentApproveModel.all().filter("comment =",comment).filter("username =",user.username).get()
            if approval==None:
                memcache.set(key,False,3600)
            else:
                memcache.set(key,approval,3600)
        elif approval==False:
            approval=None
        
        if approval:
            return approval.approve
        
    def getArticleKey(comment):
        
        if comment.parent_comment:
        
            while comment.parent_comment:
                comment=comment.parent_comment
                
        article_key=ArticleModel.all().filter("comment =",comment).get(keys_only=True)
       
        return article_key
    
    def deleteChildren(comment):
        
        page=0
        limit=100
        children=[1]
        total=0
        while children:
            children=Comments.all().filter("parent_comment =",comment).fetch(limit,page*limit)
            for child in children:
                total=total+CommentsLib.deleteChildren(child)
                child.delete()
                total=total+1
        return total
    
    deleteChildren=staticmethod(deleteChildren)
    calculateTopComments=staticmethod(calculateTopComments)
    getArticleKey=staticmethod(getArticleKey)
    getApproval=staticmethod(getApproval)
    countComments = staticmethod(countComments)        
    getComments = staticmethod(getComments)
    saveComment = staticmethod(saveComment)
    approveComment = staticmethod(approveComment)