from fastapi import FastAPI, Path
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date 
import sqlite3


# Create a new database connection object 
db_connection = sqlite3.connect('students.db')

# Create a cursor object to execute your various queries 
cursor = db_connection.cursor()

app = FastAPI()


# Student Class Schema used to define the student model 

class Student(BaseModel):
    id: int = Field(default=None, ge=1, description="Auto-generated unique ID")
    firstName: str
    lastName: str
    email: str = Field(default=None,  description="Email Address and must be unique")
    dateOfBirth: date 

# used to store information about the students 
studentInformation = {
    1:{
    "id": "1",
    "firstName": "Tegue",
    "lastName": "Brown",
    "email": "brown@gmail.com",
    "dateOfBirth": "09/11/1999"
    }
}

# Serving the Endpoint requests 

# 1 - Create a new student 
@app.post("/students")
def create_Student(student: Student, student_id: int):
    if student_id in studentInformation:
        return {"Error": "A student with this ID already exists"}
    studentInformation[student_id] = student

    return studentInformation[student_id]

# 2 - get student by ID 
@app.get("/students/{student_id}")
def get_StudentBy_ID(student_id: int = Path( description="Student ID as path parameter")):
    for student in studentInformation:
        if student == student_id:
            return studentInformation[student_id]
        
# 3 - Update student information 
@app.put("/students/{student_id}")
def update_Student(student_id: int , student: Student):
    if student_id in studentInformation:
        studentInformation[student_id].update(student)
        return studentInformation[student_id]
    return {"Error": "Student not found"}
    
# 4 - Delete a student 
@app.delete("/students/{student_id}")
def delete_Student(student_id: int):
    stud = studentInformation[student_id]
    del studentInformation[student_id]
    return {
        "Deleted Info !!": stud
    }

@app.get("/students/")
def get_All_Students():
    return studentInformation