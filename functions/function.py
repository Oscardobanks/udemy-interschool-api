from fastapi import  HTTPException, HTTPException, status
from datetime import datetime, timedelta, timezone
from jose import  jwt
from passlib.context import CryptContext
from database.db import db_connection, cursor


SECRET_KEY = "58e2fba902c292b2d16cee5dc4280359ffa66218d08ab32d1720492be3069bdf"
ALGORITHM = "HS256"

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")


# to verify password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
    
# to encrypt password
def hash_password(password):
    return pwd_context.hash(password)

# to get student in the student table
def get_student(username: str):
    cursor.execute("SELECT * FROM students WHERE userName = ?", (username,))
    student = cursor.fetchone()
    
    if student:
        
        return {
            "id": student[0],
            "userName": student[1],
            "firstName": student[2],
            "lastName": student[3],
            "email": student[4],
            "dateOfBirth": student[5],
            "user_role": student[6],
            "hashed_password": student[7]
            }
        
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="student not found")

# get the instructor information from the instructor table
def get_instructor(username: str):
    cursor.execute("SELECT * FROM instructors WHERE userName = ?", (username,))
    teacher = cursor.fetchone()
    
    if teacher:
        
        return {
            "id": teacher[0],
            "userName": teacher[1],
            "firstName": teacher[2],
            "lastName": teacher[3],
            "email": teacher[4],
            "dateOfBirth": teacher[5],
            "user_role": teacher[6],
            "hashed_password": teacher[7]
        }
        
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="instructor not found")

# to authenticate student 
def authenticate_student(username: str, password: str):
    student = get_student(username)
    if not student:
        return False
    if not verify_password(password, student["hashed_password"]):
        return False
    return student

# to create an access token 
def create_access_token(data: dict , expires_delta: timedelta | None = None ):
    to_encode = data.copy()
    if expires_delta :
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = 5)
        
    # The error arises because you're trying to include a datetime object (specifically the expire variable) in your JWT token payload. 
    # Python’s json.dumps (which is called internally by the jose library during JWT encoding) cannot handle datetime objects by default.
    # Solution: Convert the datetime object to a string or a UNIX timestamp (which is easily serializable) before adding it to the JWT payload.
    to_encode.update({"exp": expire.timestamp()})
    encoded_jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    
    return encoded_jwt_token

#  Get the Student Grades from the GRade table
def get_Student_marks(student_id: int ):
        cursor.execute("SELECT * FROM grades WHERE student_id = ?", (student_id,))
        Student_Grades = cursor.fetchone()
        if not Student_Grades:
            raise HTTPException (
                status_code= status.HTTP_204_NO_CONTENT, 
                details = "No Content was Found",
                headers = {"WWW-Authenticate":"Bearer"}
            )
            
        return {
            "Student_id": Student_Grades[1],
            "pure_maths": Student_Grades[2],
            "chemistry": Student_Grades[3],
            "biology": Student_Grades[4],
            "computer_Science": Student_Grades[5],
            "physics": Student_Grades[6],
        }

def authenticate_instructor(username: str, password: str):
    instructor = get_instructor(username)
    
    if not instructor:
        return False
    if not verify_password(password, instructor["hashed_password"]):
        return False
    
    return instructor