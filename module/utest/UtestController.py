# coding=UTF-8
# -*- coding: UTF-8 -*-
import os
import sys
import unittest

from module.utest.model.UtestModel import UtestModel
from module.utest.view.UtestView import UtestView
from common.lib.Controller import Controller
from module.home.HomeController import HomeController

class UtestController(Controller):
    def indexAction(self,methods=None):
        model = UtestModel()
        
        if not self.authenticate():
            self.error(404)
            return HomeController().indexAction()
             
        model.tests=[]
        
        if methods==None:
            methods=[]
            
        for module in os.listdir(os.path.dirname(__file__)+'/test/'):
            if module == '__init__.py' or module[-3:] != '.py':
                continue
            __import__('module.utest.test.'+module[:-3])
            # get a list of all test_* functions in the module
            className=module[:-3]
            module=sys.modules['module.utest.test.'+module[:-3]]
            controller=getattr(module,className)
            instance=controller()
            testCases={'cases':[]}
            for methodname in instance.__class__.__dict__.keys():
                if "test_"==methodname[:5]:
                    testCases['cases'].append(methodname)
            del instance
            if len(testCases['cases'])>0:
                testCases['className']=className
                testCases['hide']=True
                model.tests.append(testCases)
        del module
        
        suite = unittest.TestSuite()
        is_array = lambda var: isinstance(var, (list, tuple))
        if not is_array(methods):
            methods=[methods]
                    
        for method in methods:
            tokens=method.split('.');
            module=sys.modules['module.utest.test.'+tokens[0]]
            for test in model.tests:
                if test['className']==tokens[0]:
                    test['hide']=False;
                    
            controller=getattr(module,tokens[0]);
            suite.addTest(controller(tokens[1]))    
              
        runner = unittest.TextTestRunner()
        testResult=runner.run(suite)
        model.status=str('tests: '+str(testResult.testsRun)+' errors: '+str(len(testResult.errors))+' failures: '+str(len(testResult.failures)))
        model.errors=testResult.errors;
        model.failures=testResult.failures;
        model.methods=methods

        return UtestView(model)
    
    def authenticate(self):
        return True
        if self.youser:
            return self.youser.isadmin
        else:
            return False