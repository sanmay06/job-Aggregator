import os
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient(os.getenv("MONGO_URL"))
db = client["jobagg"]


# ---------------------------------------------------------
# INIT
# ---------------------------------------------------------

def db_init(app):
    # MongoDB needs no init
    pass


# ---------------------------------------------------------
# LOGIN FUNCTIONS
# ---------------------------------------------------------

def create_login(username, password, email):
    db.login.insert_one({
        "username": username,
        "password": password,
        "email": email
    })


def find_login(identifier):
    user = db.login.find_one({
        "$or": [
            {"username": identifier},
            {"email": identifier}
        ]
    })

    if not user:
        return None

    return {
        "username": user["username"],
        "password": user["password"],
        "email": user["email"]
    }


# ---------------------------------------------------------
# PROFILE FUNCTIONS
# ---------------------------------------------------------

def create_profile(data):
    db.profiles.insert_one(data)


def get_profiles(username):
    profiles = list(db.profiles.find({"user": username}))
    for p in profiles:
        p["_id"] = str(p["_id"])
    return profiles


def get_profile(username, name):
    p = db.profiles.find_one({"user": username, "name": name})
    if not p:
        return None

    p["_id"] = str(p["_id"])
    return p


def update_profile(username, old_name, data):
    result = db.profiles.update_one(
        {"user": username, "name": old_name},
        {"$set": data}
    )
    return result.modified_count > 0


# ---------------------------------------------------------
# JOB FUNCTIONS
# ---------------------------------------------------------

def insert_job(job):
    db.jobs.update_one(
        {"link": job["link"]},
        {"$setOnInsert": job},
        upsert=True
    )


def count_jobs(filters):
    return db.jobs.count_documents({
        "title": filters["title"],
        "location": filters["location"],
        "website": {"$in": filters["websites"]}
    })


def fetch_jobs(filters, page, limit=100):
    skip = (page - 1) * limit
    jobs = list(db.jobs.find({
        "title": filters["title"],
        "location": filters["location"],
        "website": {"$in": filters["websites"]}

    }).skip(skip).limit(limit))

    for j in jobs:
        j["_id"] = str(j["_id"])

    return jobs
