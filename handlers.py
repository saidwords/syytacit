import os
import datetime
import webapp2
from django.template import loader

class BaseHandler(webapp2.RequestHandler):
    def render_to_response(self, template_name, template_values):
        self.response.write(loader.render_to_string(template_name, template_values))

class PageHandler(BaseHandler):
    def root(self):
        now = datetime.datetime.now()
        ten_min_ago = now - datetime.timedelta(minutes=10)
        context = {
            'now': now,
            'ten_min_ago': ten_min_ago
        }
        return self.render_to_response('test_filters.html', context)
