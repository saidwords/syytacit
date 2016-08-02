from django.template import loader
import os

class View(object):
    errorcode=None
    model=None

    def __init__(self, model=None):
        self.model=model
    def render(self):
        filename=self.__module__.replace('.','/')+'.html'
        return loader.render_to_string(filename, {"model": self.model})
        