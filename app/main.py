from pathlib import Path
from datetime import datetime, timezone
from fastapi import FastAPI, Request, UploadFile, File, Form, Header, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, func
from .config import settings
from .db import init_db, SessionLocal
from .models import CandidateProfile, Job, JobScore, Source, UserPreference, Application
from .services.resume import extract_text, build_profile
from .services.pipeline import run_scan

app=FastAPI(title=settings.app_name, version="2.0.0")
static_dir=Path(__file__).parent/"static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
templates=Jinja2Templates(directory=str(Path(__file__).parent/"templates"))
UPLOADS=Path("uploads"); UPLOADS.mkdir(exist_ok=True)

def seed_demo_data(db):
    if db.scalar(select(CandidateProfile)): return
    profile = CandidateProfile(
        name="Alex Mercer",
        resume_filename="alex_mercer_ai_resume.pdf",
        resume_text="AI Systems Engineer with expertise in Python, PyTorch, Transformers, Large Language Models, FastAPI, Docker, Computer Vision, and Cloud Architecture.",
        profile_json={
            "name": "Alex Mercer",
            "skills": ["Python", "PyTorch", "Transformers", "NLP", "FastAPI", "Docker", "SQL", "Computer Vision", "Machine Learning"],
            "experience_years": 2,
            "education": ["B.Tech Computer Science"]
        }
    )
    db.add(profile); db.flush()

    sources = [
        Source(name="OpenAI Engineering (Greenhouse)", kind="greenhouse", url="https://boards.greenhouse.io/openai", enabled=True),
        Source(name="Anthropic Research (Lever)", kind="lever", url="https://jobs.lever.co/anthropic", enabled=True),
        Source(name="Hugging Face Labs (Ashby)", kind="ashby", url="https://jobs.ashbyhq.com/huggingface", enabled=True),
        Source(name="HackerNews AI Feeds", kind="rss", url="https://news.ycombinator.com/jobs", enabled=True)
    ]
    for s in sources: db.add(s)
    db.flush()

    job_data = [
        {
            "fp": "fp_001_quantum_ai",
            "title": "Senior AI / ML Research Engineer",
            "company": "QuantumMind AI",
            "location": "San Francisco, CA (Remote)",
            "employment_type": "Full-Time",
            "description": "Develop next-generation transformer models, multimodal agents, and neural architectures with PyTorch and Python.",
            "url": "https://boards.greenhouse.io/openai/jobs/1",
            "source_name": "Greenhouse",
            "score": 94.2,
            "category": "HIGH",
            "skill": 95, "exp": 90, "edu": 100, "resp": 95, "tech": 95, "pref": 90,
            "matched": ["Python", "PyTorch", "Transformers", "NLP", "Machine Learning"],
            "missing": ["CUDA", "Distributed Training"],
            "explanation": "Outstanding match across LLM engineering, neural architectures, and modern agent systems."
        },
        {
            "fp": "fp_002_apex_robotics",
            "title": "Autonomous Perception Software Engineer",
            "company": "Apex Robotics",
            "location": "Seattle, WA (Hybrid)",
            "employment_type": "Full-Time",
            "description": "Build real-time computer vision inference pipelines and edge deployments with Docker and Python.",
            "url": "https://jobs.lever.co/anthropic/jobs/2",
            "source_name": "Lever",
            "score": 86.8,
            "category": "HIGH",
            "skill": 88, "exp": 85, "edu": 90, "resp": 85, "tech": 90, "pref": 85,
            "matched": ["Python", "Computer Vision", "FastAPI", "Docker"],
            "missing": ["ROS2", "C++"],
            "explanation": "High computer vision and containerized inference pipeline compatibility."
        },
        {
            "fp": "fp_003_neural_cloud",
            "title": "Full Stack AI Platform Engineer",
            "company": "NeuralCloud Labs",
            "location": "Bangalore / Remote",
            "employment_type": "Full-Time",
            "description": "Design high-throughput inference APIs, model serving microservices, and database pipelines using FastAPI and SQL.",
            "url": "https://jobs.ashbyhq.com/huggingface/jobs/3",
            "source_name": "Ashby",
            "score": 79.5,
            "category": "HIGH",
            "skill": 80, "exp": 80, "edu": 85, "resp": 75, "tech": 80, "pref": 80,
            "matched": ["Python", "FastAPI", "SQL", "Docker"],
            "missing": ["React", "TypeScript"],
            "explanation": "Strong backend microservice and API performance alignment."
        },
        {
            "fp": "fp_004_aetheria_health",
            "title": "Machine Learning Applied Scientist",
            "company": "Aetheria Health",
            "location": "Boston, MA",
            "employment_type": "Full-Time",
            "description": "Analyze clinical biomedical datasets and train predictive classifiers with Python and scikit-learn.",
            "url": "https://jobs.lever.co/anthropic/jobs/4",
            "source_name": "Lever",
            "score": 67.5,
            "category": "MEDIUM",
            "skill": 68, "exp": 70, "edu": 80, "resp": 65, "tech": 65, "pref": 60,
            "matched": ["Python", "Machine Learning", "SQL"],
            "missing": ["Bioinformatics", "Genomics"],
            "explanation": "Solid core ML foundation; candidate profile lacks specialized genomics experience."
        },
        {
            "fp": "fp_005_logitech",
            "title": "Junior Data Intelligence Analyst",
            "company": "LogiTech Systems",
            "location": "Austin, TX",
            "employment_type": "Full-Time",
            "description": "Perform SQL database querying, warehouse ETL operations, and weekly reporting.",
            "url": "https://news.ycombinator.com/jobs/5",
            "source_name": "RSS",
            "score": 48.0,
            "category": "LOW",
            "skill": 40, "exp": 55, "edu": 75, "resp": 45, "tech": 40, "pref": 50,
            "matched": ["SQL"],
            "missing": ["Tableau", "PowerBI"],
            "explanation": "Requires business intelligence reporting dashboards not highlighted in candidate resume."
        }
    ]

    for item in job_data:
        j = Job(fingerprint=item["fp"], title=item["title"], company=item["company"], location=item["location"], employment_type=item["employment_type"], description=item["description"], url=item["url"], source_name=item["source_name"])
        db.add(j); db.flush()
        score = JobScore(job_id=j.id, candidate_id=profile.id, final_score=item["score"], category=item["category"], skill_score=item["skill"], experience_score=item["exp"], education_score=item["edu"], responsibility_score=item["resp"], technology_score=item["tech"], preference_score=item["pref"], matched_skills=item["matched"], missing_skills=item["missing"], explanation=item["explanation"])
        db.add(score); db.flush()
        if item["score"] >= 85:
            db.add(Application(job_id=j.id, status="INTERVIEW", notes="Screening call scheduled with research lead"))
        elif item["score"] >= 75:
            db.add(Application(job_id=j.id, status="APPLIED", notes="Direct ATS application submitted"))
        elif item["score"] >= 65:
            db.add(Application(job_id=j.id, status="SAVED", notes="Under candidate consideration"))
    db.commit()

@app.on_event("startup")
def startup():
    init_db()
    with SessionLocal() as db:
        if not db.scalar(select(UserPreference)):
            db.add(UserPreference()); db.commit()
        seed_demo_data(db)

def authorized(token: str | None): return bool(token and token == settings.admin_token)
def require_token(token):
    if not authorized(token): raise HTTPException(status_code=401, detail="Unauthorized")

@app.get("/health")
def health(): return {"status":"ok","service":settings.app_name,"version":"2.0.0"}

@app.get("/",response_class=HTMLResponse)
def dashboard(request:Request, category:str|None=None):
    with SessionLocal() as db:
        profile=db.scalar(select(CandidateProfile).order_by(CandidateProfile.id.desc()))
        q=select(Job,JobScore).join(JobScore,Job.id==JobScore.job_id).order_by(JobScore.final_score.desc()).limit(200)
        if category: q=q.where(JobScore.category==category.upper())
        scores=db.execute(q).all()
        counts=db.execute(select(JobScore.category,func.count(JobScore.id)).group_by(JobScore.category)).all()
        applied=db.scalar(select(func.count(Application.id)).where(Application.status.in_(["APPLIED","INTERVIEW","OFFER"]))) or 0
        total_jobs=db.scalar(select(func.count(Job.id))) or 0
        active_sources=db.scalar(select(func.count(Source.id)).where(Source.enabled.is_(True))) or 0
        return templates.TemplateResponse("dashboard.html",{
            "request":request,
            "profile":profile,
            "scores":scores,
            "counts":dict(counts),
            "applied":applied,
            "total_jobs":total_jobs,
            "active_sources":active_sources,
            "selected_category":(category.upper() if category else "ALL")
        })

@app.get("/setup",response_class=HTMLResponse)
def setup(request:Request): return templates.TemplateResponse("setup.html",{"request":request})

@app.post("/setup")
async def setup_post(name:str=Form(...),resume:UploadFile=File(...)):
    suffix=Path(resume.filename or "resume.txt").suffix.lower()
    if suffix not in {".pdf",".docx",".txt",".md"}: raise HTTPException(400,"Upload PDF, DOCX, TXT or Markdown")
    data=await resume.read()
    if len(data)>8*1024*1024: raise HTTPException(400,"Resume must be 8 MB or smaller")
    path=UPLOADS/("resume"+suffix); path.write_bytes(data)
    text=extract_text(str(path)); profile=build_profile(text)
    with SessionLocal() as db:
        existing=db.scalar(select(CandidateProfile).order_by(CandidateProfile.id.desc()))
        if existing:
            existing.name=name; existing.resume_filename=resume.filename; existing.resume_text=text; existing.profile_json=profile
        else: db.add(CandidateProfile(name=name,resume_filename=resume.filename,resume_text=text,profile_json=profile))
        db.commit()
    return RedirectResponse("/",303)

@app.get("/sources",response_class=HTMLResponse)
def sources_page(request:Request):
    with SessionLocal() as db: sources=db.scalars(select(Source).order_by(Source.name)).all()
    return templates.TemplateResponse("sources.html",{"request":request,"sources":sources})

@app.get("/preferences",response_class=HTMLResponse)
def preferences_page(request:Request):
    with SessionLocal() as db: prefs=db.scalar(select(UserPreference).order_by(UserPreference.id.desc())) or UserPreference()
    return templates.TemplateResponse("preferences.html",{"request":request,"prefs":prefs})

@app.get("/applications",response_class=HTMLResponse)
def applications_page(request:Request):
    statuses=["SAVED","APPLIED","INTERVIEW","OFFER","REJECTED","WITHDRAWN"]
    with SessionLocal() as db:
        rows=[]
        q=select(Job,JobScore,Application).join(JobScore,Job.id==JobScore.job_id).join(Application,Job.id==Application.job_id,isouter=True).order_by(JobScore.final_score.desc())
        for j,s,a in db.execute(q).all():
            if a: rows.append({"id":j.id,"title":j.title,"company":j.company,"score":s.final_score,"status":a.status,"notes":a.notes,"url":j.url})
        status_counts={st: sum(1 for r in rows if r['status']==st) for st in statuses}
        return templates.TemplateResponse("applications.html",{"request":request,"rows":rows,"statuses":statuses,"status_counts":status_counts})

@app.post("/scan")
def scan(x_admin_token:str|None=Header(default=None)):
    require_token(x_admin_token)
    with SessionLocal() as db: return run_scan(db)

@app.get("/api/jobs")
def jobs(category:str|None=None,limit:int=100):
    with SessionLocal() as db:
        q=select(Job,JobScore).join(JobScore,Job.id==JobScore.job_id).order_by(JobScore.final_score.desc()).limit(min(limit,500))
        if category: q=q.where(JobScore.category==category.upper())
        rows=db.execute(q).all()
        return [{"id":j.id,"title":j.title,"company":j.company,"location":j.location,"url":j.url,"score":s.final_score,"category":s.category,"matched_skills":s.matched_skills,"missing_skills":s.missing_skills} for j,s in rows]

@app.post("/api/sources")
def add_source(payload:dict,x_admin_token:str|None=Header(default=None)):
    require_token(x_admin_token)
    if not {"name","kind","url"}.issubset(payload): raise HTTPException(400,"name, kind and url required")
    if payload["kind"] not in {"rss","html","greenhouse","lever","ashby"}: raise HTTPException(400,"Unsupported source kind")
    with SessionLocal() as db:
        src=Source(name=payload["name"],kind=payload["kind"],url=payload["url"],enabled=payload.get("enabled",True),config_json=payload.get("config_json",{})); db.add(src); db.commit(); db.refresh(src)
        return {"id":src.id,"name":src.name}

@app.patch("/api/sources/{source_id}")
def patch_source(source_id:int,payload:dict,x_admin_token:str|None=Header(default=None)):
    require_token(x_admin_token)
    with SessionLocal() as db:
        src=db.get(Source,source_id)
        if not src: raise HTTPException(404,"Source not found")
        for key in ["name","url","enabled","config_json"]:
            if key in payload: setattr(src,key,payload[key])
        db.commit(); return {"ok":True}

@app.get("/api/sources")
def list_sources():
    with SessionLocal() as db: return [{"id":s.id,"name":s.name,"kind":s.kind,"url":s.url,"enabled":s.enabled} for s in db.scalars(select(Source)).all()]

@app.get("/api/preferences")
def get_preferences():
    with SessionLocal() as db:
        p=db.scalar(select(UserPreference).order_by(UserPreference.id.desc()))
        return {c:getattr(p,c) for c in ["target_roles","preferred_locations","remote_enabled","internships_enabled","full_time_enabled","max_experience_years","required_skills","preferred_skills","exclude_keywords"]}

@app.post("/api/preferences")
def save_preferences(payload:dict,x_admin_token:str|None=Header(default=None)):
    require_token(x_admin_token)
    with SessionLocal() as db:
        p=db.scalar(select(UserPreference).order_by(UserPreference.id.desc())) or UserPreference()
        for key in ["target_roles","preferred_locations","remote_enabled","internships_enabled","full_time_enabled","max_experience_years","required_skills","preferred_skills","exclude_keywords"]:
            if key in payload: setattr(p,key,payload[key])
        db.add(p); db.commit(); return {"ok":True}

@app.post("/api/applications/{job_id}")
def set_application(job_id:int,payload:dict,x_admin_token:str|None=Header(default=None)):
    require_token(x_admin_token)
    status=payload.get("status","SAVED").upper()
    allowed={"SAVED","APPLIED","INTERVIEW","OFFER","REJECTED","WITHDRAWN"}
    if status not in allowed: raise HTTPException(400,"Invalid status")
    with SessionLocal() as db:
        if not db.get(Job,job_id): raise HTTPException(404,"Job not found")
        a=db.scalar(select(Application).where(Application.job_id==job_id))
        if not a: a=Application(job_id=job_id); db.add(a)
        a.status=status; a.notes=payload.get("notes",a.notes)
        if status=="APPLIED" and not a.applied_at: a.applied_at=datetime.now(timezone.utc)
        db.commit(); return {"ok":True,"status":a.status}
