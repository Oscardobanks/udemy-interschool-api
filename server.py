from typing import Annotated, List
from fastapi import FastAPI, HTTPException, Depends, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm 
# from pydantic import BaseModel, Field
from jwt.exceptions import InvalidTokenError
from datetime import  timedelta
from jose import ExpiredSignatureError, jwt
from fastapi.middleware.cors import CORSMiddleware
from functions.function import create_access_token, authenticate_student, hash_password, SECRET_KEY, ALGORITHM, get_student, get_Student_marks, authenticate_instructor, get_instructor
from models.model import Token, TokenData, User, UserModel, Grade, Top_Student
from database.db import db_connection, cursor
import sqlite3


ACCESS_TOKEN_EXPIRATION_TIMEOUT = 45

#  set up the token url for obtaining the access token on successful authentication
oauth2_scheme_student = OAuth2PasswordBearer(
    tokenUrl = "auth/login/student",
    scheme_name= "Student Authentication",
    description= "Authentication endpoint for the students"
    )

oauth2_scheme_instructor = OAuth2PasswordBearer(
    tokenUrl= "auth/login/instructor",
    scheme_name= "Instructor Authentication",
    description= "Authentication endpoint for the Instructors"
    )

# declare an instance of the FastAPi object 
app = FastAPI()

# Add CORSMiddleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serving the Endpoint requests

# 1 - Create a new user 
@app.post("/auth/register", 
          response_model = User, 
          tags = ["Instructor"], 
          description = "Register a New User with a specific user Role",
          summary="Create a new user")
async def create_User(user: UserModel, token: Annotated[str, Depends(oauth2_scheme_instructor)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
        # Operation performed at this endpoint
        
        hashed_passwd = hash_password(user.password)
        
        if user.user_role == "student":
            
            try:
                cursor.execute("INSERT INTO students (userName, firstName, lastName, email, dateOfBirth, userRole, hashed_password) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (user.userName, user.firstName, user.lastName, user.email, user.dateOfBirth, user.user_role, hashed_passwd))
                db_connection.commit()
                return {
                    "userName":user.userName,
                    "firstName":user.firstName,
                    "lastName":user.lastName,
                    "email":user.email,
                    "dateOfBirth":user.dateOfBirth,
                    "user_role":user.user_role
                    }
            
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=400, detail="A student with this email already exists")
        
        elif user.user_role == "instructor":
            
            try:
                cursor.execute("INSERT INTO instructors (userName, firstName, lastName, email, dateOfBirth, userRole, hashed_password) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (user.userName, user.firstName, user.lastName, user.email, user.dateOfBirth, user.user_role, hashed_passwd))
                db_connection.commit()
                return {
                    "userName":user.userName,
                    "firstName":user.firstName,
                    "lastName":user.lastName,
                    "email":user.email,
                    "dateOfBirth":user.dateOfBirth,
                    "user_role":user.user_role
                }
            
            except sqlite3.IntegrityError:
                raise HTTPException(status_code=400, detail="A student with this email already exists")
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )


# 2 Endpoint to Edit Student Information
@app.put("/students/updateInfo/{student_id}", 
         tags= ["Instructor"],
         summary="Update Students Information",
         description="Authorized party to retrieve students information using their ID",
         response_model=User)
async def update_student_details(token: Annotated[str, Depends(oauth2_scheme_instructor)],student: UserModel, student_id: int = Path(description="Student ID as path parameter")):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
        # Operation performed at this endpoint
        hashed_passwd = hash_password(student.password)
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        existing_student_info = cursor.fetchone()
        
        if not existing_student_info:
            raise HTTPException(status_code=404, detail="Student not found")

        cursor.execute("""
                        UPDATE students
                        SET userName = ?, firstName = ?, lastName = ?, email = ?, dateOfBirth = ?, hashed_password = ?, userRole = ?
                        WHERE id = ?
                        """, (student.userName, student.firstName, student.lastName, student.email, student.dateOfBirth, hashed_passwd, student.user_role, student_id))
        db_connection.commit()

        updated_student = {
            "userName": student.userName,
            "firstName": student.firstName,
            "lastName": student.lastName,
            "email": student.email,
            "dateOfBirth": student.dateOfBirth,
            "user_role": student.user_role
        }
        
        return User(**updated_student)

    except InvalidTokenError:
            raise credentials_exception
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )


# 3 Endpoint to Edit Instructor Information
@app.put("/instructor/updateInfo", 
         tags= ["Instructor"],
         summary="Update instructors Information",
         description="Authorized party to retrieve instructors information using their ID",
         response_model=User)
async def update_instructor_details(token: Annotated[str, Depends(oauth2_scheme_instructor)], instructor: UserModel, instructor_id: int = Query(description="Student ID as path parameter")):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        authenticate_instructor = get_instructor(username)
        
        if authenticate_instructor is None:
            raise credentials_exception
            
        # Operation performed at this endpoint
        hashed_passwd = hash_password(instructor.password)
        cursor.execute("SELECT * FROM instructors WHERE id = ?", (instructor_id,))
        existing_instructor_info = cursor.fetchone()
        
        if not existing_instructor_info:
            raise HTTPException(status_code=404, detail="instructor not found")

        cursor.execute("""
                        UPDATE instructors
                        SET userName = ?, firstName = ?, lastName = ?, email = ?, dateOfBirth = ?, hashed_password = ?, userRole = ?
                        WHERE id = ?
                        """, (instructor.userName, instructor.firstName, instructor.lastName, instructor.email, instructor.dateOfBirth, hashed_passwd, instructor.user_role, instructor_id))
        db_connection.commit()

        updated_instructor = {
            "userName": instructor.userName,
            "firstName": instructor.firstName,
            "lastName": instructor.lastName,
            "email": instructor.email,
            "dateOfBirth": instructor.dateOfBirth,
            "user_role": instructor.user_role
        }
        
        return User(**updated_instructor)

    except InvalidTokenError:
            raise credentials_exception
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )


# 4 - Get student info by ID
@app.get("/students/{student_id}", 
         tags= ["Instructor"],
         summary="Get Students Information",
         description="Authorized party to retrieve students information using their ID")
async def get_student_by_id(token: Annotated[str, Depends(oauth2_scheme_instructor)], student_id: int = Path(description="Student ID as path parameter")):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
        # Operation performed at this endpoint
        
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
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
            }
        else:
            raise HTTPException(status_code=404, detail="Student not found")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )


# 4 - Get instructor info by ID
@app.get("/instructor/{instructor_id}", 
        tags= ["Instructor"],
        summary="Get instructor Information",
        description="Authorized party to retrieve students information using their ID")
async def get_instructor_by_id(token: Annotated[str, Depends(oauth2_scheme_instructor)], instructor_id: int = Path(description="Instructor ID as path parameter")):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
        # Operation performed at this endpoint
        
        cursor.execute("SELECT * FROM instructors WHERE id = ?", (instructor_id,))
        instructor = cursor.fetchone()
        if instructor:
            return {
                "id": instructor[0],
                "userName": instructor[1],
                "firstName": instructor[2],
                "lastName": instructor[3],
                "email": instructor[4],
                "dateOfBirth": instructor[5],
                "user_role": instructor[6],
            }
        else:
            raise HTTPException(status_code=404, detail="instructor not found")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )


# 5 - Update or Add student information
@app.put("/students/grades/update-Add", 
         response_model= Grade, 
         tags = ["Instructor"], 
         description="Update Existing Student Marks by an Authorized instructor",
         summary="Update existing Records of Students")
async def update_or_Add_student_Record(student_id: int, grade: Grade, token: Annotated[str, Depends(oauth2_scheme_instructor)]):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
    # Operation performed at this endpoint
        # Check if the student exists in the students table
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        existing_student = cursor.fetchone()
        if not existing_student:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student with the ID provided not found")
        
        # Check if the student already has grades in the grades table
        cursor.execute("SELECT * FROM grades WHERE student_id = ?", (student_id,))
        existing_student_grades = cursor.fetchone()
        
        if existing_student_grades:
            # Update the student's grades if they already exist
            cursor.execute("""
                UPDATE grades
                SET pure_maths = ?, chemistry = ?, biology = ?, computer_science = ?, physics = ?
                WHERE student_id = ?
            """, (grade.pure_maths, grade.chemistry, grade.biology, grade.computer_science, grade.physics, student_id))
            
            updated_student_grades = {
                "student_id": student_id,
                "pure_maths": grade.pure_maths,
                "chemistry": grade.chemistry,
                "biology": grade.biology,
                "computer_science": grade.computer_science,
                "physics": grade.physics
            }
        
        else:
            # Insert new grades for the student if they don't already exist
            cursor.execute("""
                INSERT INTO grades (student_id, pure_maths, chemistry, biology, computer_science, physics) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_id, grade.pure_maths, grade.chemistry, grade.biology, grade.computer_science, grade.physics))
            
            updated_student_grades = {
                "student_id": student_id,
                "pure_maths": grade.pure_maths,
                "chemistry": grade.chemistry,
                "biology": grade.biology,
                "computer_science": grade.computer_science,
                "physics": grade.physics
            }
        
        # Commit the changes to the database
        db_connection.commit()
        return Grade(**updated_student_grades)
    
    except InvalidTokenError:
            raise credentials_exception
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )
    except sqlite3.IntegrityError as e:
    # Check if it's a CHECK constraint violation
        if 'CHECK constraint failed' in str(e):
            raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, detail="Grade value exceeds the allowed range (0-20).")
    else:
        # Handle other potential database errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred.")


#  6 - Delete a student
@app.delete("/students/{student_id}", 
            tags= ["Instructor"],
            description="Delete all students' info and Records from the system",
            summary="Delete Student")
async def delete_student(student_id: int, token: Annotated[str, Depends(oauth2_scheme_instructor)]):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
        # Operation performed at this endpoint
        cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        student = cursor.fetchone()
        if student:
            cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
            db_connection.commit()
            return {"Deleted Info": student}
        else:
            raise HTTPException(status_code=404, detail="Student not found")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )


# 7 Delete Instructor
@app.delete("/instructor/{instructor_id}", 
            tags= ["Instructor"],
            description="Delete all students' info and Records from the system",
            summary="Delete instructor")
async def delete_instructor(instructor_id: int, token: Annotated[str, Depends(oauth2_scheme_instructor)]):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
        # Operation performed at this endpoint
        cursor.execute("SELECT * FROM instructors WHERE id = ?", (instructor_id,))
        instructor = cursor.fetchone()
        if instructor:
            cursor.execute("DELETE FROM instructors WHERE id = ?", (instructor_id,))
            db_connection.commit()
            return {"Deleted Info": instructor}
        else:
            raise HTTPException(status_code=404, detail="Instructor not found")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )


# 8 Function to get all students
@app.get("/students", 
         tags=["Instructor"],
         summary="Get All Students from the System",)
async def get_all_students(token: Annotated[str, Depends(oauth2_scheme_instructor)]):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
         # Operation performed at this endpoint
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()

        if students:
            return [
                {
                    "id": student[0],
                    "userName": student[1],
                    "firstName": student[2],
                    "lastName": student[3],
                    "email": student[4],
                    "dateOfBirth": student[5],
                    "user_role": student[6]
                } for student in students
            ]
        else:
            raise HTTPException(status_code=404, detail="No students found")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )



# 9 Function to get all instructors
@app.get("/all-instructors", 
         tags=["Instructor"],
         summary="Get All instructors from the System",)
async def get_all_instructors(token: Annotated[str, Depends(oauth2_scheme_instructor)]):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
         # Operation performed at this endpoint
        cursor.execute("SELECT * FROM instructors")
        instructors = cursor.fetchall()

        if instructors:
            return [
                {
                    "id": instructor[0],
                    "userName": instructor[1],
                    "firstName": instructor[2],
                    "lastName": instructor[3],
                    "email": instructor[4],
                    "dateOfBirth": instructor[5],
                    "user_role": instructor[6]
                } for instructor in instructors
            ]
        else:
            raise HTTPException(status_code=404, detail="No instructor found")

    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )



#  10 Get the student grades, served to an authorized student
@app.get("/my-grades", 
         response_model = Grade, 
         tags = ["Students' Endpoints"], 
         description="Student view his/her grades",
         summary="Student view his/her grades")
async def get_student_grade(student_name: str , token: Annotated[str, Depends(oauth2_scheme_student)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        
        # Token validation issue
        # You are decoding the token to extract username and role in the payload.
        # However, there is no explicit check in your token verification logic to handle invalid tokens properly
        # aside from the InvalidTokenError. if username or role are missing in the payload, that’s also a sign of invalid credentials, 
        # and this case should be handled too.
        if username is None or role is None:
            raise credentials_exception

        if username == student_name:
            token_D = {
                "username": username,
                "role": role
            }
            token_data = TokenData(**token_D)
        
        # if the username in the token doesn't match the student_name parameter provided in the request
        if username != student_name:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to access this student's grade",
                )

    except InvalidTokenError:
        raise credentials_exception
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )
    
    student = get_student(username = token_data.username)
    
    if student is None:
        raise credentials_exception
    
    Student_grades = get_Student_marks(student_id = student["id"])
    
    # Handling the error condition for null value of the Student_grades
    if Student_grades is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No grades found for this student"
        )
    return Grade(
        student_id = Student_grades["Student_id"],
        pure_maths = Student_grades["pure_maths"],
        chemistry = Student_grades["chemistry"],
        biology = Student_grades["biology"],
        computer_science= Student_grades["computer_Science"],
        physics = Student_grades["physics"],
    )



# 11 Retrieve the Top 5 students 
@app.get("/top-students", 
        tags = ["Instructor"], 
        description="Get the top 5 students by an Authorized instructor",
        summary="Retrieve the top 5 most performant student")
async def top_students(token: Annotated[str, Depends(oauth2_scheme_instructor)]):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
    # Operation performed at this endpoint
        cursor.execute("""
                        SELECT
                            students.id, 
                            students.userName, 
                            students.firstName, 
                            students.lastName,
                            (grades.pure_maths + grades.chemistry + grades.biology + grades.computer_science + grades.physics) / 5.0 AS average_marks
                        FROM 
                            students
                        JOIN 
                            grades ON students.id = grades.student_id
                        ORDER BY 
                            average_marks DESC
                        LIMIT 5;
                    """)
        
        # students.id, students.userName, students.firstName, students.lastName:
        # These fields represent the student’s details that will be retrieved along with their calculated average marks
        # (grades.pure_maths + grades.chemistry + grades.biology + grades.computer_science + grades.physics) / 5.0 AS average_marks:
        # This formula sums up the student's marks in the five subjects and divides by 5.0 (to account for the floating-point division) to compute their average.
        # JOIN grades ON students.id = grades.student_id: This joins the grades table with the students table based on the student_id, allowing you to access the student details.
        # The JOIN operation between students and grades ensures that only students who have grades in the grades table are selected.
        # ORDER BY average_marks DESC: Orders the students from the highest to the lowest based on their average marks.
        
        top_students = cursor.fetchall()
        
        if not top_students:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, 
                detail="No students Found")
            
        return [
            {
                "id": student[0],
                "userName": student[1],
                "firstName": student[2],
                "lastName": student[3],
                "average_marks": student[4]
            } for student in top_students
        ]

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A student Records not found")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error: " + str(e))
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )

'''
        Explanation:
        FROM Clause:

        The query starts with the FROM students clause, which indicates that we're primarily selecting data from the students table.
        JOIN Clause:

        The JOIN grades ON students.id = grades.student_id clause is crucial. 
        It creates a relationship between the students table and the grades table by matching the id field from students 
        with the student_id field from grades.
        This means that for every student in the students table, the query will include their corresponding grades from the grades table based 
        on the matching student_id.

        Selection of Grades:

        The selected columns include grades.pure_maths, grades.chemistry, etc. Since the JOIN establishes a relationship between the two tables,
        these columns will be available for selection.
        This allows you to compute the average marks for each student based on their grades.

        Recap:
        The query correctly selects student information and their grades due to the JOIN operation. 
        This operation combines rows from both tables based on the specified condition (students.id = grades.student_id), 
        ensuring that the query retrieves the appropriate grades for each student.

        If a student does not have a corresponding entry in the grades table, that student's information will not be included in the result set, 
        which is a typical behavior of inner joins.

        Alternative Considerations:
        Left Join: If you want to include students who do not have any grades, you could use a LEFT JOIN instead of an INNER JOIN. 
        This would return all students, with NULLs in the grade fields for students without corresponding grade records.
'''


# 12 Retrieve all the student grades  
@app.get("/all-grades", 
        tags = ["Instructor"], 
        description="Get all the students with their grade records",
        summary="get all student grades")
async def view_grades(token: Annotated[str, Depends(oauth2_scheme_instructor)]):
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("username")
        role = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        # UnAuthorized token sent is not granted the permission to use this endpoint
        instructor = get_instructor(username)
        
        if instructor is None:
            raise credentials_exception
            
    # Operation performed at this endpoint
        cursor.execute("""
                        SELECT
                            students.id, 
                            students.userName, 
                            students.firstName, 
                            students.lastName,
                            grades.pure_maths, 
                            grades.chemistry, 
                            grades.biology, 
                            grades.computer_science, 
                            grades.physics
                        FROM 
                            students
                        JOIN 
                            grades ON students.id = grades.student_id
                        ORDER BY 
                            students.id
                    """)
        
        all_student_grades = cursor.fetchall()
        
        if not all_student_grades:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND, 
                detail="No record Found")
            
        return [
            {
                "id": student_grades[0],
                "userName": student_grades[1],
                "firstName": student_grades[2],
                "lastName": student_grades[3],
                "grades": {
                    "pure_maths": student_grades[4],
                    "chemistry": student_grades[5],
                    "biology": student_grades[6],
                    "computer_science": student_grades[7],
                    "physics": student_grades[8]
                }
            } for student_grades in all_student_grades
        ]

    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="A student Records not found")
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error: " + str(e))
    
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
            )



# 12 the student's token route 
@app.post("/auth/login/student", 
          response_model = Token, 
          tags = ["Authentication Endpoints"], 
          description=" Implement token-based authentication",
          summary="Authenticates a student in the system")
async def get_access_token (form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
     # Access the username, password, and role from the form_data object
    username = form_data.username
    password = form_data.password

    #authentication logic here
    student = authenticate_student(username, password)
    
    if not student: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid credentials", 
            headers = {"WWW-Authenticate":"Bearer"}
            )
    
    # define the expiration time on successful authentication 
    access_token_expiration_time = timedelta(minutes = ACCESS_TOKEN_EXPIRATION_TIMEOUT)
    
    #  create the access token 
    access_token = create_access_token(
        data = {
            "username": username,
            "role": student["user_role"] },
        expires_delta = access_token_expiration_time
        )
    #response 
    return Token(
        access_token = access_token,
        token_type = "Bearer",
        role = student["user_role"]
    )


# 13 the instructors' token route
@app.post("/auth/login/instructor", 
          response_model = Token, 
          tags = ["Authentication Endpoints"], 
          description=" Implement token-based authentication",
          summary= "Authenticates an Instructor in the system")
async def get_access_token (form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    # Access the username, password, and role from the form_data object
    username = form_data.username
    password = form_data.password
# Add your authentication logic here, that's validating instructor credentials
    instructor = authenticate_instructor(username, password)
    
    if not instructor: 
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED, 
            detail = "Invalid credentials", 
            headers = {"WWW-Authenticate":"Bearer"}
            )
    
    # define the expiration time on successful authentication 
    access_token_expiration_time = timedelta(minutes = ACCESS_TOKEN_EXPIRATION_TIMEOUT)
    
    #  create the access token 
    access_token = create_access_token(
        data = {
            "username": username,
            "role": instructor["user_role"] },
        expires_delta = access_token_expiration_time
        )
    #response 
    return Token(
        access_token = access_token,
        token_type = "Bearer",
        role = instructor["user_role"]
    )