import sqlite3
import pandas as pd
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent.parent / "data" / "trials.db"

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS trials (
    nct_id TEXT PRIMARY KEY,
    title TEXT,
    summary TEXT,
    conditions TEXT,
    interventions TEXT,
    sponsor TEXT,
    phase TEXT,
    drug TEXT,
    disease TEXT,
    mechanism TEXT
)
"""


def _get_conn(conn=None) -> sqlite3.Connection:
    if conn is not None:
        return conn
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(DB_PATH))


def init_db(conn=None) -> None:
    """Create SQLite database with trials table."""
    c = _get_conn(conn)
    c.execute(CREATE_TABLE_SQL)
    c.commit()
    if conn is None:
        c.close()


def save_trial(trial_data: dict, conn=None) -> None:
    """Insert or replace a trial into the database."""
    c = _get_conn(conn)
    c.execute("""
        INSERT OR REPLACE INTO trials
            (nct_id, title, summary, conditions, interventions, sponsor, phase, drug, disease, mechanism)
        VALUES
            (:nct_id, :title, :summary, :conditions, :interventions, :sponsor, :phase, :drug, :disease, :mechanism)
    """, trial_data)
    c.commit()
    if conn is None:
        c.close()


def get_all_trials(conn=None) -> pd.DataFrame:
    """Return all trials as a pandas DataFrame."""
    c = _get_conn(conn)
    df = pd.read_sql_query("SELECT * FROM trials", c)
    if conn is None:
        c.close()
    return df


def search_trials(disease: Optional[str] = None, drug: Optional[str] = None,
                  phase: Optional[str] = None, conn=None) -> pd.DataFrame:
    """Filter trials by keyword (case-insensitive substring match)."""
    query = "SELECT * FROM trials WHERE 1=1"
    params = []
    if disease:
        query += " AND (LOWER(disease) LIKE ? OR LOWER(conditions) LIKE ?)"
        params += [f"%{disease.lower()}%", f"%{disease.lower()}%"]
    if drug:
        query += " AND (LOWER(drug) LIKE ? OR LOWER(interventions) LIKE ?)"
        params += [f"%{drug.lower()}%", f"%{drug.lower()}%"]
    if phase:
        query += " AND LOWER(phase) LIKE ?"
        params += [f"%{phase.lower()}%"]
    c = _get_conn(conn)
    df = pd.read_sql_query(query, c, params=params)
    if conn is None:
        c.close()
    return df


if __name__ == "__main__":
    init_db()
    print("Database initialized at", DB_PATH)
