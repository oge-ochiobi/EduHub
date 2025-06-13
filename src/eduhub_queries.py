# eduhub_queries.py

"""
This script contains Read, Update, and Delete operations for EduHub collections
"""

from pymongo import MongoClient
from datetime import datetime, timedelta

# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["eduhub_db"]

users = db["users"]
courses = db["courses"]
enrollments = db["enrollments"]
lessons = db["lessons"]
assignments = db["assignments"]
submissions = db["submissions"]

# ------------------ READ OPERATIONS ------------------

def get_active_students():
    return list(users.find({"role": "student", "isActive": True}))

def get_course_with_instructor(course_id):
    course = courses.find_one({"courseId": course_id})
    instructor = users.find_one({"userId": course["instructorId"]})
    course["instructor"] = instructor
    return course

def get_courses_by_category(category):
    return list(courses.find({"category": category}))

def get_students_in_course(course_id):
    student_ids = enrollments.find({"courseId": course_id})
    return list(users.find({"userId": {"$in": [e["studentId"] for e in student_ids]}}))

def search_courses_by_title(title):
    return list(courses.find({"title": {"$regex": title, "$options": "i"}}))

# ------------------ UPDATE OPERATIONS ------------------

def update_user_profile(user_id, new_profile):
    return users.update_one({"userId": user_id}, {"$set": {"profile": new_profile}})

def publish_course(course_id):
    return courses.update_one({"courseId": course_id}, {"$set": {"isPublished": True}})

def update_assignment_grade(assignment_id, student_id, new_grade):
    return submissions.update_one(
        {"assignmentId": assignment_id, "studentId": student_id},
        {"$set": {"grade": new_grade}}
    )

def add_tags_to_course(course_id, tags):
    return courses.update_one(
        {"courseId": course_id},
        {"$addToSet": {"tags": {"$each": tags}}}
    )

# ------------------ DELETE OPERATIONS ------------------

def soft_delete_user(user_id):
    return users.update_one({"userId": user_id}, {"$set": {"isActive": False}})

def delete_enrollment(student_id, course_id):
    return enrollments.delete_one({"studentId": student_id, "courseId": course_id})

def remove_lesson(lesson_id):
    return lessons.delete_one({"lessonId": lesson_id})

# ------------------ COMPLEX QUERIES ------------------

def find_courses_in_price_range(min_price=50, max_price=200):
    return list(courses.find({"price": {"$gte": min_price, "$lte": max_price}}))

def get_recent_users(months=6):
    cutoff = datetime.now() - timedelta(days=months * 30)
    return list(users.find({"dateJoined": {"$gte": cutoff}}))

def find_courses_by_tags(tag_list):
    return list(courses.find({"tags": {"$in": tag_list}}))

def upcoming_due_assignments():
    next_week = datetime.now() + timedelta(days=7)
    return list(assignments.find({"dueDate": {"$lte": next_week}}))

# Test examples
if __name__ == "__main__":
    print("Active students:", get_active_students())
    print("Courses in category 'Data Science':", get_courses_by_category("Data Science"))
    print("Courses with 'Python' in title:", search_courses_by_title("Python"))
