from pydantic import BaseModel
from typing import List

class UserCreate(BaseModel):
    name: str
    email: str

class QuestionCreate(BaseModel):
    question_text: str
    correct_option: str
    options: List[str]
    difficulty: str

class TriviaCreate(BaseModel):
    name: str
    description: str
    question_ids: List[int]
