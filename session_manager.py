import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class SessionManager:
    def __init__(self, session_dir: str = "sessions"):
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)

    def save(self, name: str, query_params, results, compliance_report, user: str):
        filename = self.session_dir / (name.replace(" ", "_") + ".json")

        data = {
            "name": name,
            "query_params": query_params,
            "results": results,
            "compliance_report": compliance_report,
            "user": user,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        filename.write_text(json.dumps(data, indent=2))
        return str(filename.resolve())

    def load(self, name: str):
        filename = self.session_dir / (name.replace(" ", "_") + ".json")
        return json.loads(filename.read_text())
