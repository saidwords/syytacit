from google.appengine.api import memcache
import uuid

class Session():
    sessionid=None
    data={}
    def __init__(self,request,response):
        #get the session cookie from the browser. 
        self.sessionid=request.cookies.get('s')
        # if the sessionid doesnt exist, then create it
        if not self.sessionid:
            self.sessionid=str(uuid.uuid4()).replace('-','')
            response.headers.add_header('Set-Cookie', 's='+self.sessionid+'; Path=/; Max-Age=86400;')
        
    def getSessionId(request):
        return request.cookies.get('s')        
    def get(self,keyname):
        if not self.data.has_key(keyname) and self.sessionid:
            self.data[keyname]=memcache.get(self.sessionid+keyname)
            
        return self.data[keyname]
    def set(self,keyname,val):
        self.data[keyname]=val
        if self.sessionid:
            memcache.set(self.sessionid+keyname,val,10800)

    def unset(self,keyname):
        if self.sessionid:
            memcache.delete(self.sessionid+keyname)
        del self.data[keyname]
    def save(self):
        pass
    def destroy(self):
        if self.sessionid:
            for keyname,val in self.data:
                self.unset(self.sessionid+keyname)
            
    getSessionId=staticmethod(getSessionId)