import math
import pytest
import pandas as pd
from unittest.mock import patch, Mock

from src.repurposing import get_original_indication, find_repurposing_candidates


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_response(payload: dict, status_code: int = 200) -> Mock:
    """Return a minimal requests.Response mock."""
    mock_resp = Mock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = payload
    return mock_resp


def _trials_df(*rows) -> pd.DataFrame:
    """Build a minimal trials DataFrame from (drug, disease) tuples."""
    return pd.DataFrame(rows, columns=["drug", "disease"])


# ---------------------------------------------------------------------------
# get_original_indication
# ---------------------------------------------------------------------------

@patch("src.repurposing.requests.get")
@patch("src.repurposing.get_chembl_data")
def test_get_original_indication_returns_mesh_heading(
    mock_get_chembl_data, mock_requests_get
):
    """Should return the MeSH heading of the top drug_indication entry."""
    mock_get_chembl_data.return_value = {"chembl_id": "CHEMBL123"}
    mock_requests_get.return_value = _make_mock_response(
        {
            "drug_indications": [
                {
                    "mesh_heading": "Diabetes Mellitus",
                    "efo_term": "type 2 diabetes",
                    "max_phase_for_ind": 4,
                }
            ]
        }
    )

    result = get_original_indication("metformin")

    assert result == "Diabetes Mellitus"


@patch("src.repurposing.get_chembl_data")
def test_get_original_indication_returns_none_when_no_chembl_data(
    mock_get_chembl_data,
):
    """Should return None when get_chembl_data returns None."""
    mock_get_chembl_data.return_value = None

    result = get_original_indication("unknown_drug")

    assert result is None


@patch("src.repurposing.requests.get")
@patch("src.repurposing.get_chembl_data")
def test_get_original_indication_returns_none_on_http_error(
    mock_get_chembl_data, mock_requests_get
):
    """Should return None (and not raise) when the requests.get call raises."""
    mock_get_chembl_data.return_value = {"chembl_id": "CHEMBL123"}
    mock_requests_get.side_effect = Exception("Connection timeout")

    result = get_original_indication("metformin")

    assert result is None


# ---------------------------------------------------------------------------
# find_repurposing_candidates
# ---------------------------------------------------------------------------

@patch("src.repurposing.get_original_indication")
def test_find_repurposing_candidates_returns_dataframe(mock_get_original_indication):
    """
    Drug tested in 2 diseases; original indication is a third, different disease.
    Should return a non-empty DataFrame with all expected columns.
    """
    mock_get_original_indication.return_value = "Heart Failure"

    df = _trials_df(
        ("imatinib", "Lung Cancer"),
        ("imatinib", "Breast Cancer"),
    )

    result = find_repurposing_candidates(df)

    expected_columns = {
        "drug",
        "original_indication",
        "new_indications",
        "new_indication_count",
        "signal_strength",
        "signal_label",
    }
    assert not result.empty
    assert expected_columns.issubset(set(result.columns))
    assert result.iloc[0]["drug"] == "imatinib"


@patch("src.repurposing.get_original_indication")
def test_find_repurposing_signal_label_novel_repurposing(mock_get_original_indication):
    """
    Drug tested in 4+ diseases different from its original indication.
    signal_label should contain 'Novel'.
    """
    mock_get_original_indication.return_value = "Unrelated Disease"

    df = _trials_df(
        ("imatinib", "Lung Cancer"),
        ("imatinib", "Breast Cancer"),
        ("imatinib", "Pancreatic Cancer"),
        ("imatinib", "Ovarian Cancer"),
    )

    result = find_repurposing_candidates(df)

    assert not result.empty
    row = result[result["drug"] == "imatinib"].iloc[0]
    assert "Novel" in row["signal_label"]


@patch("src.repurposing.get_original_indication")
def test_find_repurposing_signal_label_single_new_use(mock_get_original_indication):
    """
    Drug tested in exactly 1 disease different from its original indication.
    signal_label should contain 'Single'.
    """
    mock_get_original_indication.return_value = "Unrelated Disease"

    df = _trials_df(
        ("metformin", "Polycystic Ovary Syndrome"),
    )

    result = find_repurposing_candidates(df)

    assert not result.empty
    row = result[result["drug"] == "metformin"].iloc[0]
    assert "Single" in row["signal_label"]


@patch("src.repurposing.get_original_indication")
def test_find_repurposing_skips_nan_drugs(mock_get_original_indication):
    """
    A NaN value in the 'drug' column should not raise an exception.
    """
    mock_get_original_indication.return_value = "Unrelated Disease"

    df = pd.DataFrame(
        {
            "drug": ["aspirin", float("nan"), "aspirin"],
            "disease": ["Fever", "Fever", "Headache"],
        }
    )

    # Should complete without raising
    result = find_repurposing_candidates(df)

    assert isinstance(result, pd.DataFrame)


@patch("src.repurposing.get_original_indication")
def test_find_repurposing_returns_empty_dataframe_on_no_candidates(
    mock_get_original_indication,
):
    """
    When the original indication matches every disease in the trials,
    no new indications exist and the result should be an empty DataFrame
    with the correct columns.
    """
    mock_get_original_indication.return_value = "Diabetes Mellitus"

    df = _trials_df(
        ("metformin", "Diabetes Mellitus"),
    )

    result = find_repurposing_candidates(df)

    assert result.empty
    expected_columns = [
        "drug",
        "original_indication",
        "new_indications",
        "new_indication_count",
        "signal_strength",
        "signal_label",
    ]
    assert list(result.columns) == expected_columns


@patch("src.repurposing.get_original_indication")
def test_find_repurposing_handles_none_original_indication(
    mock_get_original_indication,
):
    """
    When get_original_indication returns None for all drugs, every observed
    disease counts as a new indication.  The function should still return a
    valid DataFrame without raising.
    """
    mock_get_original_indication.return_value = None

    df = _trials_df(
        ("aspirin", "Fever"),
        ("aspirin", "Headache"),
    )

    result = find_repurposing_candidates(df)

    assert isinstance(result, pd.DataFrame)
    # Both diseases are new indications when original is None
    assert not result.empty
    row = result[result["drug"] == "aspirin"].iloc[0]
    assert row["new_indication_count"] == 2
