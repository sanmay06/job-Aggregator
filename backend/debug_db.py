from app import app, db
from database.postgres import Jobs

with app.app_context():
    jobs = Jobs.query.all()
    print(f"Total jobs: {len(jobs)}")
    for j in jobs[:5]:
        print(f"Title: '{j.title}', Location: '{j.location}', Website: '{j.website}', Job Title: '{j.job_title}'")
