from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
import os

db = SQLAlchemy()
# Password hashing utilities
from werkzeug.security import generate_password_hash, check_password_hash


# ---------------------------------------------------------
# INIT
# ---------------------------------------------------------

def db_init(app):
    # Use SQLite file database by default (persists data), or DATABASE_URL if set
    import os
    # Fixed path - use backend/instance/test.db for consistency
    base_dir = r"C:\Users\sanma\Documents\projects\job Aggregator\backend\instance"
    os.makedirs(base_dir, exist_ok=True)
    db_path = os.path.join(base_dir, 'test.db')
    db_url = os.getenv("DATABASE_URL") or f"sqlite:///{db_path}"

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        # Create tables if they don't exist (don't drop existing data)
        db.create_all()

        # Migrate existing table columns to larger sizes (for PostgreSQL)
        from sqlalchemy import text
        try:
            db.session.execute(text("ALTER TABLE jobs ALTER COLUMN job_title TYPE VARCHAR(255)"))
            db.session.execute(text("ALTER TABLE jobs ALTER COLUMN link TYPE VARCHAR(512)"))
            db.session.execute(text("ALTER TABLE jobs ALTER COLUMN title TYPE VARCHAR(200)"))
            db.session.execute(text("ALTER TABLE jobs ALTER COLUMN companyname TYPE VARCHAR(200)"))
            db.session.execute(text("ALTER TABLE jobs ALTER COLUMN location TYPE VARCHAR(100)"))
            db.session.execute(text("ALTER TABLE jobs ALTER COLUMN website TYPE VARCHAR(50)"))
            db.session.commit()
            print("Database migration completed successfully")
        except Exception as e:
            db.session.rollback()
            # Silently ignore - column might already be migrated or SQLite doesn't support ALTER


# ---------------------------------------------------------
# MODELS
# ---------------------------------------------------------

class Login(db.Model):
    __tablename__ = 'login'
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(255))
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
    job_title = db.Column(db.String(255))
    link = db.Column(db.String(512), unique=True)
    title = db.Column(db.String(200))
    companyname = db.Column(db.String(200))
    salary = db.Column(db.Integer)
    minsalary = db.Column(db.Integer)
    maxsalary = db.Column(db.Integer)
    location = db.Column(db.String(100))
    website = db.Column(db.String(50))


# ---------------------------------------------------------
# LOGIN FUNCTIONS
# ---------------------------------------------------------

def create_login(username, password, email):
    # Store a securely hashed password
    hashed_pw = generate_password_hash(password)
    entry = Login(username=username, password=hashed_pw, email=email)
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
        internshalla=data.get("internshalla", False),
        adzuna=data.get("adzuna", False),
        timesjob=data.get("timesjob", False),
        jobrapido=data.get("jobrapido", False)
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

    # Truncate values to fit column limits
    j = Jobs(
        job_title=job["job_title"][:255] if job["job_title"] else None,
        link=job["link"][:512] if job["link"] else None,
        title=job["title"][:200] if job["title"] else None,
        companyname=job["companyname"][:200] if job["companyname"] else None,
        salary=job["salary"],
        minsalary=job["minsalary"],
        maxsalary=job["maxsalary"],
        location=(job["location"][:100] if job["location"] else "")[:100],
        website=(job["website"][:50] if job["website"] else "")[:50]
    )
    db.session.add(j)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error inserting job: {e}")


def count_jobs(filters):
    locations = [loc.strip().lower() for loc in filters["location"].split(",")]
    loc_conditions = [func.lower(Jobs.location) == loc for loc in locations]

    return Jobs.query.filter(
        Jobs.title == filters["title"],
        or_(*loc_conditions),
        Jobs.website.in_(filters["websites"])
    ).count()


def fetch_jobs(filters, page, limit=100):
    locations = [loc.strip().lower() for loc in filters["location"].split(",")]
    loc_conditions = [func.lower(Jobs.location) == loc for loc in locations]

    result = Jobs.query.filter(
        Jobs.title == filters["title"],
        or_(*loc_conditions),
        Jobs.website.in_(filters["websites"])
    ).order_by(Jobs.id.desc()).paginate(page=page, per_page=limit)

    return [
        {
            "id": j.id,
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
