import pytest
import pandas as pd
from unittest.mock import patch, Mock
from src.chembl_enricher import get_chembl_data, enrich_with_chembl


# ---------------------------------------------------------------------------
# Shared mock payloads
# ---------------------------------------------------------------------------

SEARCH_PAYLOAD = {
    "molecules": [{"molecule_chembl_id": "CHEMBL941"}]
}

DETAIL_PAYLOAD = {
    "max_phase": 4,
    "molecule_type": "Small molecule"
}

MECH_PAYLOAD = {
    "mechanisms": [
        {"target_chembl_id": "CHEMBL2695761", "mechanism_of_action": "BCR-ABL inhibitor"},
    ]
}


def _make_mock_response(payload, status_code=200):
    """Return a Mock that behaves like a successful requests.Response."""
    mock = Mock()
    mock.status_code = status_code
    mock.json.return_value = payload
    mock.raise_for_status = Mock()
    return mock


# ---------------------------------------------------------------------------
# get_chembl_data tests
# ---------------------------------------------------------------------------

@patch("src.chembl_enricher.requests.get")
def test_get_chembl_data_returns_expected_keys(mock_get):
    search_mock = _make_mock_response(SEARCH_PAYLOAD)
    detail_mock = _make_mock_response(DETAIL_PAYLOAD)
    mech_mock = _make_mock_response(MECH_PAYLOAD)
    mock_get.side_effect = [search_mock, detail_mock, mech_mock]

    result = get_chembl_data("imatinib")

    assert result is not None
    assert set(result.keys()) == {"chembl_id", "max_phase", "molecule_type", "targets", "mechanisms"}


@patch("src.chembl_enricher.requests.get")
def test_get_chembl_data_returns_none_when_no_molecules(mock_get):
    search_mock = _make_mock_response({"molecules": []})
    mock_get.side_effect = [search_mock]

    result = get_chembl_data("unknowndrug")

    assert result is None


@patch("src.chembl_enricher.requests.get")
def test_get_chembl_data_returns_none_on_http_error(mock_get):
    mock_get.side_effect = Exception("connection error")

    result = get_chembl_data("imatinib")

    assert result is None


@patch("src.chembl_enricher.requests.get")
def test_get_chembl_data_filters_empty_targets(mock_get):
    mech_payload_with_none = {
        "mechanisms": [
            {"target_chembl_id": None, "mechanism_of_action": "Unknown mechanism"},
            {"target_chembl_id": "CHEMBL2695761", "mechanism_of_action": "BCR-ABL inhibitor"},
        ]
    }
    search_mock = _make_mock_response(SEARCH_PAYLOAD)
    detail_mock = _make_mock_response(DETAIL_PAYLOAD)
    mech_mock = _make_mock_response(mech_payload_with_none)
    mock_get.side_effect = [search_mock, detail_mock, mech_mock]

    result = get_chembl_data("imatinib")

    assert result is not None
    assert result["targets"] == ["CHEMBL2695761"]
    assert None not in result["targets"]


# ---------------------------------------------------------------------------
# enrich_with_chembl tests
# ---------------------------------------------------------------------------

@patch("src.chembl_enricher.get_chembl_data")
def test_enrich_with_chembl_merges_data(mock_get_chembl_data):
    mock_get_chembl_data.return_value = {
        "chembl_id": "CHEMBL941",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["CHEMBL2695761"],
        "mechanisms": ["BCR-ABL inhibitor"],
    }
    df = pd.DataFrame({"drug": ["imatinib"], "nct_id": ["NCT00000001"]})

    enriched = enrich_with_chembl(df)

    assert "chembl_id" in enriched.columns
    assert enriched.loc[0, "chembl_id"] == "CHEMBL941"


@patch("src.chembl_enricher.get_chembl_data")
def test_enrich_with_chembl_returns_original_on_no_data(mock_get_chembl_data):
    mock_get_chembl_data.return_value = None
    df = pd.DataFrame({"drug": ["unknowndrug"], "nct_id": ["NCT00000002"]})

    enriched = enrich_with_chembl(df)

    assert list(enriched.columns) == list(df.columns)
    assert len(enriched) == len(df)


@patch("src.chembl_enricher.get_chembl_data")
def test_enrich_with_chembl_skips_nan_drugs(mock_get_chembl_data):
    mock_get_chembl_data.return_value = None
    df = pd.DataFrame({"drug": ["imatinib", None], "nct_id": ["NCT00000003", "NCT00000004"]})

    # Should not raise; NaN rows must be preserved
    enriched = enrich_with_chembl(df)

    assert len(enriched) == 2
    mock_get_chembl_data.assert_called_once_with("imatinib")
