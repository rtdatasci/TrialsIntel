import pytest
import pandas as pd
from src.database import init_db, save_trial, get_all_trials, search_trials


SAMPLE_TRIAL = {
    "nct_id": "NCT12345678",
    "title": "A Study of Drug X in Cancer",
    "summary": "Drug X study for cancer patients.",
    "conditions": "Lung Cancer",
    "interventions": "Drug X",
    "sponsor": "Pharma Corp",
    "phase": "PHASE2",
    "drug": "Drug X",
    "disease": "Lung Cancer",
    "mechanism": "EGFR inhibitor",
}

SAMPLE_TRIAL_2 = {
    "nct_id": "NCT99999999",
    "title": "Immunology Study of Drug Y",
    "summary": "Drug Y for rheumatoid arthritis.",
    "conditions": "Rheumatoid Arthritis",
    "interventions": "Drug Y",
    "sponsor": "BioTech Inc",
    "phase": "PHASE3",
    "drug": "Drug Y",
    "disease": "Rheumatoid Arthritis",
    "mechanism": None,
}


@pytest.fixture
def db_conn():
    """Provide an in-memory SQLite connection for each test."""
    import sqlite3
    conn = sqlite3.connect(":memory:")
    yield conn
    conn.close()


def test_init_db_creates_table(db_conn):
    init_db(conn=db_conn)
    cursor = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trials'")
    assert cursor.fetchone() is not None


def test_save_trial_inserts_row(db_conn):
    init_db(conn=db_conn)
    save_trial(SAMPLE_TRIAL, conn=db_conn)
    cursor = db_conn.execute("SELECT nct_id FROM trials")
    rows = cursor.fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "NCT12345678"


def test_save_trial_deduplicates_on_nct_id(db_conn):
    init_db(conn=db_conn)
    save_trial(SAMPLE_TRIAL, conn=db_conn)
    save_trial(SAMPLE_TRIAL, conn=db_conn)  # insert same trial again
    cursor = db_conn.execute("SELECT COUNT(*) FROM trials")
    assert cursor.fetchone()[0] == 1


def test_get_all_trials_returns_dataframe(db_conn):
    init_db(conn=db_conn)
    save_trial(SAMPLE_TRIAL, conn=db_conn)
    df = get_all_trials(conn=db_conn)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert "nct_id" in df.columns


def test_search_trials_filters_by_disease(db_conn):
    init_db(conn=db_conn)
    save_trial(SAMPLE_TRIAL, conn=db_conn)
    save_trial(SAMPLE_TRIAL_2, conn=db_conn)
    result = search_trials(disease="Cancer", conn=db_conn)
    assert len(result) == 1
    assert result.iloc[0]["nct_id"] == "NCT12345678"


def test_search_trials_filters_by_drug(db_conn):
    init_db(conn=db_conn)
    save_trial(SAMPLE_TRIAL, conn=db_conn)
    save_trial(SAMPLE_TRIAL_2, conn=db_conn)
    result = search_trials(drug="Drug Y", conn=db_conn)
    assert len(result) == 1
    assert result.iloc[0]["nct_id"] == "NCT99999999"


def test_search_trials_filters_by_phase(db_conn):
    init_db(conn=db_conn)
    save_trial(SAMPLE_TRIAL, conn=db_conn)
    save_trial(SAMPLE_TRIAL_2, conn=db_conn)
    result = search_trials(phase="PHASE3", conn=db_conn)
    assert len(result) == 1
    assert result.iloc[0]["nct_id"] == "NCT99999999"


def test_search_trials_no_filters_returns_all(db_conn):
    init_db(conn=db_conn)
    save_trial(SAMPLE_TRIAL, conn=db_conn)
    save_trial(SAMPLE_TRIAL_2, conn=db_conn)
    result = search_trials(conn=db_conn)
    assert len(result) == 2
