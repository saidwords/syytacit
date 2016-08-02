class SparseQuestion:
    question=""
    question_type=None
    id=None
    signature=""
    tags=[]
    
    def __init__(self,question=None,question_type=None,id=None,signature=None,tags=None):
        self.question=question
        self.question_type=question_type
        self.id=id
        self.signature=signature
        self.tags=tags
        
        if not self.question:
            self.question=""
        if not self.signature:
            self.signature=""
        if not self.tags:
            self.tags=[]
    