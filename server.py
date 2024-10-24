from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from bson import ObjectId
from typing import List

# MongoDB database setup
MONGODB_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(MONGODB_URL)
db = client.students_database  # Change this to your desired database name

# FastAPI app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Your React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for input validation
class StudentCreate(BaseModel):
    first_name: str
    last_name: str
    phone_number: str
    address: str
    registration_number: str
    student_class: str

class Student(StudentCreate):
    id: str

# API routes

# Create a new student
@app.post("/students/", response_model=Student)
async def create_student(student: StudentCreate):
    student_dict = student.dict()
    result = await db.students.insert_one(student_dict)
    new_student = await db.students.find_one({"_id": result.inserted_id})
    
    # Add the 'id' field with the string representation of the ObjectId
    new_student['id'] = str(new_student['_id'])
    del new_student['_id']  # Optionally remove the MongoDB _id field
    
    return Student(**new_student)

# Get all students
@app.get("/students/", response_model=List[Student])
async def get_students():
    students = []
    async for student in db.students.find():
        student['id'] = str(student['_id'])
        del student['_id']  # Optionally remove the MongoDB _id field
        students.append(Student(**student))
    return students

# Update a student
@app.put("/students/{student_id}", response_model=Student)
async def update_student(student_id: str, student: StudentCreate):
    result = await db.students.update_one({"_id": ObjectId(student_id)}, {"$set": student.dict()})
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    updated_student = await db.students.find_one({"_id": ObjectId(student_id)})
    
    updated_student['id'] = str(updated_student['_id'])
    del updated_student['_id']  # Optionally remove the MongoDB _id field
    
    return Student(**updated_student)

# Delete a student
@app.delete("/students/{student_id}")
async def delete_student(student_id: str):
    result = await db.students.delete_one({"_id": ObjectId(student_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"detail": "Student deleted successfully"}
