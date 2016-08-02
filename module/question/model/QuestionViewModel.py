from common.models.BaseModel import BaseModel
class QuestionViewModel(BaseModel):
    questions=[]
    cats=[]
    page=1
    limit=10