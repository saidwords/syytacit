from common.models.BaseModel import BaseModel
class UserHome(BaseModel):
    username=None
    user1=None
    user_date_established=None
    user_date_elapsed=None
    comments=[]
    articles=[]
    aprovals=[]
    categories=[]
    userstats=[]
    rejected_articles=[]
    approved_articles=[]
    rejected_comments=[]
    approved_articles=[]
    numarticles=0
    numcomments=0
    numrejected_articles=0
    numapproved_articles=0
    numrejected_comments=0
    numapproved_articles=0
    nextpage=0
    prevpage=0
    section="articles"
    leaderboard=None
    userstats=None
    lesser_userstats=None
    greater_userstats=None
    