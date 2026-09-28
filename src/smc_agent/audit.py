import json
from datetime import datetime,timezone
from pathlib import Path

class AuditLog:
    def __init__(self,path="logs/audit.jsonl"):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
    def write(self,event:str,payload:dict):
        row={"ts":datetime.now(timezone.utc).isoformat(),"event":event,"payload":payload}
        with self.path.open("a",encoding="utf-8") as f:
            f.write(json.dumps(row,separators=(",",":"))+"\n")
