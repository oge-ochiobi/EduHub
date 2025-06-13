# eduhub_seed_and_crud.py
"""
This file contains:
- Connection setup
- Schema validation setup for each collection
- Data insertion using Faker
- CRUD operations for each collection
"""

from pymongo import MongoClient, ASCENDING, DESCENDING, errors
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from faker import Faker
import random
import string

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["eduhub_db"]

fake = Faker()

# Helper function to generate unique IDs
def generate_id(prefix):
    return prefix + "_" + ''.join(random.choices(string.ascii_letters + string.digits, k=8))

"""
------------------------------
Collection Schemas + Creation
------------------------------
"""

# Users Collection
user_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["userId", "email", "firstName", "lastName", "role", "dateJoined", "isActive"],
        "properties": {
            "userId": {"bsonType": "string"},
            "email": {"bsonType": "string", "pattern": "^.+@.+\\..+$"},
            "firstName": {"bsonType": "string"},
            "lastName": {"bsonType": "string"},
            "role": {"enum": ["student", "instructor"]},
            "dateJoined": {"bsonType": "date"},
            "profile": {
                "bsonType": "object",
                "properties": {
                    "bio": {"bsonType": "string"},
                    "avatar": {"bsonType": "string"},
                    "skills": {
                        "bsonType": "array",
                        "items": {"bsonType": "string"}
                    }
                }
            },
            "isActive": {"bsonType": "bool"}
        }
    }
}

db.create_collection("users", validator=user_validator)

# Courses Collection
course_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["courseId", "title", "instructorId", "level", "duration", "price", "createdAt", "isPublished"],
        "properties": {
            "courseId": {"bsonType": "string"},
            "title": {"bsonType": "string"},
            "description": {"bsonType": "string"},
            "instructorId": {"bsonType": "string"},
            "category": {"bsonType": "string"},
            "level": {"enum": ["beginner", "intermediate", "advanced"]},
            "duration": {"bsonType": "int"},
            "price": {"bsonType": "double"},
            "tags": {
                "bsonType": "array",
                "items": {"bsonType": "string"}
            },
            "createdAt": {"bsonType": "date"},
            "updatedAt": {"bsonType": "date"},
            "isPublished": {"bsonType": "bool"}
        }
    }
}

db.create_collection("courses", validator=course_validator)

# Add similar schema validation for enrollments, lessons, assignments, submissions...

"""
------------------------------
Sample Data Seeding
------------------------------
"""

users = []
for _ in range(10):
    role = random.choice(["student", "instructor"])
    users.append({
        "userId": generate_id("USR"),
        "email": fake.email(),
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "role": role,
        "dateJoined": fake.date_time_between(start_date='-1y', end_date='now'),
        "profile": {
            "bio": fake.sentence(),
            "avatar": fake.image_url(),
            "skills": fake.words(nb=3)
        },
        "isActive": True
    })

inserted_users = db.users.insert_many(users)
print("Inserted Users:", len(inserted_users.inserted_ids))

"""
------------------------------
CRUD Operations
------------------------------
"""

# Create a new course
def create_course():
    instructor = db.users.find_one({"role": "instructor"})
    course = {
        "courseId": generate_id("CRS"),
        "title": fake.catch_phrase(),
        "description": fake.text(),
        "instructorId": instructor["userId"],
        "category": random.choice(["tech", "business", "design"]),
        "level": random.choice(["beginner", "intermediate", "advanced"]),
        "duration": random.randint(5, 20),
        "price": round(random.uniform(50, 300), 2),
        "tags": fake.words(nb=4),
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow(),
        "isPublished": False
    }
    db.courses.insert_one(course)
    print("Created course:", course["title"])

create_course()

# Read: find all active students
active_students = db.users.find({"role": "student", "isActive": True})
print("Active students:")
for student in active_students:
    print(student["firstName"], student["lastName"])

# Update: Mark a course as published
course_to_publish = db.courses.find_one({"isPublished": False})
db.courses.update_one({"_id": course_to_publish["_id"]}, {"$set": {"isPublished": True}})

# Delete (soft): Deactivate a user
user_to_deactivate = db.users.find_one({"isActive": True})
db.users.update_one({"_id": user_to_deactivate["_id"]}, {"$set": {"isActive": False}})
print("User deactivated:", user_to_deactivate["email"])


