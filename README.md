# Student Management API with FastAPI_

Introduction

This task is a simple Student Management API built using FastAPI. The primary reason for choosing FastAPI was because i preferred to care about performance(since FastAPI is inherently design to make use of Async programming, on which i'll like to implement later on this task), ease of use, and similarities in logic to Express.js, the NodeJS framework with which I am already familiar. Additionally, FastAPI's built-in features, such as automatic documentation and data validation, significantly streamline the development process.

Environment Setup:

To set up the environment for this project, I started by installing FastAPI and Uvicorn, a lightning-fast ASGI server. After the installation, I created the app.py file, where I began exploring FastAPI by referencing YouTube videos and tutorials.

DevelopmentProcess

1. Initial Setup
In the initial phase, I defined a simple Python dictionary to store student information. This allowed me to focus on serving the various URL endpoints without needing to immediately dive into database management. At this point, I was not yet familiar with using SQLite, the database management system required for this task.

2. Integrating SQLite
As the task progressed, I started documenting myself on SQLite, discovering that it's conveniently built into Python. This was a great revelation, as it simplified the database setup process. With basic knowledge of establishing connections and executing query statements, I instantiated my student schema in the SQLite database and tested the outcomes.

Conclusion

This task served as a practical introduction to FastAPI and SQLite, allowing me to leverage my existing knowledge of Express.js while learning new tools. The combination of FastAPI's performance and built-in features with SQLite's simplicity made the development process both enjoyable and educational.

HOW TO RUN THE PROJECT:

After cloning the CodeBase from the Remote Repository make sure to have the requirements.txt file and the server.py file in the project's root directory and run the following commands in this order.

pip install -r requirements.txt

uvicorn server:app --reload
