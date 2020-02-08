from datetime import datetime, timezone

def now(ts=False):
    utc = datetime.now(timezone.utc)
    return utc.timestamp() if ts else utc
