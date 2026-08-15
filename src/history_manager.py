import json
import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class HistoryManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self._ensure_dir()

    def _ensure_dir(self):
        dir_path = os.path.dirname(self.filepath)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)

    def load_history(self) -> List[Dict[str, Any]]:
        """Load history list from disk."""
        if not os.path.exists(self.filepath):
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return []
        except Exception as e:
            logger.warning(f"Failed to read history from {self.filepath}: {e}. Returning empty list.")
            return []

    def get_excluded_keys(self) -> Set[str]:
        """Return set of problem keys already sent in history."""
        history = self.load_history()
        keys = set()
        for item in history:
            key = item.get("key")
            if key:
                keys.add(key.upper())
            else:
                contest_id = item.get("contestId")
                index = item.get("index")
                if contest_id and index:
                    keys.add(f"{contest_id}{index.strip().upper()}")
        return keys

    def record_problem(self, problem: Dict[str, Any]):
        """Record newly sent problem into history."""
        history = self.load_history()
        
        record = {
            "key": problem.get("key"),
            "contestId": problem.get("contestId"),
            "index": problem.get("index"),
            "name": problem.get("name"),
            "rating": problem.get("rating"),
            "tags": problem.get("tags", []),
            "url": problem.get("url"),
            "sent_at": datetime.now(timezone.utc).isoformat()
        }
        
        history.append(record)
        
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
            logger.info(f"Recorded problem {record['key']} in {self.filepath}")
        except Exception as e:
            logger.error(f"Failed to write history file: {e}")
            raise
