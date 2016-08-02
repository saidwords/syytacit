# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.admin.model.AdminModel import AdminModel
import datetime
from module.admin.view.AdminView import AdminView
from module.home.HomeController import HomeController
import logging

class AdminController(Controller):
    def defaultAction(self,segments,qs):
        return self.indexAction()
    
    def indexAction(self):
        model=AdminModel()
        if not self.authenticate("admin"):
            return HomeController().indexAction()
            
        model.todaydate=datetime.datetime.now()
        return AdminView(model)
