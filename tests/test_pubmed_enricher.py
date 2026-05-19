import pytest
import pandas as pd
from unittest.mock import patch, Mock

from src.pubmed_enricher import (
    search_pubmed_by_disease,
    get_mesh_terms,
    compute_gap_analysis,
    enrich_with_pubmed,
)


# ---------------------------------------------------------------------------
# search_pubmed_by_disease
# ---------------------------------------------------------------------------

@patch("src.pubmed_enricher.Entrez.read")
@patch("src.pubmed_enricher.Entrez.esearch")
def test_search_pubmed_by_disease_returns_int(mock_esearch, mock_read):
    mock_handle = Mock()
    mock_esearch.return_value = mock_handle
    mock_read.return_value = {"Count": "142"}

    result = search_pubmed_by_disease("Diabetes")

    assert result == 142
    assert isinstance(result, int)


@patch("src.pubmed_enricher.Entrez.esearch")
def test_search_pubmed_by_disease_returns_zero_on_error(mock_esearch):
    mock_esearch.side_effect = Exception("Network failure")

    result = search_pubmed_by_disease("Diabetes")

    assert result == 0


# ---------------------------------------------------------------------------
# get_mesh_terms
# ---------------------------------------------------------------------------

@patch("src.pubmed_enricher.Entrez.read")
@patch("src.pubmed_enricher.Entrez.efetch")
def test_get_mesh_terms_returns_list(mock_efetch, mock_read):
    mock_handle = Mock()
    mock_efetch.return_value = mock_handle

    mock_record = {
        "PubmedArticle": [
            {
                "MedlineCitation": {
                    "MeshHeadingList": [
                        {"DescriptorName": "Neoplasms"}
                    ]
                }
            }
        ]
    }
    mock_read.return_value = mock_record

    result = get_mesh_terms("12345678")

    assert isinstance(result, list)
    assert "Neoplasms" in result


@patch("src.pubmed_enricher.Entrez.efetch")
def test_get_mesh_terms_returns_empty_on_error(mock_efetch):
    mock_efetch.side_effect = Exception("API error")

    result = get_mesh_terms("12345678")

    assert result == []


# ---------------------------------------------------------------------------
# compute_gap_analysis
# ---------------------------------------------------------------------------

SAMPLE_TRIALS_DF = pd.DataFrame(
    {
        "nct_id": ["NCT001", "NCT002", "NCT003"],
        "disease": ["Cancer", "Cancer", "Diabetes"],
        "title": ["Study A", "Study B", "Study C"],
    }
)


@patch("src.pubmed_enricher.search_pubmed_by_disease")
def test_compute_gap_analysis_returns_dataframe(mock_search):
    mock_search.side_effect = lambda disease, **kwargs: 100 if disease == "Cancer" else 50

    result = compute_gap_analysis(SAMPLE_TRIALS_DF)

    assert isinstance(result, pd.DataFrame)
    assert set(result.columns) == {"disease", "trial_count", "pubmed_count", "ratio", "signal"}
    assert len(result) == 2  # two unique diseases


@patch("src.pubmed_enricher.search_pubmed_by_disease")
def test_gap_analysis_high_opportunity_signal(mock_search):
    # pubmed_count=500, trial_count=2 → ratio=250 → "High Opportunity"
    df = pd.DataFrame({"disease": ["RareDisease", "RareDisease"]})
    mock_search.return_value = 500

    result = compute_gap_analysis(df)

    assert "Opportunity" in result.loc[result["disease"] == "RareDisease", "signal"].values[0]


@patch("src.pubmed_enricher.search_pubmed_by_disease")
def test_gap_analysis_limited_research_signal(mock_search):
    # pubmed_count=2, trial_count=10 → ratio=0.2 → "Limited Research"
    df = pd.DataFrame({"disease": ["CommonDisease"] * 10})
    mock_search.return_value = 2

    result = compute_gap_analysis(df)

    assert "Limited" in result.loc[result["disease"] == "CommonDisease", "signal"].values[0]


# ---------------------------------------------------------------------------
# enrich_with_pubmed
# ---------------------------------------------------------------------------

@patch("src.pubmed_enricher.search_pubmed_by_disease")
def test_enrich_with_pubmed_adds_columns(mock_search):
    mock_search.return_value = 75

    result = enrich_with_pubmed(SAMPLE_TRIALS_DF)

    assert "pubmed_count" in result.columns
    assert "pub_trial_ratio" in result.columns


@patch("src.pubmed_enricher.search_pubmed_by_disease")
def test_enrich_with_pubmed_does_not_mutate_input(mock_search):
    mock_search.return_value = 75

    original_columns = list(SAMPLE_TRIALS_DF.columns)
    original_values = SAMPLE_TRIALS_DF.copy()

    enrich_with_pubmed(SAMPLE_TRIALS_DF)

    assert list(SAMPLE_TRIALS_DF.columns) == original_columns
    pd.testing.assert_frame_equal(SAMPLE_TRIALS_DF, original_values)
