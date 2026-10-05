import feedparser
from .base import Collector, RawJob
class RSSCollector(Collector):
    def collect(self):
        feed = feedparser.parse(self.source.url)
        jobs=[]
        for e in feed.entries:
            jobs.append(RawJob(title=e.get("title","Untitled"), company=self.source.config_json.get("company", self.source.name), location=e.get("location", self.source.config_json.get("location","")), employment_type=self.source.config_json.get("employment_type",""), description=e.get("summary", e.get("description","")), url=e.get("link", self.source.url), source_name=self.source.name))
        return jobs
