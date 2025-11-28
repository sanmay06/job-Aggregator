from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
import os

db = SQLAlchemy()


# ---------------------------------------------------------
# INIT
# ---------------------------------------------------------

def db_init(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()


# ---------------------------------------------------------
# MODELS
# ---------------------------------------------------------

class Login(db.Model):
    __tablename__ = 'login'
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(20))
    email = db.Column(db.String(30))


class Profiles(db.Model):
    __tablename__ = 'profiles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20), db.ForeignKey('login.username'))
    internshalla = db.Column(db.Boolean, default=False)
    adzuna = db.Column(db.Boolean, default=False)
    timesjob = db.Column(db.Boolean, default=False)
    jobrapido = db.Column(db.Boolean, default=False)
    min = db.Column(db.Integer)
    max = db.Column(db.Integer)
    location = db.Column(db.String(50))
    search = db.Column(db.String(20))


class Jobs(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(100))
    link = db.Column(db.String(255), unique=True)
    title = db.Column(db.String(100))
    companyname = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    minsalary = db.Column(db.Integer)
    maxsalary = db.Column(db.Integer)
    location = db.Column(db.String(50))
    website = db.Column(db.String(30))


# ---------------------------------------------------------
# LOGIN FUNCTIONS
# ---------------------------------------------------------

def create_login(username, password, email):
    entry = Login(username=username, password=password, email=email)
    db.session.add(entry)
    db.session.commit()


def find_login(identifier):
    user = Login.query.filter(
        (Login.username == identifier) | (Login.email == identifier)
    ).first()

    if not user:
        return None

    return {
        "username": user.username,
        "password": user.password,
        "email": user.email
    }


# ---------------------------------------------------------
# PROFILE FUNCTIONS
# ---------------------------------------------------------

def create_profile(data):
    p = Profiles(
        name=data["name"],
        username=data["user"],
        search=data["search"],
        location=data["location"],
        min=data["min"],
        max=data["max"],
        internshalla=data["internshalla"],
        adzuna=data["adzuna"],
        timesjob=data["timesjob"],
        jobrapido=data["jobrapido"]
    )
    db.session.add(p)
    db.session.commit()


def get_profiles(username):
    profiles = Profiles.query.filter_by(username=username).all()
    return [
        {
            "name": p.name,
            "search": p.search,
            "location": p.location,
            "internshalla": p.internshalla,
            "adzuna": p.adzuna,
            "timesjob": p.timesjob,
            "jobrapido": p.jobrapido,
            "min": p.min,
            "max": p.max
        }
        for p in profiles
    ]


def get_profile(username, name):
    p = Profiles.query.filter_by(username=username, name=name).first()
    if not p:
        return None

    return {
        "name": p.name,
        "username": p.username,
        "search": p.search,
        "location": p.location,
        "min": p.min,
        "max": p.max,
        "internshalla": p.internshalla,
        "adzuna": p.adzuna,
        "timesjob": p.timesjob,
        "jobrapido": p.jobrapido
    }


def update_profile(username, old_name, data):
    p = Profiles.query.filter_by(username=username, name=old_name).first()
    if not p:
        return False

    p.name = data["name"]
    p.search = data["search"]
    p.location = data["location"]
    p.min = data["min"]
    p.max = data["max"]
    p.internshalla = data["internshalla"]
    p.adzuna = data["adzuna"]
    p.timesjob = data["timesjob"]
    p.jobrapido = data["jobrapido"]

    db.session.commit()
    return True


# ---------------------------------------------------------
# JOB FUNCTIONS
# ---------------------------------------------------------

def insert_job(job):
    existing = Jobs.query.filter_by(link=job["link"]).first()
    if existing:
        return

    j = Jobs(
        job_title=job["job_title"],
        link=job["link"],
        title=job["title"],
        companyname=job["companyname"],
        salary=job["salary"],
        minsalary=job["minsalary"],
        maxsalary=job["maxsalary"],
        location=job["location"],
        website=job["website"]
    )
    db.session.add(j)
    db.session.commit()


def count_jobs(filters):
    return Jobs.query.filter(
        Jobs.title == filters["title"],
        Jobs.location == filters["location"],
        Jobs.website.in_(filters["websites"])
    ).count()


def fetch_jobs(filters, page, limit=100):
    result = Jobs.query.filter(
        Jobs.title == filters["title"],
        Jobs.location == filters["location"],
        Jobs.website.in_(filters["websites"])
    ).paginate(page=page, per_page=limit)

    return [
        {
            "job_title": j.job_title,
            "link": j.link,
            "title": j.title,
            "companyname": j.companyname,
            "salary": j.salary,
            "minsalary": j.minsalary,
            "maxsalary": j.maxsalary,
            "location": j.location,
            "website": j.website
        }
        for j in result.items
    ]
