import pytest
import pandas as pd
from src.search import search_by_keywords


@pytest.fixture
def sample_df():
    return pd.DataFrame([
        {"nct_id": "NCT001", "drug": "Pembrolizumab", "disease": "Lung Cancer", "phase": "PHASE2", "conditions": "NSCLC", "interventions": "Pembrolizumab"},
        {"nct_id": "NCT002", "drug": "Nivolumab", "disease": "Melanoma", "phase": "PHASE3", "conditions": "Melanoma", "interventions": "Nivolumab"},
        {"nct_id": "NCT003", "drug": "Drug Z", "disease": "Rheumatoid Arthritis", "phase": "PHASE1", "conditions": "RA", "interventions": "Drug Z"},
    ])


def test_filter_by_disease(sample_df):
    result = search_by_keywords(sample_df, disease="cancer")
    assert len(result) == 1
    assert result.iloc[0]["nct_id"] == "NCT001"


def test_filter_by_drug(sample_df):
    result = search_by_keywords(sample_df, drug="nivolumab")
    assert len(result) == 1
    assert result.iloc[0]["nct_id"] == "NCT002"


def test_filter_by_phase(sample_df):
    result = search_by_keywords(sample_df, phase="PHASE3")
    assert len(result) == 1
    assert result.iloc[0]["nct_id"] == "NCT002"


def test_no_filters_returns_all(sample_df):
    result = search_by_keywords(sample_df)
    assert len(result) == 3


def test_combined_filters(sample_df):
    result = search_by_keywords(sample_df, disease="cancer", phase="PHASE2")
    assert len(result) == 1
    assert result.iloc[0]["nct_id"] == "NCT001"


def test_no_match_returns_empty(sample_df):
    result = search_by_keywords(sample_df, disease="Diabetes")
    assert len(result) == 0


def test_case_insensitive_match(sample_df):
    result = search_by_keywords(sample_df, drug="PEMBROLIZUMAB")
    assert len(result) == 1
