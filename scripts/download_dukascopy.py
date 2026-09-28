#!/usr/bin/env python3
"""Download EURUSD tick history from Dukascopy's requester-pays S3 archive.

Requires AWS credentials with access to the public requester-pays bucket.
Raw tick files are daily .bi5 files; this script downloads only the requested
date range and leaves decoding to the next pipeline stage.
"""
import argparse
import subprocess
from datetime import date,timedelta
from pathlib import Path

BUCKET="s3://cfg-public-proper-wallaby"
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--start",required=True,help="YYYY-MM-DD")
    p.add_argument("--end",required=True,help="YYYY-MM-DD")
    p.add_argument("--out",default="data/raw/EURUSD")
    a=p.parse_args()
    start=date.fromisoformat(a.start); end=date.fromisoformat(a.end)
    if end<start: raise SystemExit("end before start")
    out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    d=start
    while d<=end:
        key=f"EURUSD/{d:%Y}/{d.month-1:02d}/{d.day}_ticks.bi5"
        dest=out/key.split("/",1)[1]
        dest.parent.mkdir(parents=True,exist_ok=True)
        cmd=["aws","s3","cp",f"{BUCKET}/{key}",str(dest),"--region","eu-west-1","--request-payer","requester","--only-show-errors"]
        subprocess.run(cmd,check=False)
        d+=timedelta(days=1)
if __name__=="__main__": main()
