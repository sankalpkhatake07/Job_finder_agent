from .rss import RSSCollector
from .html import HTMLCollector
from .ats import GreenhouseCollector, LeverCollector, AshbyCollector
MAP={"rss":RSSCollector,"html":HTMLCollector,"greenhouse":GreenhouseCollector,"lever":LeverCollector,"ashby":AshbyCollector}
def collector_for(source): return MAP[source.kind](source)
