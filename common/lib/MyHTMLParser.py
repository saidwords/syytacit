# coding=UTF-8
# -*- coding: UTF-8 -*-
from HTMLParser import HTMLParser
import re
import htmlentitydefs

class MyHTMLParser(HTMLParser):
    title=''
    description=''
    tag=None
    def handle_starttag(self, tag, attrs):
        self.tag=tag
    def handle_endtag(self, tag):
        self.tag=tag
    def handle_data(self,data):
        if self.tag=='title':
            self.title=self.title+data
            
    def getTitle(self,html):
        regex=re.compile("<title[^>]*>([^\"]*)</title>",re.IGNORECASE)
        search_result= regex.search(html)
        if search_result!= None:
            self.title=re.sub("\s\s+" , " ",search_result.group(1)).strip()
            #self.title=self.html_entity_decode(self.title)

    def getDescription(self,html):
        regex =  re.compile( r'<META\s*NAME\s?=\s?[\'"]DESCRIPTION[\'"].*?CONTENT\s?=\s?[\'"]([^\"]*)[\'"]', re.IGNORECASE)
        search_result = regex.search(html)
        if search_result != None:
            self.description=re.sub("\s\s+" , " ",search_result.group(1)).strip()
            #self.description=self.html_entity_decode(self.description)

    def html_entity_decode_char(self,m, defs=htmlentitydefs.entitydefs):
        try:
            return defs[m.group(1)]
        except KeyError:
            return m.group(0)
    
    def html_entity_decode(self,string):
        pattern = re.compile("&(\w+?);")
        return pattern.sub(self.html_entity_decode_char, string)
