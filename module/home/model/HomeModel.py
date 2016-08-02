from common.models.BaseModel import BaseModel
class HomeModel(BaseModel):
    articles=[]
    tags=None
    page=1
    previouspage=1
    nextpage=2
    question=None
    user=None
    userstats=None
    greater_userstats=None
    lesser_userstats=None
    community=None
    category=None
    base_url=None
    sticky_articles=[]