from common.models.BaseModel import BaseModel
class UtestModel(BaseModel):
    status=None
    tests=[]
    errors=[]
    failures=[]
    methods=[]
    messages=[]
