from pydantic import BaseModel 
#Create an object class to contian the string
class UserQuery(BaseModel):
    question: str
