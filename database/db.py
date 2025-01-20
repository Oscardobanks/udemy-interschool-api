import sqlite3

# Create a new database connection object
db_connection = sqlite3.connect('school.db', check_same_thread=False)  # Avoid threading issues with SQLite in FastAPI

# Create a cursor object to execute your various queries
cursor = db_connection.cursor()

db_connection.row_factory = sqlite3.Row  # Enables accessing columns by name

# Create the students table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    userName VARCHAR(255) NOT NULL UNIQUE,
                    firstName TEXT NOT NULL,
                    lastName TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    dateOfBirth DATE NOT NULL,
                    userRole TEXT NOT NULL, 
                    hashed_password TEXT NOT NULL
                )''')

# Commit the changes
db_connection.commit()

# Create Table Grades having a one to many relationship with the student table, with as foreign key the student_id
# Foreign Key Constraint: Ensures referential integrity so that every grade must correspond to a valid student in the students table.
cursor.execute('''CREATE TABLE IF NOT EXISTS grades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL UNIQUE,
                    pure_maths INTEGER NOT NULL CHECK (pure_maths >= 0 AND pure_maths <= 20),
                    chemistry INTEGER NOT NULL CHECK (chemistry >= 0 AND chemistry <= 20),
                    biology INTEGER NOT NULL CHECK (biology >= 0 AND biology <= 20),
                    computer_science INTEGER NOT NULL CHECK (computer_science >= 0 AND computer_science <= 20),
                    physics INTEGER NOT NULL CHECK (physics >= 0 AND physics <= 20),
                    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                )''')

# Commit the changes
db_connection.commit()

#  Create table teachers to store the login credentials and personal information of Instructors

cursor.execute('''CREATE TABLE IF NOT EXISTS instructors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    userName VARCHAR(255) NOT NULL UNIQUE,
                    firstName TEXT NOT NULL,
                    lastName TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    dateOfBirth DATE NOT NULL,
                    userRole TEXT NOT NULL,
                    hashed_password TEXT NOT NULL
                )''')

# Commit the changes
db_connection.commit()
