import json
import re
import anthropic
from dotenv import load_dotenv

load_dotenv()

_NULL_RESULT = {
    "drug": None,
    "disease": None,
    "sponsor": None,
    "phase": None,
    "mechanism": None,
}

EXTRACTION_PROMPT = """You are extracting structured information from clinical trial data.

Given this trial description, extract the following information and return ONLY a JSON object:
{{
    "drug": "primary drug or intervention name",
    "disease": "primary disease or condition",
    "sponsor": "sponsoring organization",
    "phase": "trial phase (e.g., Phase 1, Phase 2, etc.)",
    "mechanism": "mechanism of action if mentioned, otherwise null"
}}

If any field cannot be determined, use null.

Trial description:
{trial_text}

Return only the JSON, no other text."""


def _build_prompt(trial_text: str) -> str:
    return EXTRACTION_PROMPT.format(trial_text=trial_text)


def _parse_response(raw: str) -> dict:
    """Parse Claude's text response into a dict. Handles markdown code fences."""
    text = raw.strip()
    text = re.sub(r"^```(?:json)?\n?", "", text)
    text = re.sub(r"\n?```$", "", text)
    try:
        data = json.loads(text)
        return {
            "drug": data.get("drug"),
            "disease": data.get("disease"),
            "sponsor": data.get("sponsor"),
            "phase": data.get("phase"),
            "mechanism": data.get("mechanism"),
        }
    except json.JSONDecodeError:
        print(f"[extract_entities] Failed to parse JSON: {text[:100]}")
        return dict(_NULL_RESULT)


def extract_with_claude(trial_text: str) -> dict:
    """
    Use Claude API to extract structured entities from trial description.

    Input: Raw trial text (title + summary)
    Output: {drug, disease, sponsor, phase, mechanism}
    """
    try:
        client = anthropic.Anthropic()
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=256,
            messages=[{"role": "user", "content": _build_prompt(trial_text)}],
        )
        raw = message.content[0].text
        return _parse_response(raw)
    except Exception as e:
        print(f"[extract_entities] Claude API error: {e}")
        return dict(_NULL_RESULT)


if __name__ == "__main__":
    sample = "A Phase 2 Study of Pembrolizumab in Non-Small Cell Lung Cancer. This study evaluates the PD-1 inhibitor pembrolizumab for NSCLC. Sponsored by Merck."
    result = extract_with_claude(sample)
    print(result)
