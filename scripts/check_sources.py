#!/usr/bin/env python3
"""Daily change detection, not automatic audition verification."""
import json, hashlib, urllib.request, datetime, pathlib
sources={
"creede":"https://creederep.org/work-with-us/job-opportunities/",
"weathervane":"https://weathervaneplayhouse.org/audition-information/",
"woodstock":"https://www.woodstockplayhouse.org/employment-casting",
"fpta":"https://www.fpta.net/audition-info",
"alhambra":"https://www.alhambrajax.com/employment/"
}
path=pathlib.Path("data/source-status.json")
old=json.loads(path.read_text()) if path.exists() else {"sources":{}}
now=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
out={"checked_at":now,"sources":{}}
for key,url in sources.items():
    previous=old.get("sources",{}).get(key,{})
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"StageDoorAuditionMonitor/1.0 (public audition page checker)"})
        with urllib.request.urlopen(req,timeout=18) as response:
            body=response.read(1_000_000)
        digest=hashlib.sha256(body).hexdigest()
        status="Changed since previous check" if previous.get("sha256") and previous["sha256"]!=digest else "Checked; no change detected"
        out["sources"][key]={"status":status,"checked_at":now,"sha256":digest,"url":url}
    except Exception as exc:
        out["sources"][key]={"status":"Check failed","checked_at":now,"url":url,"error":type(exc).__name__,"sha256":previous.get("sha256","")}
path.parent.mkdir(parents=True,exist_ok=True)
path.write_text(json.dumps(out,indent=2)+"\n")
