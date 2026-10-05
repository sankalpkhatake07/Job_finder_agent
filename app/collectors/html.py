import hashlib
import httpx
from bs4 import BeautifulSoup
from .base import Collector, RawJob
from ..config import settings
class HTMLCollector(Collector):
    def collect(self):
        r=httpx.get(self.source.url, headers={"User-Agent":settings.user_agent}, timeout=settings.request_timeout, follow_redirects=True)
        r.raise_for_status(); soup=BeautifulSoup(r.text,"html.parser")
        cfg=self.source.config_json
        jobs=[]
        selectors=cfg.get("job_selector")
        if not selectors: selectors=["article", "li", ".job", ".job-card", ".job-listing"]
        nodes=[]
        for sel in selectors:
            nodes.extend(soup.select(sel))
        seen=set()
        for n in nodes:
            title_node=n.select_one(cfg.get("title_selector","h2, h3, h4, .title, .job-title"))
            link_node=n.select_one(cfg.get("link_selector","a[href]"))
            if not title_node or not link_node: continue
            title=title_node.get_text(" ",strip=True); url=link_node.get("href","")
            if url.startswith("/"):
                from urllib.parse import urljoin
                url=urljoin(self.source.url,url)
            if not title or not url or url in seen: continue
            seen.add(url)
            desc=n.get_text(" ",strip=True)
            jobs.append(RawJob(title=title, company=cfg.get("company",self.source.name), location=cfg.get("location",""), employment_type=cfg.get("employment_type",""), description=desc, url=url, source_name=self.source.name))
        return jobs[:cfg.get("max_items",200)]
