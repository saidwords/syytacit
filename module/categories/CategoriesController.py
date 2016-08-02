# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.category.CategoryController import CategoryController


class CategoriesController(Controller):
    
    def defaultAction(self,terms=None,sort='alphabetical',sort_order='ascending',page=1):
        return CategoryController().searchAction(terms, sort, sort_order, page)