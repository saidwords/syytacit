from common.models.BaseModel import BaseModel
class CategoryHomeModel(BaseModel):
    category_name=None
    articles=[]
    leaderboard=None
    userstats=None
    greater_userstats=None
    lesser_userstats=None
    user=None