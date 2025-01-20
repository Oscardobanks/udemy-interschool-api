from pydantic import BaseModel, Field
from datetime import date

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str


class TokenData(BaseModel):
    username: str | None = None 
    role : str | None = None


# class Teacher(BaseModel):
#     username: str 
#     full_name: str | None = None
#     email: str | None = None
#     user_role: str = "Instructor"


# class TeacherInDB(Teacher):
#     hashed_password: str


class User(BaseModel):
    userName: str
    firstName: str
    lastName: str
    email: str = Field(default=None, description="Email Address and must be unique")
    dateOfBirth: date
    user_role: str 



class UserInDB(User):
    hashed_password: str 

class UserModel(User):
    password: str


class Grade(BaseModel):
    student_id: int 
    pure_maths: int
    chemistry: int
    biology: int
    computer_science: int
    physics: int


class Top_Student(BaseModel):
    student_id: int
    student_name: str
    first_name: str
    last_name: str
    average_marks: float