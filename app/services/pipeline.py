import hashlib
from sqlalchemy import select
from ..models import CandidateProfile, Source, Job, JobScore, UserPreference
from ..collectors.registry import collector_for
from .scoring import score_job
from .alerts import send_telegram, send_email

def fingerprint(title, company, location, url):
    canonical=url.split("?")[0].rstrip("/").lower()
    raw="|".join([company.strip().lower(),title.strip().lower(),location.strip().lower(),canonical])
    return hashlib.sha256(raw.encode()).hexdigest()

def allowed_by_preferences(job, prefs):
    text=f"{job.title} {job.description} {job.employment_type}".lower()
    for term in (prefs.exclude_keywords if prefs else []):
        if term.lower() in text: return False
    if prefs:
        if not prefs.internships_enabled and "intern" in text: return False
        if not prefs.full_time_enabled and any(x in text for x in ["full-time","full time","permanent"]): return False
        if prefs.required_skills:
            if not all(s.lower() in text for s in prefs.required_skills): return False
    return True

def run_scan(db):
    profile=db.scalar(select(CandidateProfile).order_by(CandidateProfile.id.desc()))
    if not profile: return {"error":"Upload a resume first.","sources":0,"jobs":0,"high":0,"medium":0,"low":0}
    prefs=db.scalar(select(UserPreference).order_by(UserPreference.id.desc()))
    sources=db.scalars(select(Source).where(Source.enabled.is_(True))).all()
    discovered=high=medium=low=failed=0
    for source in sources:
        try:
            raw_jobs=collector_for(source).collect()
        except Exception:
            failed+=1; continue
        for r in raw_jobs:
            fp=fingerprint(r.title,r.company,r.location,r.url)
            job=db.scalar(select(Job).where(Job.fingerprint==fp))
            if not job:
                job=Job(fingerprint=fp,title=r.title[:400],company=r.company[:300],location=r.location[:500],employment_type=r.employment_type[:100],description=r.description,url=r.url,source_name=r.source_name,posted_at=r.posted_at)
                db.add(job); db.flush(); discovered+=1
            if not allowed_by_preferences(job,prefs):
                continue
            result=score_job(profile.profile_json,profile.resume_text,job.title,job.description,job.location,job.employment_type,prefs=prefs)
            existing=db.scalar(select(JobScore).where(JobScore.job_id==job.id,JobScore.candidate_id==profile.id))
            if existing:
                for k,v in result.items():
                    setattr(existing, "final_score" if k=="score" else k, v)
                score=existing
            else:
                payload=dict(result); payload["final_score"]=payload.pop("score")
                score=JobScore(job_id=job.id,candidate_id=profile.id,**payload); db.add(score); db.flush()
                if score.category=="HIGH":
                    high+=1; send_telegram(db,job,score); send_email(db,job,score)
                elif score.category=="MEDIUM": medium+=1
                else: low+=1
    db.commit()
    return {"sources":len(sources),"jobs":discovered,"high":high,"medium":medium,"low":low,"failed_sources":failed}
