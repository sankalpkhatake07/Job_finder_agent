from dataclasses import dataclass
from datetime import datetime

@dataclass
class RawJob:
    title: str
    company: str
    location: str
    employment_type: str
    description: str
    url: str
    source_name: str
    posted_at: datetime | None = None

class Collector:
    def __init__(self, source): self.source = source
    def collect(self) -> list[RawJob]: raise NotImplementedError
