import pandas as pd
from typing import Optional


def search_by_keywords(
    df: pd.DataFrame,
    disease: Optional[str] = None,
    drug: Optional[str] = None,
    phase: Optional[str] = None,
) -> pd.DataFrame:
    """
    Simple keyword filtering on a trials DataFrame.
    Matches are case-insensitive substrings.
    Returns a filtered DataFrame (may be empty).
    """
    mask = pd.Series([True] * len(df), index=df.index)

    if disease:
        d = disease.lower()
        disease_mask = (
            df["disease"].fillna("").str.lower().str.contains(d, regex=False) |
            df["conditions"].fillna("").str.lower().str.contains(d, regex=False)
        )
        mask &= disease_mask

    if drug:
        dr = drug.lower()
        drug_mask = (
            df["drug"].fillna("").str.lower().str.contains(dr, regex=False) |
            df["interventions"].fillna("").str.lower().str.contains(dr, regex=False)
        )
        mask &= drug_mask

    if phase:
        p = phase.lower()
        phase_mask = df["phase"].fillna("").str.lower().str.contains(p, regex=False)
        mask &= phase_mask

    return df[mask].reset_index(drop=True)
