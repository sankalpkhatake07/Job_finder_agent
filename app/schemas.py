from pydantic import BaseModel, Field, HttpUrl

class SourceIn(BaseModel):
    name: str
    kind: str = Field(pattern="^(rss|html|greenhouse|lever|ashby)$")
    url: HttpUrl
    enabled: bool = True
    config_json: dict = {}

class ScoreOut(BaseModel):
    score: float
    category: str
    matched_skills: list[str]
    missing_skills: list[str]
    explanation: str
