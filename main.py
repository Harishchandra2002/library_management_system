from fastapi import FastAPI, HTTPException, Query, Path
from pydantic import BaseModel
from pymongo import MongoClient
from bson import ObjectId
from typing import Optional



# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["school"]
collection = db["students"]

# FastAPI app
app = FastAPI()

# Model for student data
class Student(BaseModel):
    name: str
    age: int
    address: dict

# Endpoint to create a student

@app.post("/students", status_code=201)
def create_student(student: Student):
    # Convert the Pydantic Student model to a dictionary
    student_dict = student.dict()

    # Insert the student data into the MongoDB collection
    inserted_student = collection.insert_one(student_dict)

    # Return the ID of the newly created student
    return {"id": str(inserted_student.inserted_id)}

# Endpoint to list students
@app.get("/students", response_model=dict)
def list_students(country: str = Query(None, description="Filter by country"),
                  age: int = Query(None, description="Minimum age to filter")):
    query = {}
    if country:
        query["address.country"] = country
    if age is not None:
        query["age"] = {"$gte": age}
    students = list(collection.find(query, {"_id": 0}))
    return {"data": students}

# Endpoint to fetch a student by ID
@app.get("/students/{id}", response_model=Student)
def get_student(id: str = Path(..., title="The ID of the student", regex="^[a-fA-F0-9]{24}$")):
    try:
        student = collection.find_one({"_id": ObjectId(id)})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return Student(**student)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

# Endpoint to update a student by ID
@app.patch("/students/{id}", status_code=204)
def update_student(id: str, student: Student):
    updated_student = collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": student.dict(exclude_unset=True)}
    )
    if updated_student.modified_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")

# Endpoint to delete a student by ID
@app.delete("/students/{id}", status_code=204)
def delete_student(id: str):
    deleted_student = collection.delete_one({"_id": ObjectId(id)})
    if deleted_student.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Student not found")



# Function to add sample student records to MongoDB
# def add_sample_students():
#     sample_students = [
#         {"name": "Alice1", "age": 27, "address": {"city": "vijayawada", "country": "USA"}},
#         {"name": "Bob2", "age": 32, "address": {"city": "Los Angeles", "country": "USA"}},
#         {"name": "Charlie3", "age": 24, "address": {"city": "London", "country": "UK"}},
#     ]
#     collection.insert_many(sample_students)
#
# # Call the function to add sample students
def get_student_ids():
    # Query the MongoDB collection to retrieve all student records
    cursor = collection.find({}, {"_id": 1})

    # Extract student IDs from the query result
    student_ids = [str(student["_id"]) for student in cursor]

    return student_ids

# Example usage to get student IDs
student_ids = get_student_ids()
print("Student IDs:", student_ids)


@app.get("/students", response_model=dict)
def list_students(country: Optional[str] = Query(None, description="Filter by country"),
                  min_age: Optional[int] = Query(None, description="Minimum age to filter")):
    query = {}
    if country:
        query["address.country"] = country
    if min_age is not None:
        query["age"] = {"$gte": min_age}

    # Query the MongoDB collection based on the filters
    students = list(collection.find(query, {"_id": 0}))

    # Return the filtered students
    return {"data": students}


# Example for deletion
def delete_student_example(student_id):
    result = collection.delete_one({"_id": student_id})
    if result.deleted_count == 1:
        print(f"Student with ID {student_id} deleted successfully.")
    else:
        print(f"Student with ID {student_id} not found.")

# Example for getting a student by ID
def get_student_example(student_id):
    student = collection.find_one({"_id": student_id})
    if student:
        print(f"Found student with ID {student_id}: {student}")
    else:
        print(f"Student with ID {student_id} not found.")

# Example for updating a student by ID
def update_student_example(student_id, update_data):
    result = collection.update_one({"_id": student_id}, {"$set": update_data})
    if result.modified_count == 1:
        print(f"Student with ID {student_id} updated successfully.")
    else:
        print(f"Student with ID {student_id} not found.")

# Example usage
student_id = ObjectId("66155fcfaa733a119b5b181d")  # Replace with an existing student ID

get_student_example(student_id)

update_data = {"age": 23}  # Example update data
update_student_example(student_id, update_data)
get_student_example(student_id)
# delete_student_example(student_id)
