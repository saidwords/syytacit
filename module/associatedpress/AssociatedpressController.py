# coding=UTF-8
# -*- coding: UTF-8 -*-
from common.lib.Controller import Controller
from module.associatedpress.lib.AssociatedPressLib import AssociatedPressLib
from module.home.HomeController import HomeController
from module.home.view.NullView import NullView

class AssociatedpressController(Controller):
    def acquire_latest_headlinesAction(self):
        if not self.authenticate("admin"):
            return HomeController().indexAction()
        aplib=AssociatedPressLib()
        aplib.save_latest_headlines()
        return NullView()