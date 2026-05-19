"""
Drug repurposing signal detection module.

Compares each drug's original ChEMBL-registered indication against the
diseases it is currently being tested for in the trials database.  A drug
is flagged as a repurposing candidate when it is observed in one or more
disease areas that differ from its primary registered indication.
"""

import requests
import pandas as pd

from src.chembl_enricher import get_chembl_data


_CHEMBL_BASE = "https://www.ebi.ac.uk/chembl/api/data"
_TIMEOUT = 15

# Column schema for an empty result
_RESULT_COLUMNS = [
    "drug",
    "original_indication",
    "new_indications",
    "new_indication_count",
    "signal_strength",
    "signal_label",
]


def get_original_indication(drug_name: str) -> str | None:
    """
    Return the primary registered indication for a drug via ChEMBL.

    Looks up the drug's ChEMBL ID with get_chembl_data(), then queries the
    drug_indication endpoint ordered by descending max phase to surface the
    most-developed indication first.

    Returns the MeSH heading if available, falling back to the EFO term.
    Returns None if the drug cannot be found or any network/parse error occurs.
    Never raises.
    """
    try:
        chembl_data = get_chembl_data(drug_name)
    except Exception as e:
        print(f"[repurposing] Error: get_chembl_data failed for '{drug_name}': {e}")
        return None

    if not chembl_data:
        return None

    chembl_id = chembl_data.get("chembl_id")
    if not chembl_id:
        return None

    indication_url = (
        f"{_CHEMBL_BASE}/drug_indication"
        f"?molecule_chembl_id={chembl_id}"
        f"&format=json"
        f"&order_by=-max_phase_for_ind"
    )

    try:
        response = requests.get(indication_url, timeout=_TIMEOUT)
        if response.status_code != 200:
            print(
                f"[repurposing] Error: drug_indication returned HTTP "
                f"{response.status_code} for '{drug_name}' ({chembl_id})"
            )
            return None
        payload = response.json()
    except Exception as e:
        print(
            f"[repurposing] Error: drug_indication request failed for "
            f"'{drug_name}' ({chembl_id}): {e}"
        )
        return None

    indications = payload.get("drug_indications", [])
    if not indications:
        return None

    top = indications[0]
    return top.get("mesh_heading") or top.get("efo_term") or None


def find_repurposing_candidates(trials_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify drugs in trials_df that are being tested in disease areas beyond
    their originally registered ChEMBL indication.

    Parameters
    ----------
    trials_df : pd.DataFrame
        Must contain at least 'drug' and 'disease' columns.

    Returns
    -------
    pd.DataFrame
        One row per repurposing candidate with columns:
            drug, original_indication, new_indications (comma-separated),
            new_indication_count, signal_strength, signal_label.
        Returns an empty DataFrame with those columns if no candidates are found.
    """
    candidates = []

    unique_drugs = trials_df["drug"].dropna().unique()

    for drug in unique_drugs:
        original_indication = get_original_indication(drug)

        tested_diseases = (
            trials_df[trials_df["drug"] == drug]["disease"]
            .dropna()
            .unique()
        )

        if original_indication is not None:
            new_indications = [
                d for d in tested_diseases
                if d.lower() != original_indication.lower()
            ]
        else:
            # No registered indication found — every observed disease is "new"
            new_indications = list(tested_diseases)

        new_indication_count = len(new_indications)
        if new_indication_count < 1:
            continue

        candidates.append(
            {
                "drug": drug,
                "original_indication": original_indication or "Unknown",
                "new_indications": ", ".join(new_indications),
                "new_indication_count": new_indication_count,
                "signal_strength": min(new_indication_count, 5),
            }
        )

    if not candidates:
        return pd.DataFrame(columns=_RESULT_COLUMNS)

    result_df = pd.DataFrame(candidates)

    def _label(strength: int) -> str:
        if strength >= 4:
            return "💡 Novel Repurposing"
        if strength == 3:
            return "🔀 Cross-Category"
        if strength == 2:
            return "🔄 Adjacent Use"
        return "➡️ Single New Use"

    result_df["signal_label"] = result_df["signal_strength"].apply(_label)

    return result_df[_RESULT_COLUMNS]


if __name__ == "__main__":
    sample_df = pd.DataFrame(
        {
            "drug": ["imatinib", "imatinib", "imatinib", "metformin", "metformin"],
            "disease": [
                "Chronic Myeloid Leukemia",
                "Gastrointestinal Stromal Tumor",
                "Breast Cancer",
                "Type 2 Diabetes",
                "Polycystic Ovary Syndrome",
            ],
        }
    )
    candidates = find_repurposing_candidates(sample_df)
    if candidates.empty:
        print("No repurposing candidates found.")
    else:
        print(candidates.to_string(index=False))
