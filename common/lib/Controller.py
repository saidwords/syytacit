# coding=UTF-8
# -*- coding: UTF-8 -*-

from common.models.UserProperties import UserProperties
from common.lib.Users import Users

class Controller():
    errorcode=None
    user=None
    
    def __init__(self):
        self.user=Users.get_current_user()
     
    def error(self,code):
        self.errorcode=code
        
    def isLoggedInAs(self,usertype=None):
        
        if not self.user or not self.user.username:
            return False
        
        if usertype:
            properties=UserProperties.all().filter("username =",self.user.username).get()
            if properties and usertype in properties.roles:
                return True
            else:
                return False
        
        
    def requireLoggedin(self,usertype=None,redirect=False):
        
        if not self.user or not self.user.username:
            self.error(403)
            raise Exception("You must be logged in")
        
        if usertype:
            properties=UserProperties.all().filter("username =",self.user.username).get()
            if properties and usertype in properties.roles:
                return True
            else:
                self.error(403) 
                raise Exception("You do not have "+usertype+" permissions")
        
        
                