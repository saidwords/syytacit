# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.example.model.ExampleModel import ExampleModel
import datetime
from module.example.view.ExampleView import ExampleView
from module.wiki.model.WikiCategoryModel import WikiCategoryModel

class ExampleController(Controller):
    def defaultAction(self,segments,qs):
        return self.indexAction()
    
    def indexAction(self,tag=None):
        model=ExampleModel()
        model.todaydate=datetime.datetime.now()
        
        cat=WikiCategoryModel.all().filter("name =",tag).get()
        model.message=cat.numsentences
        return ExampleView(model)