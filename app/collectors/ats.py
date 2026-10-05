import httpx
from .base import Collector, RawJob
from ..config import settings
class GreenhouseCollector(Collector):
    def collect(self):
        board=self.source.url.rstrip("/").split("/")[-1]
        api=f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
        r=httpx.get(api,headers={"User-Agent":settings.user_agent},timeout=settings.request_timeout); r.raise_for_status(); data=r.json()
        return [RawJob(j.get("title",""), self.source.config_json.get("company",self.source.name), j.get("location",{}).get("name","") if isinstance(j.get("location"),dict) else str(j.get("location","")), "", j.get("content","") or "", j.get("absolute_url",self.source.url), self.source.name) for j in data.get("jobs",[])]
class LeverCollector(Collector):
    def collect(self):
        site=self.source.url.rstrip("/").split("/")[-1]
        api=f"https://api.lever.co/v0/postings/{site}?mode=json"
        r=httpx.get(api,headers={"User-Agent":settings.user_agent},timeout=settings.request_timeout); r.raise_for_status(); data=r.json()
        return [RawJob(j.get("text",""), self.source.config_json.get("company",self.source.name), j.get("categories",{}).get("location","") if isinstance(j.get("categories"),dict) else "", j.get("categories",{}).get("commitment","") if isinstance(j.get("categories"),dict) else "", j.get("descriptionPlain",""), j.get("hostedUrl",self.source.url), self.source.name) for j in data]
class AshbyCollector(Collector):
    def collect(self):
        # Ashby public job pages expose structured JSON; use configured API URL when supplied.
        api=self.source.config_json.get("api_url",self.source.url)
        r=httpx.get(api,headers={"User-Agent":settings.user_agent},timeout=settings.request_timeout); r.raise_for_status(); data=r.json()
        jobs=data.get("jobs",data if isinstance(data,list) else [])
        out=[]
        for j in jobs:
            out.append(RawJob(j.get("title",j.get("name","")),self.source.config_json.get("company",self.source.name),j.get("location",j.get("locationName","")),j.get("employmentType",""),j.get("descriptionPlain",j.get("description","")),j.get("jobUrl",j.get("url",self.source.url)),self.source.name))
        return out
