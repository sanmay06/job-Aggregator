from flask import Flask, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from jobs import internshala, adzuna, jobRapido, timesjob

import db  # AUTO-SWITCHING DB BACKEND

from db import (
    db_init, create_login, find_login,
    create_profile, get_profiles, get_profile, update_profile,
    insert_job, count_jobs, fetch_jobs
)

load_dotenv()
# Password verification utility
from werkzeug.security import check_password_hash

# JWT and security utilities
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os

# Flask-Limiter for rate limiting
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# JWT and rate limiter will be configured after Flask app creation

def generate_token(username):
    payload = {
        "sub": username,
        "exp": datetime.utcnow() + timedelta(hours=2)
    }
    return jwt.encode(payload, app.config["SECRET_KEY"], algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])

def jwt_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return {"msg": "Missing token"}, 401
        token = auth.split()[1]
        try:
            payload = decode_token(token)
            request.user = payload["sub"]
        except jwt.ExpiredSignatureError:
            return {"msg": "Token expired"}, 401
        except jwt.InvalidTokenError:
            return {"msg": "Invalid token"}, 401
        return fn(*args, **kwargs)
    return wrapper
app = Flask(__name__)

# Configure secret key for JWT (fallback for development)
app.config["SECRET_KEY"] = os.getenv("JWT_SECRET", "dev-secret-key")

# Initialise rate limiter (5 requests per minute for auth endpoints)
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)
CORS(app)

db_init(app)


@app.get("/")
def home():
    return "working"


# ------------------------------------------
# REGISTER
# ------------------------------------------
@app.post("/reg")
@limiter.limit("5 per minute")
def register():
    data = request.get_json()
    # Basic validation
    required = ["username", "password", "email"]
    if not data or not all(k in data and data[k] for k in required):
        return {"msg": "username, password, and email required"}, 400
    create_login(data["username"], data["password"], data["email"])
    return {"msg": "created successfully"}, 201


# ------------------------------------------
# LOGIN
# ------------------------------------------
@app.post("/login")
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    # Basic input validation
    if not data or not data.get("username") or not data.get("password"):
        return {"msg": "username and password required"}, 400
    user = find_login(data["username"])

    if user and check_password_hash(user["password"], data["password"]):
        token = generate_token(user["username"])
        return {"msg": "success", "token": token, "user": user["username"]}, 200

    return {"msg": "Wrong password or username"}, 401


# ------------------------------------------
# GET PROFILES
# ------------------------------------------
@app.get("/getprofiles")
@jwt_required
def getProfiles():
    user = request.args.get("user")
    profiles = get_profiles(user)
    names = [p["name"] for p in profiles]
    return {"msg": "success", "names": names}, 200


# ------------------------------------------
# GET PROFILE
# ------------------------------------------
@app.get("/profile/<name>")
@jwt_required
def getProfile(name):
    user = request.args.get("user")
    profile = get_profile(user, name)

    if not profile:
        return {"msg": "Profile not found"}, 404

    return {"msg": "success", "profile": profile}, 200


# ------------------------------------------
# CREATE PROFILE
# ------------------------------------------
@app.post("/profile/create")
@jwt_required
def postProfile():
    data = request.get_json()
    sites = data["sites"]

    # Use the username from the JWT token (set by jwt_required)
    username = request.user

    profile_data = {
        "name": data["name"],
        "user": username,
        "search": data["search"],
        "location": data["location"],
        "min": data["min"],
        "max": data["max"],
        "internshalla": "Internshalla" in sites,
        "adzuna": "Adzuna" in sites,
        "timesjob": "TimesJobs" in sites,
        "jobrapido": "JobRapido" in sites
    }

    create_profile(profile_data)
    return {"msg": "Profile created successfully"}, 201


# ------------------------------------------
# UPDATE PROFILE
# ------------------------------------------
@app.post("/profile/<profile>/update")
@jwt_required
def updateProfile(profile):
    data = request.get_json()
    data["user"] = request.user
    # print("[DEBUG] updateProfile received data:", data)
    sites = data["sites"]

    new_data = {
        "name": data["name"],
        "search": data["search"],
        "location": data["location"],
        "min": data["min"],
        "max": data["max"],
        "internshalla": "Internshalla" in sites,
        "adzuna": "Adzuna" in sites,
        "timesjob": "TimesJobs" in sites,
        "jobrapido": "JobRapido" in sites
    }

    updated = update_profile(data["user"], profile, new_data)
    # print("[DEBUG] update_profile returned:", updated)
    if not updated:
        return {"msg": "Profile not found"}, 404

    return {"msg": "Profile updated successfully"}, 200


# ------------------------------------------
# SCRAPING
# ------------------------------------------
@app.get('/scrape_jobs/<site>/<profile>')
@jwt_required
def scrape(site, profile):
    username = request.args.get("user")
    p = get_profile(username, profile)

    if not p:
        return {"msg": "Profile not found"}, 404

    print(site)

    if not p.get(site):
        return {"msg": "Site disabled"}, 200

    print(f"Scraping {site} for {profile}...")
    if site == "internshalla":
        jobs = internshala(p["search"], p["location"])
    elif site == "adzuna":
        jobs = adzuna(p["search"], p["location"])
    elif site == "timesjob":
        jobs = timesjob(p["search"], p["location"])
    else:
        jobs = jobRapido(p["search"], p["location"])

    print(f"Found {len(jobs)} jobs from {site}")
    for job in jobs:
        insert_job(job)

    return {"msg": f"{site} scraping completed"}, 200


# ------------------------------------------
# PAGINATION
# ------------------------------------------
@app.get("/get_pages/<profile>")
@jwt_required
def pages(profile):
    username = request.args.get("user")
    p = get_profile(username, profile)

    filters = {
        "title": p["search"],
        "location": p["location"],
        "websites": [
            w for w, enabled in {
                "Internshala": p["internshalla"],
                "Adzuna": p["adzuna"],
                "TimesJobs": p["timesjob"],
                "JobRapido": p["jobrapido"],
            }.items() if enabled
        ]
    }

    total = count_jobs(filters)
    pages = (total + 99) // 100
    # print(pages)
    return {"pages": pages}, 200


@app.get("/fetch_jobs/<profile>/<page>")
@jwt_required
def fetchJobs(profile, page):
    username = request.args.get("user")
    page = int(page)

    p = get_profile(username, profile)

    filters = {
        "title": p["search"],
        "location": p["location"],
        "websites": [
            w for w, enabled in {
                "Internshala": p["internshalla"],
                "Adzuna": p["adzuna"],
                "TimesJobs": p["timesjob"],
                "JobRapido": p["jobrapido"]
            }.items() if enabled
        ]
    }

    jobs = fetch_jobs(filters, page)

    if not jobs:
        return {"msg": "No jobs found"}, 404

    return {"msg": "success", "jobs": jobs}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
