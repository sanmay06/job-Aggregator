from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv
from jobs import internshala, adzuna, times_job, jobRapido
from sqlalchemy import select, or_, and_

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
# db.init_from_url(os.getenv('DATABASE_URL', 'postgresql://postgres:1234@localhost:5432/job-agg'))

class Login(db.Model):
    __tablename__ = 'login'
    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.String(20))
    email = db.Column(db.String(30))

    def __init__(self, username, password, email):
        self.username = username
        self.password = password
        self.email = email

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

    def __init__(self, name, username, internshalla=False, adzuna=False, timesjob=False, jobrapido=False, min =0, max = 0, location = '', search = ''):
        self.name = name
        self.username = username
        self.internshalla = internshalla
        self.adzuna = adzuna
        self.timesjob = timesjob
        self.jobrapido = jobrapido
        self.min = min
        self.max = max
        self.location = location
        self.search = search
    def Return(self):
        return {
            "id": self.id,
            "name": self.name,
            "username": self.username,
            "internshalla": self.internshalla,
            "adzuna": self.adzuna,
            "timesjob": self.timesjob,
            "jobrapido": self.jobrapido,
            "min": self.min,
            "max": self.max,
            "location": self.location,
            "search": self.search
        }

class Jobs(db.Model):
    __tablename__ = 'jobs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_title = db.Column(db.String(100))
    link = db.Column(db.String(500), unique=True)
    title = db.Column(db.String(20))
    website = db.Column(db.String(100))
    companyname = db.Column(db.String(100))
    salary = db.Column(db.Integer)
    minsalary = db.Column(db.Integer)
    maxsalary = db.Column(db.Integer)
    location = db.Column(db.String(100))
    createddate = db.Column(db.Date, default=db.func.current_date())

    def __init__(self, job_title, link, title, companyname, salary, minsalary, maxsalary, location, website):
        self.job_title = job_title
        self.link = link
        self.title = title
        self.companyname = companyname
        self.salary = salary
        self.minsalary = minsalary
        self.maxsalary = maxsalary
        self.location = location
        self.website = website

with app.app_context():
    db.create_all()


@app.route("/")
def home():
#     connection.rollback()
#     cursor = connection.cursor()
    
#     try:
#         cursor.execute(createJobs)
#         cursor.execute("alter table jobs alter column job_title type varchar(100)")
#         connection.commit()
#     except psycopg2.Error as e:
#         connection.rollback()
#         return str(e), 400
    return "working"

@app.post("/reg")
def register():
    data = request.get_json()
        
    username = data["username"]
    password = data["password"]
    email = data["email"]

    login = Login(username, password, email)
    db.session.add(login)
    db.session.commit()

    return {"msg": "created successfully"}, 201

@app.post("/login")
def login():
    data = request.get_json()
    username = data["username"]
    passw = data["password"]

    stmt = select(Login).where(or_(Login.username == username, Login.email == username))
    result = db.session.execute(stmt).scalars().first()
    print(result)

    if result and result.password == passw:
        return {"msg": "success", "user": result.username}, 200
    return {"msg": "Wrong password or username"}, 401
    
@app.get("/getprofiles")
def getProfiles():
    user = request.args.get('user')
    stmt = select(Profiles).where(Profiles.username == user)
    names = db.session.execute(stmt).scalars().all()
    if names is not None:
        return { "msg": "success", "names": [name.name for name in names]}, 200
    else:
        return {"msg": "No profiles found"}, 404

@app.get("/profile/<name>")
def getProfile(name):
    username = request.args.get('user')
    profile = Profiles.query.filter_by(name = name, username = username).first()
    print("Profile:", profile.Return())
    if profile is None:
        return {"msg": "Profile not found"}, 404
    else:
        return {"msg": "success", "profile": profile.Return()}, 200

@app.post("/profile/create")
def postProfile():
    data = request.get_json()

    username = data['user']
    new_name = data["name"]  
    search = data["search"]
    sites = data["sites"]
    min_salary = data['min']
    max_salary = data['max']
    print("Sites",sites)
    print("Adzuna" in sites)
    adzuna = "Adzuna" in sites
    inter = "Internshalla" in sites
    times = "TimesJobs" in sites
    jobr = "JobRapido" in sites
    location = data['location']

    profile = Profiles(new_name, username, inter, adzuna, times, jobr, min_salary, max_salary, location, search)
    db.session.add(profile)
    db.session.commit()
    return {"msg": "Profile created successfully"}, 201

@app.post("/profile/<profile>/update")
def updateProfile(profile):
    data = request.get_json()
    username = data.get('user')
    new_name = data.get("name")
    search = data.get("search")
    sites = data.get("sites", [])
    min_salary = data.get("min")
    max_salary = data.get("max")
    location = data.get("location")

    print("Sites",sites)
    print("Adzuna" in sites)
    adzuna = "Adzuna" in sites
    inter = "Internshalla" in sites
    times = "TimesJobs" in sites
    jobr = "JobRapido" in sites
    location = data['location']
    profile_r = Profiles.query.filter_by(name=profile, username=username).first()
    if profile_r is None:
        return {"msg": "Profile not found"}, 404
    # Update the profile
    profile_r.name = new_name
    profile_r.search = search
    profile_r.internshalla = inter
    profile_r.adzuna = adzuna
    profile_r.timesjob = times
    profile_r.jobrapido = jobr
    profile_r.min = min_salary
    profile_r.max = max_salary
    profile_r.location = location
    
    db.session.commit()
    return {"msg": "Profile updates successfully"}, 200

def InsertJob(jobs):
    for job in jobs:
        # print("Job:", job)
        try:
            j = Jobs(
                job_title=job['job_title'],
                link=job['link'],
                title=job['title'],
                companyname=job['companyname'],
                salary=job['salary'],
                minsalary=job['minsalary'],
                maxsalary=job['maxsalary'],
                location=job['location'],
                website=job['website']
            )

            db.session.add(j)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            if "duplicate key value violates unique constraint" in str(e):
                continue  # Skip duplicate link
            else:
                print(e) 
    # db.session.commit()

@app.get('/scrape_jobs/internshala/<profile>')
def scrape_internshala(profile):
    username = request.args.get('user')

    profile_data = Profiles.query.filter_by(name=profile, username=username).first()
    if profile_data is None:
        return {"msg": "Profile not found"}, 404
    if not profile_data.internshalla:
        return {}, 200
    location = profile_data.location
    search = profile_data.search
    jobs = internshala(search, location)
    # print("Jobs Internshala:", jobs)
    if jobs:
        InsertJob(jobs)
    db.session.commit()
    return {"msg": "Internshala scraping completed."}, 200

@app.get('/scrape_jobs/adzuna/<profile>')
def scrape_adzuna(profile):
    username = request.args.get('user')

    profile_data = Profiles.query.filter_by(name=profile, username=username).first()
    if profile_data is None:
        return {"msg": "Profile not found"}, 404
    if not profile_data.adzuna:
        return {}, 200
    location = profile_data.location
    search = profile_data.search
    jobs = adzuna(search, location)
    # print("Jobs Adzuna:", jobs)
    if jobs:
        InsertJob(jobs)
    db.session.commit()
    return {"msg": "Adzuna scraping completed."}, 200

@app.get('/scrape_jobs/timesjob/<profile>')
def scrape_timesjob(profile):
    username = request.args.get('user')
    profile_data = Profiles.query.filter_by(name=profile, username=username).first()
    if profile_data is None:
        return {"msg": "Profile not found"}, 404
    if not profile_data.timesjob:
        return {}, 200
    location = profile_data.location
    search = profile_data.search
    jobs = times_job(search, location)
    # print("Jobs TimesJob:", jobs)
    if jobs:
        InsertJob(jobs)
    db.session.commit()
    return {"msg": "TImes job scraping completed."}, 200

@app.get('/scrape_jobs/jobrapido/<profile>')
def scrape_jobrapido(profile):
    username = request.args.get('user')
    profile_data = Profiles.query.filter_by(name=profile, username=username).first()
    if profile_data is None:
        return {"msg": "Profile not found"}, 404
    if not profile_data.jobrapido:
        return {}, 200
    location = profile_data.location
    search = profile_data.search
    jobs = jobRapido(search, location)
    
    if jobs:
        InsertJob(jobs)
    db.session.commit()
    return {"msg": "Job Rapido scraping completed."}, 200
   

@app.get('/get_pages/<profile>')
def pages(profile):
    username = request.args.get('user')
    profile = Profiles.query.filter_by(name=profile, username=username).first()
    count = Jobs.query.filter(
        Jobs.title == profile.search,
        Jobs.location == profile.location,
        Jobs.website.in_(
            [
                source for source, enabled in {
                    "Internshala": profile.internshalla,
                    "Adzuna": profile.adzuna,
                    "TimesJobs": profile.timesjob,
                    "JobRapido": profile.jobrapido
                }.items() if enabled
            ]
        ),
        # or_(
        # and_(
        #         Jobs.salary != None,
        #         Jobs.salary >= profile.min,
        #         Jobs.salary <= profile.max
        #     ),
        #     and_(
        #         Jobs.minsalary >= profile.min,
        #         Jobs.maxsalary <= profile.max
        #     )
        # )
    ).count()
    pages = count // 100 + (1 if count % 100 > 0 else 0)
    return { "pages": pages }, 200

@app.get('/fetch_jobs/<profile>/<page>')
def fetch_jobs(profile, page):
    username = request.args.get('user')
    page = int(page)
    profile = Profiles.query.filter_by(name=profile, username=username).first()
    if profile is None:
        return {"msg": "Profile not found"}, 404
    if not (profile.internshalla or profile.adzuna or profile.timesjob or profile.jobrapido):
        return {"msg": "No websites selected for scraping"}, 200
    jobs = Jobs.query.filter(
        Jobs.title == profile.search,
        Jobs.location == profile.location,
        Jobs.website.in_(
            [
                source for source, enabled in {
                    "Internshala": profile.internshalla,
                    "Adzuna": profile.adzuna,
                    "TimesJobs": profile.timesjob,
                    "JobRapido": profile.jobrapido
                }.items() if enabled
            ]
        ),
        # or_(
        # and_(
        #     Jobs.salary != None,
        #     Jobs.salary >= profile.min,
        #     Jobs.salary <= profile.max
        # ),
        # and_(
        #     Jobs.minsalary >= profile.min,
        #     Jobs.maxsalary <= profile.max
        # )
        # )
    ).paginate(page = page, per_page = 100)
    if not jobs.items:
        # print("No jobs found for this profile")
        return {"msg": "No jobs found for this profile"}, 404
    return {
        "msg": "success",
        "jobs": [
            {
                "job_title": job.job_title,
                "link": job.link,
                "title": job.title,
                "companyname": job.companyname,
                "salary": job.salary,
                "minsalary": job.minsalary,
                "maxsalary": job.maxsalary,
                "location": job.location,
                "website": job.website
            } for job in jobs.items
        ]
    }, 200

if __name__ == "__main__":
    app.run(debug=True)
