import struct
import zlib
from datetime import datetime, timedelta, timezone

def decode_bi5(blob, day):
    raw=zlib.decompress(blob)
    rows=[]
    for i in range(0,len(raw)-19,20):
        ms,ask,bid,av,bv=struct.unpack(">IIIII",raw[i:i+20])
        ts=day.replace(tzinfo=timezone.utc)+timedelta(milliseconds=ms)
        rows.append({"timestamp":ts.isoformat(),"bid":bid/1e5,"ask":ask/1e5,"ask_volume":av,"bid_volume":bv})
    return rows

def ticks_to_rows(ticks):
    return [{"timestamp":t["timestamp"],"bid":t["bid"],"ask":t["ask"]} for t in ticks]
