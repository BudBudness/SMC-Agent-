import json
from pathlib import Path
def append_event(path,event):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("a",encoding="utf-8") as f: f.write(json.dumps(event,default=str,sort_keys=True)+"\n")
def read_events(path):
    p=Path(path)
    return [] if not p.exists() else [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]
