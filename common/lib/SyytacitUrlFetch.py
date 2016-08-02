from google.appengine.api import urlfetch, memcache
class SyytacitUrlFetch:
    def fetch(url, payload=None, method=urlfetch.GET, headers={},allow_truncated=False, follow_redirects=True,deadline=None, validate_certificate=None,cache=True):
        urlFetchResult=None
        if cache:
            urlFetchResult=memcache.get('urlfetch_'+url)
        if not urlFetchResult:
            fetchResult = urlfetch.fetch(url,payload,method,headers,allow_truncated,follow_redirects,deadline,validate_certificate)
            urlFetchResult=SyytacitUrlFetchResult()
            urlFetchResult.content=fetchResult.content
            urlFetchResult.status_code=fetchResult.status_code
            urlFetchResult.final_url=fetchResult.final_url
            
            memcache.set('urlfetch_'+url,urlFetchResult,3600)
        
        return urlFetchResult
    
    fetch=staticmethod(fetch)
    
class SyytacitUrlFetchResult(object):
    content=None
    final_url=None
    status_code=None
        
        
        