import requests


BASE_URL = "https://clinicaltrials.gov/api/v2/studies"


def _parse_study(study: dict) -> dict:
    """Extract flat fields from a raw ClinicalTrials.gov study dict."""
    proto = study.get("protocolSection", {})

    ident = proto.get("identificationModule", {})
    nct_id = ident.get("nctId", "")
    title = ident.get("briefTitle", "")

    desc = proto.get("descriptionModule", {})
    summary = desc.get("briefSummary", "")

    cond_module = proto.get("conditionsModule", {})
    conditions = ", ".join(cond_module.get("conditions", []))

    arms = proto.get("armsInterventionsModule", {})
    interventions_list = arms.get("interventions", [])
    interventions = ", ".join(i.get("name", "") for i in interventions_list)

    sponsor_module = proto.get("sponsorCollaboratorsModule", {})
    lead = sponsor_module.get("leadSponsor", {})
    sponsor = lead.get("name", "")

    design = proto.get("designModule", {})
    phases = design.get("phases", [])
    phase = phases[0] if phases else ""

    return {
        "nct_id": nct_id,
        "title": title,
        "summary": summary,
        "conditions": conditions,
        "interventions": interventions,
        "sponsor": sponsor,
        "phase": phase,
    }


def fetch_trials_from_api(query: str = "cancer", max_results: int = 50) -> list[dict]:
    """
    Fetch trials from ClinicalTrials.gov API v2.
    Returns list of dicts with: nct_id, title, summary, conditions,
    interventions, sponsor, phase.
    """
    trials = []
    params = {
        "query.cond": query,
        "pageSize": min(max_results, 100),
        "format": "json",
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        studies = data.get("studies", [])
        for study in studies[:max_results]:
            trials.append(_parse_study(study))
    except Exception as e:
        print(f"[fetch_trials] Error fetching trials: {e}")
    return trials


if __name__ == "__main__":
    import json
    results = fetch_trials_from_api(query="cancer", max_results=50)
    print(f"Fetched {len(results)} trials")
    if results:
        print(json.dumps(results[0], indent=2))
