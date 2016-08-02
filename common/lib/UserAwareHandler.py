from webapp2_extras import sessions, auth
import webapp2
    
class UserAwareHandler(webapp2.RequestHandler):    
    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(backend="memcache")
    
    def dispatch(self):        
        try:
            super(UserAwareHandler, self).dispatch()
        finally:
            # Save the session after each request        
            self.session_store.save_sessions(self.response)