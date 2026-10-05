import re
from rapidfuzz import fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

ROLE_TERMS = ["ai engineer", "machine learning", "ml engineer", "data scientist", "data science", "computer vision", "python developer", "software engineer", "ai/ml", "intern"]

def _tokens(s): return set(re.findall(r"[a-zA-Z0-9+#.\-]+", s.lower()))

def _skill_score(profile, job_text):
    skills = profile.get("skills", [])
    lower = job_text.lower()
    matched = [s for s in skills if s.lower() in lower]
    return (len(matched) / max(1, len(skills))) * 100, matched

def _semantic(profile_text, job_text):
    if not profile_text.strip() or not job_text.strip(): return 0
    vec = TfidfVectorizer(stop_words="english", max_features=5000)
    try:
        x = vec.fit_transform([profile_text[:20000], job_text[:20000]])
        return float(cosine_similarity(x[0:1], x[1:2])[0][0] * 100)
    except ValueError:
        return 0

def _experience(job_text):
    lower = job_text.lower()
    if any(x in lower for x in ["fresher", "0-1 year", "0 to 1 year", "0–1 year", "entry level", "internship"]): return 100
    if any(x in lower for x in ["1-2 years", "1 to 2 years", "0-2 years", "0 to 2 years", "1–2 years"]): return 90
    if re.search(r"[3-5]\+?\s+years", lower): return 45
    if re.search(r"[6-9]\+?\s+years|10\+\s+years", lower): return 15
    return 70

def _education(profile, job_text):
    lower = job_text.lower()
    edu = " ".join(profile.get("education", []))
    if any(x in lower for x in ["b.tech", "btech", "b.e.", "bachelor", "computer science", "engineering"]):
        return 100 if edu else 75
    return 80

def _preference(job_text):
    lower = job_text.lower()
    role_hits = sum(1 for x in ROLE_TERMS if x in lower)
    return min(100, 50 + role_hits * 10)

def score_job(profile: dict, resume_text: str, title: str, description: str, location: str = "", employment_type: str = "", prefs=None):
    job_text = f"{title}\n{description}\n{location}\n{employment_type}"
    skill, matched = _skill_score(profile, job_text)
    missing = [s for s in profile.get("skills", []) if s not in matched]
    exp = _experience(job_text)
    edu = _education(profile, job_text)
    semantic = _semantic(resume_text, job_text)
    preference = _preference(job_text)
    if prefs and prefs.target_roles:
        role_text = title.lower()
        role_hits = sum(1 for r in prefs.target_roles if r.lower() in role_text)
        preference = min(100, preference + role_hits * 15)
    if prefs and prefs.preferred_locations:
        loc = location.lower()
        if any(x.lower() in loc for x in prefs.preferred_locations): preference = min(100, preference + 10)
    if prefs and prefs.remote_enabled and "remote" in job_text.lower(): preference = min(100, preference + 10)
    # Responsibility is represented by semantic similarity; technology by skills.
    responsibility = semantic
    technology = skill
    final = round((skill * .40) + (exp * .20) + (edu * .10) + (responsibility * .15) + (technology * .10) + (preference * .05), 2)
    if final >= 75: category = "HIGH"
    elif final >= 55: category = "MEDIUM"
    else: category = "LOW"
    explanation = f"{category} match at {final:.1f}%. Matched {len(matched)} candidate skills. Semantic/responsibility similarity: {semantic:.1f}%. Experience fit: {exp:.0f}%."
    return {"score": final, "category": category, "skill_score": skill, "experience_score": exp, "education_score": edu, "responsibility_score": responsibility, "technology_score": technology, "preference_score": preference, "matched_skills": matched, "missing_skills": missing, "explanation": explanation}
