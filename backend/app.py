from flask import Flask, request
from flask_cors import CORS
import os
from dotenv import load_dotenv
from jobs import internshala, adzuna, jobRapido

import db  # AUTO-SWITCHING DB BACKEND

from db import (
    db_init, create_login, find_login,
    create_profile, get_profiles, get_profile, update_profile,
    insert_job, count_jobs, fetch_jobs
)

load_dotenv()
app = Flask(__name__)
CORS(app)

db_init(app)


@app.get("/")
def home():
    return "working"


# ------------------------------------------
# REGISTER
# ------------------------------------------
@app.post("/reg")
def register():
    data = request.get_json()
    create_login(data["username"], data["password"], data["email"])
    return {"msg": "created successfully"}, 201


# ------------------------------------------
# LOGIN
# ------------------------------------------
@app.post("/login")
def login():
    data = request.get_json()
    user = find_login(data["username"])

    if user and user["password"] == data["password"]:
        return {"msg": "success", "user": user["username"]}, 200

    return {"msg": "Wrong password or username"}, 401


# ------------------------------------------
# GET PROFILES
# ------------------------------------------
@app.get("/getprofiles")
def getProfiles():
    user = request.args.get("user")
    profiles = get_profiles(user)
    names = [p["name"] for p in profiles]
    return {"msg": "success", "names": names}, 200


# ------------------------------------------
# GET PROFILE
# ------------------------------------------
@app.get("/profile/<name>")
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
def postProfile():
    data = request.get_json()
    sites = data["sites"]

    profile_data = {
        "name": data["name"],
        "user": data["user"],
        "search": data["search"],
        "location": data["location"],
        "min": data["min"],
        "max": data["max"],
        "internshalla": "Internshalla" in sites,
        "adzuna": "Adzuna" in sites,
        "jobrapido": "JobRapido" in sites
    }

    create_profile(profile_data)
    return {"msg": "Profile created successfully"}, 201


# ------------------------------------------
# UPDATE PROFILE
# ------------------------------------------
@app.post("/profile/<profile>/update")
def updateProfile(profile):
    data = request.get_json()
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
                "JobRapido": p["jobrapido"],
            }.items() if enabled
        ]
    }

    total = count_jobs(filters)
    pages = (total + 99) // 100
    # print(pages)
    return {"pages": pages}, 200


@app.get("/fetch_jobs/<profile>/<page>")
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
    app.run(debug=True)
