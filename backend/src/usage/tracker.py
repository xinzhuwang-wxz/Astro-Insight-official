import json
from pathlib import Path
from datetime import datetime

FILE = Path("api_usage.json")

def record(model="unknown", tokens=0):
    data = load()
    data.append({
        "time": datetime.utcnow().isoformat(),
        "model": model,
        "tokens": tokens
    })
    FILE.write_text(json.dumps(data, indent=2))

def load():
    if FILE.exists():
        return json.loads(FILE.read_text())
    return []

def summary():
    logs = load()
    return {
        "requests": len(logs),
        "tokens": sum(x.get("tokens",0) for x in logs),
        "logs": logs[-50:]
    }