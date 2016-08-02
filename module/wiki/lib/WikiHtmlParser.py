from HTMLParser import HTMLParser

# create a subclass and override the handler methods
class WikiHtmlParser(HTMLParser):
    capture=False
    ignore=False
    text=""
    def handle_starttag(self, tag, attrs):
        if tag=='p':
            self.capture=True
        if tag=='sup':
            self.ignore=True
            
    def handle_endtag(self, tag):
        if tag=='p':
            self.capture=False
        if tag=='sup':
            self.ignore=False
        
    def handle_data(self, data):
        if self.capture and not self.ignore:
            self.text=self.text+data+" "