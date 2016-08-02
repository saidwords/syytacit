from common.lib.View import View
from django.utils import simplejson
import types
import inspect
from common.models.BaseModel import BaseModel
import logging
import datetime
from google.appengine.api.datastore_types import Link
from google.appengine.ext import db
import google

class JSONView(View):
    def render(self):
        
        response=JSONView.object_to_dict(self.model)
        
        return simplejson.dumps(response)
        
    def object_to_dict(obj):
        typ=type(obj)
        if typ==types.NoneType:
            return None
        if typ==types.UnicodeType:
            return obj.encode("UTF-8")
        if typ==types.IntType:
            return str(obj)
        if typ==types.LongType:
            return str(obj)
        if typ==types.BooleanType:
            return obj
        if typ==types.StringType:
            return obj
        if typ==types.ListType:
            result=[]
            for value in obj:
                result.append(JSONView.object_to_dict(value))
            return result
       
        result={}
        if typ==types.DictType:
            for prop,value in obj.items():
                if prop[0]!='_':
                    result[prop]=JSONView.object_to_dict(value)
            return result
        
        for prop,value in inspect.getmembers(obj):
            if prop[0]=='_':
                continue;
            typ=type(value)
            if typ==types.IntType:
                result[prop]=value
            elif typ==types.InstanceType:
                for p in vars(obj):
                    if p[0]!='_':
                        result[p]=JSONView.object_to_dict(getattr(obj, p))
            elif typ==types.LongType:
                result[prop]=value
            elif typ==types.FloatType:
                result[prop]=value
            elif typ==types.StringType:
                result[prop]=value
            elif typ==types.DictType:
                result[prop]=value
            elif typ==types.DictionaryType:
                result[prop]=value
            elif typ==types.ListType:
                result[prop]=[]
                for p in value:
                    result[prop].append(JSONView.object_to_dict(p))
            elif typ==types.GetSetDescriptorType:
                result[prop]=value
            elif typ==types.BooleanType:
                result[prop]=value
            elif typ==types.UnicodeType:
                result[prop]=value.encode("UTF-8")
            elif typ==types.NoneType:
                result[prop]=''
            elif typ==types.ObjectType:
                result[prop]=JSONView.object_to_dict(value)
            elif typ==types.InstanceType:
                result[prop]=JSONView.object_to_dict(value)
            elif isinstance(value, db.Model):
                result[prop]=JSONView.object_to_dict(value)
            elif isinstance(value, BaseModel):
                result[prop]=JSONView.object_to_dict(value)
            elif typ==datetime.datetime:
                try:
                    result[prop]=str(value.strftime('%s'))
                except ValueError:
                    result[prop]=None
            elif typ==datetime.timedelta:
                result[prop]=str(value)
            elif typ==types.CodeType:
                pass
            elif typ==types.MethodType:
                pass
            elif typ==types.TypeType:
                pass
            elif typ==types.FunctionType:
                pass
            elif typ==google.appengine.ext.db.Query:
                pass
            elif typ==types.BuiltinFunctionType:
                pass
            elif typ==types.BuiltinMethodType:
                pass
            elif typ==google.appengine.ext.ndb.model.MetaModel:
                pass
            elif typ==Link:
                result[prop]=str(value)
            elif typ==int:
                result[prop]=value
            elif typ==google.appengine.api.datastore_types.Email:
                result[prop]=value
            elif typ==google.appengine.api.datastore_types.Key:
                result[prop]=str(value)
            elif typ==google.appengine.api.datastore_types.Integer:
                result[prop]=str(value)
            else:
                logging.info('unsupported data type: '+str(typ)+' '+prop)
                
        
        return result
        
    object_to_dict = staticmethod(object_to_dict)
