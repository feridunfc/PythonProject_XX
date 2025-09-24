import json, logging
from sqlalchemy import create_engine, text
from ..config.settings import settings

logger = logging.getLogger(__name__)

class StateStore:
    def __init__(self, db_url: str | None = None):
        self.engine = create_engine(db_url or settings.db_url, future=True)

    def save_snapshot(self, sprint, report: dict, results: dict):
        with self.engine.begin() as conn:
            conn.exec_driver_sql("""
                CREATE TABLE IF NOT EXISTS snapshots(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sprint_id TEXT, report TEXT, results TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute(text("INSERT INTO snapshots (sprint_id, report, results) VALUES (:sid,:rep,:res)"),
                         {"sid": sprint.id, "rep": json.dumps(report), "res": json.dumps(results)})
            logger.info("Snapshot saved for sprint %s", sprint.id)
