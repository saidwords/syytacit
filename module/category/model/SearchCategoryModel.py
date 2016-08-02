from common.models.BaseModel import BaseModel
class SearchCategoryModel(BaseModel):
    categories=[]
    nextpage=2
    previouspage=1
    page=1
    limit=20
    num_records=0
    terms=""
    sort=None
    sort_order=None
    user=None
    