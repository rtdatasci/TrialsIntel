"""
ChEMBL drug enrichment module.

Fetches drug data from the ChEMBL public REST API (https://www.ebi.ac.uk/chembl/)
and merges it into a trials DataFrame. For each unique drug name, the module
retrieves the ChEMBL identifier, development phase, molecule type, known
biological targets, and mechanisms of action.
"""

import requests
import pandas as pd


_CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"
_TIMEOUT = 15


def get_chembl_data(drug_name: str) -> dict | None:
    """
    Fetch drug data from the ChEMBL API for a single drug name.

    Returns a dict with keys:
        chembl_id, max_phase, molecule_type, targets, mechanisms
    Returns None if the drug cannot be found or any HTTP call fails.
    """
    # --- 1. Search for the molecule ---
    search_url = f"{_CHEMBL_BASE}/molecule/search?q={drug_name}&format=json"
    try:
        response = requests.get(search_url, timeout=_TIMEOUT)
        if response.status_code != 200:
            print(f"[chembl_enricher] Error: search returned HTTP {response.status_code} for '{drug_name}'")
            return None
        results = response.json()
    except Exception as e:
        print(f"[chembl_enricher] Error: search request failed for '{drug_name}': {e}")
        return None

    molecules = results.get("molecules", [])
    if not molecules:
        return None
    chembl_id = molecules[0].get("molecule_chembl_id")
    if not chembl_id:
        return None

    # --- 2. Fetch molecule detail ---
    detail_url = f"{_CHEMBL_BASE}/molecule/{chembl_id}?format=json"
    try:
        detail_resp = requests.get(detail_url, timeout=_TIMEOUT)
        detail = detail_resp.json()
    except Exception as e:
        print(f"[chembl_enricher] Error: detail request failed for '{chembl_id}': {e}")
        return None

    # --- 3. Fetch mechanism of action ---
    mech_url = f"{_CHEMBL_BASE}/mechanism?molecule_chembl_id={chembl_id}&format=json"
    try:
        mech_resp = requests.get(mech_url, timeout=_TIMEOUT)
        mechanisms_data = mech_resp.json()
    except Exception as e:
        print(f"[chembl_enricher] Error: mechanism request failed for '{chembl_id}': {e}")
        return None

    mechanism_list = mechanisms_data.get("mechanisms", [])

    # Filter out None/empty values from list fields
    targets = [
        m.get("target_chembl_id")
        for m in mechanism_list
        if m.get("target_chembl_id")
    ]
    mechanisms = [
        m.get("mechanism_of_action")
        for m in mechanism_list
        if m.get("mechanism_of_action")
    ]

    return {
        "chembl_id": chembl_id,
        "max_phase": detail.get("max_phase", "Unknown"),
        "molecule_type": detail.get("molecule_type", "Unknown"),
        "targets": targets,
        "mechanisms": mechanisms,
    }


def enrich_with_chembl(trials_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add ChEMBL data for each unique drug in trials_df.

    Merges chembl_id, max_phase, molecule_type, targets, and mechanisms
    columns into the DataFrame on the 'drug' column (left join).

    Returns the original trials_df unchanged if no ChEMBL data is retrieved.
    """
    chembl_data = []

    unique_drugs = trials_df["drug"].dropna().unique()
    for drug in unique_drugs:
        data = get_chembl_data(drug)
        if data:
            chembl_data.append({"drug": drug, **data})

    if not chembl_data:
        return trials_df

    chembl_df = pd.DataFrame(chembl_data)
    return trials_df.merge(chembl_df, on="drug", how="left")


if __name__ == "__main__":
    sample_df = pd.DataFrame({"drug": ["imatinib", "pembrolizumab", None]})
    enriched = enrich_with_chembl(sample_df)
    print(enriched[["drug", "chembl_id", "max_phase", "molecule_type"]].to_string(index=False))
