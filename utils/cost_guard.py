import os, sqlite3, datetime, threading
_DB = os.getenv("COST_DB_PATH", "cost_monthly.db")
_LIMIT = float(os.getenv("MONTHLY_COST_LIMIT", "50.0"))
_lock = threading.Lock()

def _migrate(conn: sqlite3.Connection):
    conn.execute("CREATE TABLE IF NOT EXISTS spend(date TEXT NOT NULL, usd REAL NOT NULL)")
    conn.commit()

def spend(amount_usd: float) -> float:
    with _lock, sqlite3.connect(_DB) as c:
        _migrate(c)
        today = datetime.date.today()
        ym = today.strftime("%Y-%m")
        c.execute("INSERT INTO spend(date, usd) VALUES(?,?)", (today.isoformat(), float(amount_usd)))
        used = c.execute(
            "SELECT COALESCE(SUM(usd),0) FROM spend WHERE substr(date,1,7)=?", (ym,)
        ).fetchone()[0]
        if used > _LIMIT:
            raise RuntimeError(f"Monthly budget exceeded: used=${used:.2f} > limit=${_LIMIT:.2f}")
        return used