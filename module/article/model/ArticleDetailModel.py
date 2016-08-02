from common.models.BaseModel import BaseModel

class ArticleDetailModel(BaseModel):
    article=None
    tags=""
    comment_key=None
    leaderboard=None
    userstats=None
    greater_userstats=None
    lesser_userstats=None
    comments=[]