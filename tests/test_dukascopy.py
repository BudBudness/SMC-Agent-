import struct,zlib
from datetime import datetime
from smc_agent.dukascopy import decode_bi5

def test_decoder():
    raw=struct.pack(">IIIII",1000,110000,109990,2,3)
    rows=decode_bi5(zlib.compress(raw),datetime(2026,1,1))
    assert rows[0]["bid"]==1.0999
