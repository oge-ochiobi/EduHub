# eduhub_analytics.py

from pymongo import MongoClient
from datetime import datetime, timedelta

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["eduhub_db"]

# -----------------------------
# Course Enrollment Statistics
# -----------------------------

def total_enrollments_per_course():
    return list(db.enrollments.aggregate([
        {"$group": {"_id": "$courseId", "total_enrollments": {"$sum": 1}}},
        {"$sort": {"total_enrollments": -1}}
    ]))

def average_course_rating():
    return list(db.courses.aggregate([
        {"$group": {"_id": "$courseId", "avg_rating": {"$avg": "$rating"}}}
    ]))

def group_by_course_category():
    return list(db.courses.aggregate([
        {"$group": {"_id": "$category", "total": {"$sum": 1}}},
        {"$sort": {"total": -1}}
    ]))

# -----------------------------
# Student Performance Analysis
# -----------------------------

def average_grade_per_student():
    return list(db.submissions.aggregate([
        {"$group": {"_id": "$studentId", "avg_grade": {"$avg": "$grade"}}},
        {"$sort": {"avg_grade": -1}}
    ]))

def completion_rate_by_course():
    return list(db.enrollments.aggregate([
        {"$group": {"_id": "$courseId", 
                     "total_students": {"$sum": 1},
                     "completed": {"$sum": {"$cond": ["$completed", 1, 0]}}}},
        {"$project": {"completion_rate": {"$divide": ["$completed", "$total_students"]}}},
        {"$sort": {"completion_rate": -1}}
    ]))

def top_performing_students(limit=5):
    return list(db.submissions.aggregate([
        {"$group": {"_id": "$studentId", "avg_score": {"$avg": "$grade"}}},
        {"$sort": {"avg_score": -1}},
        {"$limit": limit}
    ]))

# -----------------------------
# Instructor Analytics
# -----------------------------

def total_students_per_instructor():
    return list(db.courses.aggregate([
        {"$lookup": {
            "from": "enrollments",
            "localField": "courseId",
            "foreignField": "courseId",
            "as": "enrollments"
        }},
        {"$group": {
            "_id": "$instructorId",
            "total_students": {"$sum": {"$size": "$enrollments"}}
        }}
    ]))

def average_course_rating_per_instructor():
    return list(db.courses.aggregate([
        {"$group": {"_id": "$instructorId", "avg_rating": {"$avg": "$rating"}}}
    ]))

def revenue_generated_per_instructor():
    return list(db.courses.aggregate([
        {"$lookup": {
            "from": "enrollments",
            "localField": "courseId",
            "foreignField": "courseId",
            "as": "enrollments"
        }},
        {"$project": {
            "instructorId": 1,
            "revenue": {"$multiply": ["$price", {"$size": "$enrollments"}]}
        }},
        {"$group": {"_id": "$instructorId", "total_revenue": {"$sum": "$revenue"}}}
    ]))

# -----------------------------
# Advanced Analytics
# -----------------------------

def monthly_enrollment_trends():
    return list(db.enrollments.aggregate([
        {"$project": {
            "month": {"$dateToString": {"format": "%Y-%m", "date": "$enrollmentDate"}}
        }},
        {"$group": {"_id": "$month", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]))

def popular_course_categories():
    return list(db.courses.aggregate([
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]))

def student_engagement_metrics():
    return list(db.submissions.aggregate([
        {"$group": {"_id": "$studentId", "submissions": {"$sum": 1}, "avg_grade": {"$avg": "$grade"}}},
        {"$sort": {"submissions": -1}}
    ]))
