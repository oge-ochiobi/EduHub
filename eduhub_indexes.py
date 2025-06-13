# eduhub_indexes.py
"""
This script creates indexes and performs query performance analysis using PyMongo.

"""

from pymongo import MongoClient
from datetime import datetime
import time

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["eduhub_db"]

# ----------------------------
# Task 5.1: Index Creation
# ----------------------------

# 1. User email lookup index
db.users.create_index("email", unique=True)

# 2. Course search by title and category
db.courses.create_index([("title", 1), ("category", 1)])

# 3. Assignment queries by due date
db.assignments.create_index("dueDate")

# 4. Enrollment queries by student and course
db.enrollments.create_index([("studentId", 1), ("courseId", 1)], unique=True)

# ----------------------------
# Task 5.2: Query Optimization
# ----------------------------

def analyze_query_time(query_fn, *args):
    start = time.time()
    result = query_fn(*args)
    duration = time.time() - start
    print(f"Execution Time: {duration:.5f} seconds\n")
    return result

# 1. Analyze slow query: course search without index
def search_courses_raw():
    return db.courses.find({"title": {"$regex": "python", "$options": "i"}}).explain()

# 2. Analyze fast query: with index
def search_courses_indexed():
    return db.courses.find({"title": {"$regex": "python", "$options": "i"}}).explain()

# Run both for performance insight
print("\n--- Raw (non-optimized) Course Search ---")
explain_raw = analyze_query_time(search_courses_raw)
print(explain_raw)

print("\n--- Indexed Course Search ---")
explain_indexed = analyze_query_time(search_courses_indexed)
print(explain_indexed)

# 3. Optimized: Search enrollments by studentId and courseId
def find_enrollment():
    return db.enrollments.find_one({"studentId": "STU001", "courseId": "CRS001"})

analyze_query_time(find_enrollment)

# 4. Optimized: Upcoming assignments by due date
def upcoming_assignments():
    today = datetime.utcnow()
    next_week = today + timedelta(days=7)
    return list(db.assignments.find({"dueDate": {"$gte": today, "$lte": next_week}}))

analyze_query_time(upcoming_assignments)

print("\n✅ Indexing and optimization complete.")
