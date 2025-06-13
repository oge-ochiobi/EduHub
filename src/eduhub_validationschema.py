# eduhub_validation_and_errors.py
"""
Schema validation and error handling logic for EduHub backend (PyMongo).
Covers required fields, enum validation, type checks, and exception catching.
"""

from pymongo import MongoClient, errors
import re
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["eduhub_db"]

# --------------------------
# Task 6.1 Schema Validation
# --------------------------

# Schema validation for 'users' collection
db.command({
    "collMod": "users",
    "validator": {
        "$jsonSchema": {
            "bsonType": "object",
            "required": ["userId", "email", "firstName", "lastName", "role"],
            "properties": {
                "userId": {"bsonType": "string"},
                "email": {
                    "bsonType": "string",
                    "pattern": "^.+@.+\..+$",
                    "description": "Must be a valid email format"
                },
                "firstName": {"bsonType": "string"},
                "lastName": {"bsonType": "string"},
                "role": {
                    "enum": ["student", "instructor"],
                    "description": "Only 'student' or 'instructor' roles allowed"
                },
                "dateJoined": {"bsonType": "date"},
                "isActive": {"bsonType": "bool"}
            }
        }
    },
    "validationLevel": "strict"
})

# --------------------------
# Task 6.2 Error Handling
# --------------------------

def insert_user(user_data):
    try:
        result = db.users.insert_one(user_data)
        print("✅ Inserted user with ID:", result.inserted_id)
    except errors.DuplicateKeyError:
        print("❌ Duplicate email or userId.")
    except errors.WriteError as we:
        print("❌ WriteError:", we.details)
    except Exception as e:
        print("❌ Unexpected error:", str(e))

# Example 1: Duplicate Key Error
existing_email_user = {
    "userId": "STU002",
    "email": "janedoe@example.com",
    "firstName": "Jane",
    "lastName": "Doe",
    "role": "student",
    "dateJoined": datetime.utcnow(),
    "isActive": True
}
insert_user(existing_email_user)  # Run twice to simulate duplicate

# Example 2: Invalid Data Type (e.g. string instead of boolean)
invalid_user = {
    "userId": "STU005",
    "email": "newstudent@example.com",
    "firstName": "Invalid",
    "lastName": "User",
    "role": "student",
    "isActive": "yes"  # Should be boolean
}
insert_user(invalid_user)

# Example 3: Missing Required Fields
incomplete_user = {
    "userId": "STU006",
    "firstName": "NoEmail"
    # Missing email, lastName, and role
}
insert_user(incomplete_user)

print("\n✅ Schema validation and error handling module complete.")
