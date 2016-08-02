# coding=utf-8
import os
import webapp2
from common.lib.Users import Users
from module.api.view.JSONView import JSONView
import types
from module.home.HomeController import HomeController
import traceback


# Must set this env var before importing any part of Django
# 'project' is the name of the project created with django-admin.py

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
# Force Django to reload its settings.
from django.conf import settings
settings._target = None

import urllib
import sys
import logging
import inspect
from common.lib.View import View
from common.lib.UserAwareHandler import UserAwareHandler

#class Main(webapp2.RequestHandler):
class Main(UserAwareHandler):
    controller=None
    method=None
    segments=[]
    application_environment="DEV"
    
    def handle_exception(self, exception, debug):
        if debug:
            self.RequestHandler.handle_exception(self, exception, debug)
        else:
            logging.exception(exception)
            self.error(500)
            self.response.out.write("an error ocurred")

    def post(self):
        return self.get()
    
    def get(self):
        # turn on maintenance mode
        #view= HomeController().maintenanceAction()
        #self.response.out.write(view.render())
        #return None
        isjson=False
        if len(self.request.path.strip('/')):
            self.segments=urllib.unquote_plus(self.request.path).strip('/').split('/')
        else:
            self.segments=[]
            
        if len(self.segments) > 0:
            if self.segments[0]=='json':
                if len(self.segments)>1:
                    self.controller=self.segments[1].lower()
                isjson=True
                from webapp2_extras import json
                self.segments.pop(0)
            elif self.segments[0]=='community':
                self.controller='community'
                if len(self.segments)>1:
                    if self.segments[1]!='search':
                        self.segments.insert(1, 'default')
                
            else:
                self.controller=self.segments[0].lower()
        else:
            self.controller='home'
            
        if len(self.segments) > 1:    
            self.method=self.segments[1].lower()
        elif len(self.segments)==1:
            try:
                page=int(self.segments[0])
                self.segments[0]='home'
                self.segments.append('articles')
                self.method='articles'
                self.controller='home'
                self.segments.append(page)
                
            except ValueError:
                self.method='default'
        else:
            self.method='default'
                
            
        className=self.controller.capitalize()+'Controller'
        
        # get the controller
        try:
            __import__('module.'+self.controller+'.'+className)
            module=sys.modules['module.'+self.controller+'.'+className]
            controller=getattr(module,className);
        except Exception as e:
            stacktrace = traceback.format_exc()
            logging.error("%s", stacktrace)
            self.controller='home';
            import module.home.HomeController
            module=sys.modules['module.home.HomeController']
            controller=getattr(module,'HomeController');
            self.method='fourzerofour'
            
        #get the function
        try:    
            function=getattr(controller,self.method+'Action')  
        except Exception:
            stacktrace = traceback.format_exc()
            logging.error("%s", stacktrace)
            self.controller='home';
            self.method='fourzerofour'
            className=self.controller.capitalize()+'Controller'
            __import__('module.'+self.controller+'.'+className)
            module=sys.modules['module.'+self.controller+'.'+className]
            controller=getattr(module,className);
            function=getattr(controller,'fourzerofourAction')
            
        if self.segments:
            self.segments.pop(0)
        if self.segments:
            self.segments.pop(0)
            
        foo=inspect.getargspec(function)
        argspec=foo[0]
        if argspec:
            argspec.pop(0)
            
        i=0;funcargs={};numsegments=len(self.segments)
        

        qs={}
        is_array = lambda var: isinstance(var, (list, tuple))
        # POSTED data overrides url segment data
        if self.request.POST.multi: 
            for (key,value) in self.request.POST.multi._items:
                if key.endswith('[]'):
                    key=key[0:-2]
                    if qs.has_key(key):
                        if is_array(qs[key]):
                            qs[key].append(value)
                        else:
                            qs[key]=[value]
                    else:
                        qs[key]=[value]

                else:
                    qs[key]=value
        # GET data overrides POSTED dat a            
        if self.request.GET.multi:
            for (key,value) in self.request.GET.multi._items:
                if key.endswith('[]'):
                    key=key[0:-2]
                    if qs.has_key(key):
                        if is_array(qs[key]):
                            qs[key].append(value)
                        else:
                            qs[key]=[value]
                    else:
                        qs[key]=[value]

                else:
                    qs[key]=value
           
        for varname in argspec:
            if i<numsegments:
                funcargs[varname]=self.segments[i]
                i=i+1
            if qs.has_key(varname):
                funcargs[varname]=qs[varname]
                
        # #convert javascript data-types to python
        for key,value in enumerate(funcargs):
            if funcargs[value]=='null':
                funcargs[value]=None
            elif funcargs[value]=='true':
                funcargs[value]=True
            elif funcargs[value]=='false':
                funcargs[value]=False
        
        # execute the controller::action()
        instance=controller()
        
        try:
            model=getattr(controller,self.method+'Action')(instance,**funcargs)
        except Exception, e:
            stacktrace = traceback.format_exc()
            logging.error("%s", stacktrace)
            if not instance.errorcode:
                instance.errorcode=500                
            #TODO: return the error page
            model={"exception":{"type":e.__class__.__name__,"message":e.message}}
        
        if instance.errorcode:
            self.response.set_status(instance.errorcode)
       
        if isinstance(model, View):
            if not model.model:
                model.model={"exception":None}
            else:
                typ=type(model.model)
                if typ==types.DictType:
                    if not model.model.has_key('exception'):
                        model.model['exception']=None;
                elif isinstance(model.model, object):
                    if not hasattr(model.model, 'exception'):
                        model.model.exception=None;
            if isjson:
                #TODO: send json header?
                #self.response.out.write(json.encode(model.model))
                response=JSONView.object_to_dict(model.model)
               
                self.response.out.write(json.encode(response))
            else:
                #model.model['revision']=os.environ['CURRENT_VERSION_ID']
                typ=type(model.model)
                if typ==types.DictType:
                    model.model['revision']=os.environ['CURRENT_VERSION_ID'];
                    model.model['application_environment']=self.application_environment
                elif isinstance(model.model, object):
                    model.model.revision=os.environ['CURRENT_VERSION_ID'];
                    model.model.application_environment=self.application_environment
                    
                self.response.out.write(model.render())
        else:
            if model==None:
                model={"exception":None}
            elif not model.has_key("exception"):
                model['exception']=None;
                    
            # we got raw data here, 
            if isjson:
                #TODO: send json header?
                response=JSONView.object_to_dict(model)
                self.response.out.write(json.encode(response))
            else:                
                #try to apply the default html template
                filename=os.path.dirname(__file__)+'/module/'+self.controller+"/view/"+self.method+".html";
                if os.path.isfile(filename):
                    from django.template import loader
                    model.revision=os.environ['CURRENT_VERSION_ID']
                    model.application_environment=self.application_environment
                    self.response.out.write(loader.render_to_string(filename, {"model": model}))
                else:
                    self.response.out.write("")
                    
               
config = {
          'webapp2_extras.auth': {
            'user_model': 'webapp2_extras.appengine.auth.models.User',
               'session_backend':'memcache',
               'cookie_name':'syytacit',
               'user_attributes': ['auth_ids']
            }
}     
config['webapp2_extras.sessions'] = {
    'secret_key': '2014-03-22 18:05:08'
 
}

app = webapp2.WSGIApplication([('/.*', Main),], debug=False,config=config)

