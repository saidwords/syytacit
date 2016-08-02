# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.home.HomeController import HomeController

class AboutController(Controller):
    
    def defaultAction(self):
        return HomeController().aboutAction()