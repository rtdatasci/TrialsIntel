"""
Mock enrichment data for TrialsIntel demo mode.

Provides pre-built DataFrames for ChEMBL, PubMed gap analysis, and
repurposing signals so the app renders fully without live API calls.
Data is illustrative only — not sourced from real API responses.
"""

import pandas as pd


# ---------------------------------------------------------------------------
# Mock ChEMBL enrichment — one row per drug
# ---------------------------------------------------------------------------

_MOCK_CHEMBL_ROWS = [
    {
        "drug": "Pembrolizumab",
        "chembl_id": "CHEMBL3301610",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["PDCD1"],
        "mechanisms": ["Programmed cell death protein 1 (PD-1) inhibitor"],
    },
    {
        "drug": "Nivolumab",
        "chembl_id": "CHEMBL3137343",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["PDCD1"],
        "mechanisms": ["PD-1 immune checkpoint inhibitor"],
    },
    {
        "drug": "Atezolizumab",
        "chembl_id": "CHEMBL3833335",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["CD274"],
        "mechanisms": ["PD-L1 immune checkpoint inhibitor"],
    },
    {
        "drug": "Venetoclax",
        "chembl_id": "CHEMBL3137660",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["BCL2"],
        "mechanisms": ["BCL-2 family apoptosis inhibitor antagonist"],
    },
    {
        "drug": "Olaparib",
        "chembl_id": "CHEMBL521686",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["PARP1", "PARP2"],
        "mechanisms": ["Poly ADP-ribose polymerase (PARP) inhibitor"],
    },
    {
        "drug": "Osimertinib",
        "chembl_id": "CHEMBL3353410",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["EGFR"],
        "mechanisms": ["Third-generation EGFR tyrosine kinase inhibitor"],
    },
    {
        "drug": "Ribociclib",
        "chembl_id": "CHEMBL3545110",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["CDK4", "CDK6"],
        "mechanisms": ["Cyclin-dependent kinase 4 and 6 inhibitor"],
    },
    {
        "drug": "Selpercatinib",
        "chembl_id": "CHEMBL4523582",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["RET"],
        "mechanisms": ["Selective RET kinase inhibitor"],
    },
    {
        "drug": "Daratumumab",
        "chembl_id": "CHEMBL1743076",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["CD38"],
        "mechanisms": ["Anti-CD38 monoclonal antibody"],
    },
    {
        "drug": "Tislelizumab",
        "chembl_id": "CHEMBL4297618",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["PDCD1"],
        "mechanisms": ["Anti-PD-1 monoclonal antibody"],
    },
    {
        "drug": "Dupilumab",
        "chembl_id": "CHEMBL3545338",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["IL4R"],
        "mechanisms": ["IL-4 receptor alpha subunit inhibitor (blocks IL-4 and IL-13 signalling)"],
    },
    {
        "drug": "Secukinumab",
        "chembl_id": "CHEMBL2018426",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["IL17A"],
        "mechanisms": ["Anti-IL-17A monoclonal antibody"],
    },
    {
        "drug": "Upadacitinib",
        "chembl_id": "CHEMBL4297459",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["JAK1"],
        "mechanisms": ["Selective JAK1 inhibitor"],
    },
    {
        "drug": "Guselkumab",
        "chembl_id": "CHEMBL3989899",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["IL23A"],
        "mechanisms": ["Anti-IL-23 monoclonal antibody (targets p19 subunit)"],
    },
    {
        "drug": "Vedolizumab",
        "chembl_id": "CHEMBL1742430",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["ITGA4", "ITGB7"],
        "mechanisms": ["Gut-selective anti-alpha4beta7 integrin antibody"],
    },
    {
        "drug": "Ozanimod",
        "chembl_id": "CHEMBL3989790",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["S1PR1", "S1PR5"],
        "mechanisms": ["Sphingosine 1-phosphate receptor 1 and 5 modulator"],
    },
    {
        "drug": "Belimumab",
        "chembl_id": "CHEMBL1201600",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["TNFSF13B"],
        "mechanisms": ["BLyS/BAFF inhibitor — reduces B-lymphocyte survival"],
    },
    {
        "drug": "Baricitinib",
        "chembl_id": "CHEMBL3137500",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["JAK1", "JAK2"],
        "mechanisms": ["JAK1 and JAK2 inhibitor"],
    },
    {
        "drug": "Ixekizumab",
        "chembl_id": "CHEMBL3545095",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["IL17A"],
        "mechanisms": ["Anti-IL-17A monoclonal antibody"],
    },
    {
        "drug": "Satralizumab",
        "chembl_id": "CHEMBL4297490",
        "max_phase": 4,
        "molecule_type": "Antibody",
        "targets": ["IL6R"],
        "mechanisms": ["IL-6 receptor recycling antibody (anti-IL-6R)"],
    },
    {
        "drug": "Erdafitinib",
        "chembl_id": "CHEMBL3940010",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["FGFR1", "FGFR2", "FGFR3", "FGFR4"],
        "mechanisms": ["Pan-FGFR kinase inhibitor"],
    },
    {
        "drug": "Capmatinib",
        "chembl_id": "CHEMBL3545029",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["MET"],
        "mechanisms": ["MET tyrosine kinase inhibitor"],
    },
    {
        "drug": "Pralsetinib",
        "chembl_id": "CHEMBL4297619",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["RET"],
        "mechanisms": ["Selective RET kinase inhibitor"],
    },
    {
        "drug": "Lurbinectedin",
        "chembl_id": "CHEMBL3545147",
        "max_phase": 3,
        "molecule_type": "Small molecule",
        "targets": ["POLR2A"],
        "mechanisms": ["RNA polymerase II inhibitor — induces DNA double-strand breaks in tumour cells"],
    },
    {
        "drug": "Niraparib",
        "chembl_id": "CHEMBL2180741",
        "max_phase": 4,
        "molecule_type": "Small molecule",
        "targets": ["PARP1", "PARP2"],
        "mechanisms": ["Poly ADP-ribose polymerase (PARP) 1 and 2 inhibitor"],
    },
]

_MOCK_CHEMBL_DF = pd.DataFrame(_MOCK_CHEMBL_ROWS)


def get_mock_chembl_enrichment(trials_df: pd.DataFrame) -> pd.DataFrame:
    """Merge pre-built ChEMBL mock data into trials_df."""
    return trials_df.merge(_MOCK_CHEMBL_DF, on="drug", how="left")


# ---------------------------------------------------------------------------
# Mock PubMed gap analysis — one row per disease
# ---------------------------------------------------------------------------

_MOCK_GAP_ROWS = [
    {"disease": "Non-Small Cell Lung Cancer", "trial_count": 4, "pubmed_count": 32400, "ratio": 8100.0},
    {"disease": "Metastatic Melanoma",        "trial_count": 1, "pubmed_count": 8200,  "ratio": 8200.0},
    {"disease": "Triple-Negative Breast Cancer", "trial_count": 1, "pubmed_count": 5100, "ratio": 5100.0},
    {"disease": "Acute Myeloid Leukemia",     "trial_count": 1, "pubmed_count": 7800,  "ratio": 7800.0},
    {"disease": "Ovarian Cancer",             "trial_count": 1, "pubmed_count": 9400,  "ratio": 9400.0},
    {"disease": "Breast Cancer",              "trial_count": 1, "pubmed_count": 41200, "ratio": 41200.0},
    {"disease": "RET Fusion-Positive Solid Tumors", "trial_count": 1, "pubmed_count": 680, "ratio": 680.0},
    {"disease": "Multiple Myeloma",           "trial_count": 1, "pubmed_count": 11600, "ratio": 11600.0},
    {"disease": "Hodgkin Lymphoma",           "trial_count": 1, "pubmed_count": 3900,  "ratio": 3900.0},
    {"disease": "Atopic Dermatitis",          "trial_count": 1, "pubmed_count": 6200,  "ratio": 6200.0},
    {"disease": "Ankylosing Spondylitis",     "trial_count": 1, "pubmed_count": 4100,  "ratio": 4100.0},
    {"disease": "Rheumatoid Arthritis",       "trial_count": 1, "pubmed_count": 22800, "ratio": 22800.0},
    {"disease": "Plaque Psoriasis",           "trial_count": 1, "pubmed_count": 5700,  "ratio": 5700.0},
    {"disease": "Crohn's Disease",            "trial_count": 1, "pubmed_count": 8900,  "ratio": 8900.0},
    {"disease": "Multiple Sclerosis",         "trial_count": 1, "pubmed_count": 19300, "ratio": 19300.0},
    {"disease": "Systemic Lupus Erythematosus", "trial_count": 1, "pubmed_count": 7400, "ratio": 7400.0},
    {"disease": "COVID-19",                   "trial_count": 1, "pubmed_count": 28600, "ratio": 28600.0},
    {"disease": "Psoriatic Arthritis",        "trial_count": 1, "pubmed_count": 3800,  "ratio": 3800.0},
    {"disease": "Neuromyelitis Optica Spectrum Disorder", "trial_count": 1, "pubmed_count": 1200, "ratio": 1200.0},
    {"disease": "Urothelial Carcinoma",       "trial_count": 1, "pubmed_count": 2900,  "ratio": 2900.0},
    {"disease": "Small Cell Lung Cancer",     "trial_count": 1, "pubmed_count": 6100,  "ratio": 6100.0},
    {"disease": "Prostate Cancer",            "trial_count": 1, "pubmed_count": 31500, "ratio": 31500.0},
]


def _assign_signal(ratio: float) -> str:
    if ratio > 20:
        return "🔥 High Opportunity"
    elif ratio < 3:
        return "⚠️ Limited Research"
    return "✅ Balanced"


def get_mock_gap_analysis() -> pd.DataFrame:
    """Return pre-built publication vs trial gap analysis."""
    df = pd.DataFrame(_MOCK_GAP_ROWS)
    df["signal"] = df["ratio"].apply(_assign_signal)
    return df[["disease", "trial_count", "pubmed_count", "ratio", "signal"]]


# ---------------------------------------------------------------------------
# Mock MeSH categories
# ---------------------------------------------------------------------------

MOCK_MESH_CATEGORIES = {
    "Neoplasms": 98,
    "Antineoplastic Agents": 87,
    "Immune System Diseases": 54,
    "Immunologic Factors": 51,
    "Protein Kinase Inhibitors": 44,
    "Carcinoma, Non-Small-Cell Lung": 38,
    "Antibodies, Monoclonal": 36,
    "Immunotherapy": 34,
    "Lymphoma": 28,
    "Autoimmune Diseases": 26,
    "Biological Products": 24,
    "Breast Neoplasms": 22,
    "Dermatitis, Atopic": 18,
    "Arthritis, Rheumatoid": 17,
    "Leukemia": 15,
}


# ---------------------------------------------------------------------------
# Mock repurposing signals
# ---------------------------------------------------------------------------

_MOCK_REPURPOSING_ROWS = [
    {
        "drug": "Baricitinib",
        "original_indication": "Rheumatoid Arthritis",
        "new_indications": "COVID-19",
        "new_indication_count": 1,
        "signal_strength": 1,
        "signal_label": "➡️ Single New Use",
    },
    {
        "drug": "Olaparib",
        "original_indication": "Ovarian Cancer",
        "new_indications": "Prostate Cancer",
        "new_indication_count": 1,
        "signal_strength": 1,
        "signal_label": "➡️ Single New Use",
    },
    {
        "drug": "Niraparib",
        "original_indication": "Ovarian Cancer",
        "new_indications": "Prostate Cancer",
        "new_indication_count": 1,
        "signal_strength": 1,
        "signal_label": "➡️ Single New Use",
    },
    {
        "drug": "Pembrolizumab",
        "original_indication": "Melanoma",
        "new_indications": "Non-Small Cell Lung Cancer",
        "new_indication_count": 1,
        "signal_strength": 1,
        "signal_label": "➡️ Single New Use",
    },
    {
        "drug": "Upadacitinib",
        "original_indication": "Rheumatoid Arthritis",
        "new_indications": "Atopic Dermatitis, Psoriatic Arthritis, Ankylosing Spondylitis",
        "new_indication_count": 3,
        "signal_strength": 3,
        "signal_label": "🔀 Cross-Category",
    },
    {
        "drug": "Secukinumab",
        "original_indication": "Plaque Psoriasis",
        "new_indications": "Ankylosing Spondylitis, Psoriatic Arthritis",
        "new_indication_count": 2,
        "signal_strength": 2,
        "signal_label": "🔄 Adjacent Use",
    },
    {
        "drug": "Ixekizumab",
        "original_indication": "Plaque Psoriasis",
        "new_indications": "Psoriatic Arthritis, Ankylosing Spondylitis",
        "new_indication_count": 2,
        "signal_strength": 2,
        "signal_label": "🔄 Adjacent Use",
    },
    {
        "drug": "Ozanimod",
        "original_indication": "Relapsing Multiple Sclerosis",
        "new_indications": "Crohn's Disease, Ulcerative Colitis",
        "new_indication_count": 2,
        "signal_strength": 2,
        "signal_label": "🔄 Adjacent Use",
    },
    {
        "drug": "Selpercatinib",
        "original_indication": "RET Fusion-Positive NSCLC",
        "new_indications": "Thyroid Cancer, Pancreatic Cancer, Colorectal Cancer, Salivary Gland Cancer",
        "new_indication_count": 4,
        "signal_strength": 4,
        "signal_label": "💡 Novel Repurposing",
    },
    {
        "drug": "Pralsetinib",
        "original_indication": "RET Fusion-Positive NSCLC",
        "new_indications": "Thyroid Cancer, Medullary Thyroid Cancer, Pancreatic Cancer, Colon Cancer",
        "new_indication_count": 4,
        "signal_strength": 4,
        "signal_label": "💡 Novel Repurposing",
    },
]


def get_mock_repurposing() -> pd.DataFrame:
    """Return pre-built repurposing signal candidates."""
    return pd.DataFrame(_MOCK_REPURPOSING_ROWS)
