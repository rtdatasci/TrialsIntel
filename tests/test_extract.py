import pytest
import json
from unittest.mock import patch, Mock, MagicMock
from src.extract_entities import extract_with_claude, _build_prompt, _parse_response


SAMPLE_TRIAL_TEXT = "A Phase 2 Study of Pembrolizumab in Non-Small Cell Lung Cancer. This study evaluates the PD-1 inhibitor pembrolizumab (Keytruda) for NSCLC. Sponsored by Merck."

VALID_CLAUDE_JSON = json.dumps({
    "drug": "Pembrolizumab",
    "disease": "Non-Small Cell Lung Cancer",
    "sponsor": "Merck",
    "phase": "Phase 2",
    "mechanism": "PD-1 inhibitor"
})


def test_build_prompt_contains_trial_text():
    prompt = _build_prompt(SAMPLE_TRIAL_TEXT)
    assert SAMPLE_TRIAL_TEXT in prompt


def test_build_prompt_requests_json():
    prompt = _build_prompt(SAMPLE_TRIAL_TEXT)
    assert "JSON" in prompt


def test_parse_response_valid_json():
    result = _parse_response(VALID_CLAUDE_JSON)
    assert result["drug"] == "Pembrolizumab"
    assert result["disease"] == "Non-Small Cell Lung Cancer"
    assert result["mechanism"] == "PD-1 inhibitor"


def test_parse_response_handles_json_wrapped_in_markdown():
    wrapped = f"```json\n{VALID_CLAUDE_JSON}\n```"
    result = _parse_response(wrapped)
    assert result["drug"] == "Pembrolizumab"


def test_parse_response_returns_nulls_on_invalid_json():
    result = _parse_response("not json at all")
    assert result["drug"] is None
    assert result["disease"] is None
    assert result["sponsor"] is None
    assert result["phase"] is None
    assert result["mechanism"] is None


@patch("src.extract_entities.anthropic.Anthropic")
def test_extract_with_claude_returns_dict(mock_anthropic_class):
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=VALID_CLAUDE_JSON)]
    mock_client.messages.create.return_value = mock_message

    result = extract_with_claude(SAMPLE_TRIAL_TEXT)
    assert result["drug"] == "Pembrolizumab"
    assert result["phase"] == "Phase 2"


@patch("src.extract_entities.anthropic.Anthropic")
def test_extract_with_claude_handles_api_error(mock_anthropic_class):
    mock_client = MagicMock()
    mock_anthropic_class.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API error")

    result = extract_with_claude(SAMPLE_TRIAL_TEXT)
    assert result["drug"] is None
    assert result["disease"] is None
