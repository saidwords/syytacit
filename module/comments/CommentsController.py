# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.home.view.NullView import NullView
from module.comments.model.Comments import Comments
from module.comments.model.CommentThread import CommentThread
from module.comments.lib.CommentsLib import CommentsLib


class CommentsController(Controller):
    def defaultController(self,segments,qs):
        return self.indexAction()
    
    def indexAction(self):
        return NullView(None)

    def getcommentsAction(self,comment_key,maxlevels=3,page=0,limit=10):
        model=CommentThread()
        try:
            i=int(page);page=i;
            i=int(limit);limit=i
            i=int(maxlevels);maxlevels=i
        except ValueError:
            page=0
            limit=10
            maxlevels=3
    
        comment=Comments.get(comment_key);
        
        model.responses=CommentsLib.getComments(comment,self.user,page,limit)
            
        return NullView(model)
   
    
    def deleteAction(self,comment_key):
        if not self.user:
            raise Exception('you must be logged in')
        
        model={"comment_key":"","delta":0}
        
        comment=Comments.get(comment_key)
        if comment:
            # only allow the creatoror the admin to delete the comment
            if comment.username != self.user.username and not self.isLoggedInAs('admin'):
                raise Exception('you do not have permission to delete this comment')
            """    
            children=Comments.all().filter("parent_comment =",comment.key()).fetch(255, 0)
            for child_comment in children:
                child_id=child_comment.key().id()
                self.deleteAction(child_id)
            """
            # flag the comment as deleted
            comment.deleted=True
            comment.save()
            
            model['comment_key']=comment_key
            model['delta']=-1;
            
        else:
            raise Exception('comment not found');
        
        return NullView(model)
    
    """
    @param article_key - the key of the article that the comment is being attached to
    @param parent_key- the key of the comment to which the user is commenting on
    @param comment - the text of the comment
    """
    def savecommentAction(self,article_key,comment,parent_key=None):
        if not self.user:
            raise Exception('You must be logged in')
        
        if len(comment)==0:
            raise Exception('Comment must not be empty')
        
            
        model={"comment_key":"","parent_key":parent_key,"delta":0}
        
        c=CommentsLib.saveComment(article_key,comment,parent_key,self.user)
        
        #logging.info("saved comment "+str(parent_key))
        
        if c:
            model['comment_key']=str(c.key())
            model['delta']=1
            model['date']=c.updated.strftime("%A %d. %B %Y")
            model['user']=self.user
         
        return NullView(model)
    
    def approveAction(self,article_key,comment_key,approve=True):
        
        if not self.user:
            raise Exception('You must be logged in')
        
        if approve=='true' or approve==True:
            approve=True
        else:
            approve=False
            
        response=CommentsLib.approveComment(self.user, article_key, comment_key,approve)
        model={"n":response}
        
        
        return NullView(model)
    
    def rejectAction(self,article_key,comment_key):
        
        return self.approveAction(article_key,comment_key,False)
            
      