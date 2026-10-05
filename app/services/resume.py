import re
from pathlib import Path
import fitz
from docx import Document

SKILL_ALIASES = {
    "python": "python", "java": "java", "c++": "c++", "sql": "sql", "typescript": "typescript",
    "machine learning": "machine learning", "ml": "machine learning", "deep learning": "deep learning",
    "computer vision": "computer vision", "opencv": "opencv", "pytorch": "pytorch", "tensorflow": "tensorflow",
    "scikit-learn": "scikit-learn", "sklearn": "scikit-learn", "pandas": "pandas", "numpy": "numpy",
    "fastapi": "fastapi", "django": "django", "flask": "flask", "react": "react", "next.js": "next.js",
    "postgresql": "postgresql", "postgres": "postgresql", "mysql": "mysql", "mongodb": "mongodb",
    "redis": "redis", "docker": "docker", "kubernetes": "kubernetes", "aws": "aws", "azure": "azure",
    "gcp": "gcp", "firebase": "firebase", "spark": "spark", "etl": "etl", "langchain": "langchain",
    "langgraph": "langgraph", "rag": "rag", "generative ai": "generative ai", "llm": "llm",
    "git": "git", "github": "github", "linux": "linux", "rest api": "rest api", "api": "api",
}

def extract_text(path: str) -> str:
    p = Path(path)
    if p.suffix.lower() == ".pdf":
        with fitz.open(path) as doc:
            return "\n".join(page.get_text() for page in doc)
    if p.suffix.lower() == ".docx":
        doc = Document(path)
        return "\n".join(x.text for x in doc.paragraphs)
    return p.read_text(encoding="utf-8", errors="ignore")

def extract_skills(text: str) -> list[str]:
    lower = text.lower()
    found = {canonical for alias, canonical in SKILL_ALIASES.items() if re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", lower)}
    return sorted(found)

def build_profile(text: str) -> dict:
    skills = extract_skills(text)
    roles = []
    role_patterns = ["ai engineer", "machine learning engineer", "ml engineer", "data scientist", "data analyst", "computer vision engineer", "python developer", "ai/ml intern", "ml intern", "data science intern", "software engineer"]
    lower = text.lower()
    for role in role_patterns:
        if role in lower: roles.append(role)
    education = []
    for term in ["b.tech", "btech", "b.e.", "bachelor", "m.tech", "mtech", "master"]:
        if term in lower: education.append(term)
    return {"skills": skills, "target_roles": sorted(set(roles)), "education": education, "keywords": skills}
