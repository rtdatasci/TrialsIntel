import pytest
from unittest.mock import patch, Mock
from src.fetch_trials import fetch_trials_from_api, _parse_study


SAMPLE_STUDY = {
    "protocolSection": {
        "identificationModule": {
            "nctId": "NCT12345678",
            "briefTitle": "A Study of Drug X in Cancer Patients"
        },
        "descriptionModule": {
            "briefSummary": "This study evaluates Drug X for treating cancer."
        },
        "conditionsModule": {
            "conditions": ["Lung Cancer", "NSCLC"]
        },
        "armsInterventionsModule": {
            "interventions": [
                {"name": "Drug X", "type": "Drug"}
            ]
        },
        "sponsorCollaboratorsModule": {
            "leadSponsor": {"name": "Pharma Corp"}
        },
        "designModule": {
            "phases": ["PHASE2"]
        }
    }
}


def test_parse_study_extracts_nct_id():
    result = _parse_study(SAMPLE_STUDY)
    assert result["nct_id"] == "NCT12345678"


def test_parse_study_extracts_title():
    result = _parse_study(SAMPLE_STUDY)
    assert result["title"] == "A Study of Drug X in Cancer Patients"


def test_parse_study_extracts_summary():
    result = _parse_study(SAMPLE_STUDY)
    assert "Drug X" in result["summary"]


def test_parse_study_extracts_conditions():
    result = _parse_study(SAMPLE_STUDY)
    assert "Lung Cancer" in result["conditions"]


def test_parse_study_extracts_interventions():
    result = _parse_study(SAMPLE_STUDY)
    assert "Drug X" in result["interventions"]


def test_parse_study_extracts_sponsor():
    result = _parse_study(SAMPLE_STUDY)
    assert result["sponsor"] == "Pharma Corp"


def test_parse_study_extracts_phase():
    result = _parse_study(SAMPLE_STUDY)
    assert result["phase"] == "PHASE2"


def test_parse_study_handles_missing_fields():
    minimal = {"protocolSection": {"identificationModule": {"nctId": "NCT00000001", "briefTitle": "Test"}}}
    result = _parse_study(minimal)
    assert result["nct_id"] == "NCT00000001"
    assert result["summary"] == ""
    assert result["conditions"] == ""
    assert result["interventions"] == ""
    assert result["sponsor"] == ""
    assert result["phase"] == ""


@patch("src.fetch_trials.requests.get")
def test_fetch_trials_returns_list(mock_get):
    mock_response = Mock()
    mock_response.json.return_value = {
        "studies": [SAMPLE_STUDY],
        "nextPageToken": None
    }
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    results = fetch_trials_from_api(query="cancer", max_results=1)
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0]["nct_id"] == "NCT12345678"


@patch("src.fetch_trials.requests.get")
def test_fetch_trials_handles_api_error(mock_get):
    mock_get.side_effect = Exception("Connection error")
    results = fetch_trials_from_api(query="cancer", max_results=5)
    assert results == []
