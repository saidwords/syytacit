from google.appengine.api import urlfetch
from django.utils import simplejson, html
from module.opencalais.model.OCSocialTag import OCSocialTag


class OpenCalais:
    ENTRYPOINT='http://api.opencalais.com/tag/rs/enrich'
    #ENTRYPOINT='http://localhost/oc.html'
    LICENSEID='s5bxa4t64tygxuhmht2gd4za'
    
    CONTENTTYPE_XML='text/xml; charset=UTF-8'
    CONTENTTYPE_HTML='text/html; charset=UTF-8'
    CONTENTTYPE_HTMLRAW='text/htmlraw; charset=UTF-8'
    CONTENTTYPE_RAW='text/raw; charset=UTF-8'
    
    OUTPUTFORMAT_XMLRDF='XML/RDF'
    OUTPUTFORMAT_TEXTSIMPLE='Text/Simple'
    OUTPUTFORMAT_TEXTMICROFORMATS='Text/Microformats'
    OUTPUTFORMAT_APPLICATIONJSON='Application/JSON'
    OUTPUTFORMAT_TEXTN3='text/N3'

    # (could combine comma-separated options: "GenericRelations,SocialTags"
    METADATATYPE_GENERICRELATIONS='GenericRelations' # to enable Generic Relations
    METADATATYPE_SOCIALTAGS='SocialTags' # to enable Social Tags
    
    def classify(content):
        tags=[]
        
        headers={}
        headers["x-calais-licenseID"]=OpenCalais.LICENSEID
        headers["Content-Type"]=OpenCalais.CONTENTTYPE_HTML
        headers["accept"]=OpenCalais.OUTPUTFORMAT_APPLICATIONJSON
        headers["enableMetadataType"]="SocialTags"
        
        #headers["calculateRelevanceScore"]=True;
        import HTMLParser
        #import re
        h = HTMLParser.HTMLParser()
        content=unicode(content,errors="replace")
        #pattern = r"(?is)(<script[^>]*>)(.*?)(</script>)"
        #content=re.sub(pattern, '\1\3', content)
        #pattern = r"(?is)(<style[^>]*>)(.*?)(</style>)"
        #content=re.sub(pattern, '\1\3', content)
        #content= html.strip_tags(content)
        content=h.unescape(content)
        content=content.encode("ascii",errors="ignore")
        
        urlFetchResult = urlfetch.fetch(OpenCalais.ENTRYPOINT,content,urlfetch.POST,headers,False,True,60)
        
        oc=simplejson.loads(urlFetchResult.content)
        
        importance=0.0
        #return oc
        for k in oc.keys():
            if k=='doc':
                continue
            if oc[k].has_key('_typeGroup'):
                tag=None
                if oc[k]['_typeGroup']=='socialTag':
                    tag=oc[k]['name']
                    if oc[k].has_key('importance'):
                        importance=float(oc[k]['importance'])
                        if importance > 0:
                            tags.append(OCSocialTag(tag,importance))   
                                                
                #elif oc[k]['_typeGroup']=='topics':
                #    tag=oc[k]['categoryName']
                #    if oc[k].has_key('score'):
                #        importance=float(oc[k]['score'])   
        
        return tags
    
    classify=staticmethod(classify)
        