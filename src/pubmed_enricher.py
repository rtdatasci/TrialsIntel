"""
pubmed_enricher.py
Fetches publication data from PubMed via Biopython's Entrez interface
and computes gap analysis metrics for TrialsIntel.
"""

import pandas as pd
from Bio import Entrez

Entrez.email = "trialsintel@demo.example"


def search_pubmed_by_disease(disease, max_results=100):
    """Search PubMed for papers about a disease (last 5 years).

    Parameters
    ----------
    disease : str
        Disease name to search for.
    max_results : int
        Maximum number of results (used for retmax, though rettype=count
        makes this informational only).

    Returns
    -------
    int
        Count of matching PubMed articles, or 0 on any error.
    """
    handle = None
    try:
        term = f"{disease}[MeSH Terms] OR {disease}[Title/Abstract]"
        handle = Entrez.esearch(
            db="pubmed",
            term=term,
            rettype="count",
            datetype="pdat",
            reldate=1826,
        )
        results = Entrez.read(handle)
        return int(results["Count"])
    except Exception as exc:
        print(f"[pubmed_enricher] Warning: could not fetch PubMed count for '{disease}': {exc}")
        return 0
    finally:
        if handle is not None:
            handle.close()


def get_mesh_terms(pmid):
    """Extract MeSH descriptor names from a PubMed article.

    Parameters
    ----------
    pmid : str or int
        PubMed article identifier.

    Returns
    -------
    list of str
        MeSH descriptor name strings, or [] on any error.
    """
    handle = None
    try:
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="xml", retmode="xml")
        records = Entrez.read(handle)
        terms = []
        for article in records.get("PubmedArticle", []):
            medline = article.get("MedlineCitation", {})
            mesh_list = medline.get("MeshHeadingList", [])
            for heading in mesh_list:
                descriptor = heading.get("DescriptorName", None)
                if descriptor is not None:
                    terms.append(str(descriptor))
        return terms
    except Exception as exc:
        print(f"[pubmed_enricher] Warning: could not fetch MeSH terms for PMID {pmid}: {exc}")
        return []
    finally:
        if handle is not None:
            handle.close()


def get_mesh_categories(trials_df):
    """Categorize trials by MeSH terms across all unique diseases.

    Parameters
    ----------
    trials_df : pd.DataFrame
        DataFrame containing a 'disease' column.

    Returns
    -------
    dict
        Mapping of MeSH term -> occurrence count.
    """
    mesh_categories = {}
    unique_diseases = trials_df["disease"].dropna().unique()

    for disease in unique_diseases:
        handle = None
        try:
            handle = Entrez.esearch(
                db="pubmed",
                term=f"{disease}[MeSH Terms]",
                retmax=10,
            )
            pmids = Entrez.read(handle)["IdList"]
        except Exception as exc:
            print(f"[pubmed_enricher] Warning: MeSH esearch failed for '{disease}': {exc}")
            pmids = []
        finally:
            if handle is not None:
                handle.close()

        for pmid in pmids[:5]:
            terms = get_mesh_terms(pmid)
            for term in terms:
                mesh_categories[term] = mesh_categories.get(term, 0) + 1

    return mesh_categories


def enrich_with_pubmed(trials_df):
    """Add publication counts and pub/trial ratio for each disease.

    Parameters
    ----------
    trials_df : pd.DataFrame
        DataFrame containing a 'disease' column.

    Returns
    -------
    pd.DataFrame
        Copy of trials_df with additional columns:
        - pubmed_count : int, number of PubMed articles for the disease
        - pub_trial_ratio : float, pubmed_count divided by trial count per disease
    """
    df = trials_df.copy()

    df["pubmed_count"] = df["disease"].apply(
        lambda x: search_pubmed_by_disease(x) if pd.notna(x) else 0
    )

    trial_counts = df.groupby("disease")["disease"].transform("count")
    df["pub_trial_ratio"] = df["pubmed_count"] / trial_counts

    return df


def compute_gap_analysis(trials_df):
    """Compute a gap analysis between published research and clinical trials.

    Groups trials by disease, fetches PubMed counts, calculates a
    publication-to-trial ratio, and assigns an opportunity signal.

    Parameters
    ----------
    trials_df : pd.DataFrame
        DataFrame containing a 'disease' column.

    Returns
    -------
    pd.DataFrame
        Columns: disease, trial_count, pubmed_count, ratio, signal
    """
    disease_counts = (
        trials_df.dropna(subset=["disease"])
        .groupby("disease")
        .size()
        .reset_index(name="trial_count")
    )

    pubmed_counts = []
    for disease in disease_counts["disease"]:
        count = search_pubmed_by_disease(disease)
        pubmed_counts.append(count)

    disease_counts["pubmed_count"] = pubmed_counts
    disease_counts["ratio"] = disease_counts.apply(
        lambda row: row["pubmed_count"] / max(row["trial_count"], 1),
        axis=1,
    )

    def _signal(ratio):
        if ratio > 20:
            return "🔥 High Opportunity"
        elif ratio < 3:
            return "⚠️ Limited Research"
        else:
            return "✅ Balanced"

    disease_counts["signal"] = disease_counts["ratio"].apply(_signal)

    return disease_counts[["disease", "trial_count", "pubmed_count", "ratio", "signal"]]
