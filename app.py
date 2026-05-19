import os
import streamlit as st
import pandas as pd
import altair as alt
from src.database import get_all_trials
from src.search import search_by_keywords
from src.chembl_enricher import enrich_with_chembl
from src.pubmed_enricher import compute_gap_analysis, get_mesh_categories
from src.repurposing import find_repurposing_candidates
from src.mock_enrichment import (
    get_mock_chembl_enrichment,
    get_mock_gap_analysis,
    get_mock_repurposing,
    MOCK_MESH_CATEGORIES,
)

# Set to "1" to call live PubMed/ChEMBL APIs instead of using mock data.
_LIVE_MODE = os.environ.get("TRIALSINTEL_LIVE", "0") == "1"

st.set_page_config(
    page_title="TrialsIntel",
    page_icon="🧬",
    layout="wide",
)

st.title("🔬 TrialsIntel Pro")
st.markdown("*Multi-source clinical trial intelligence — ClinicalTrials.gov + PubMed + ChEMBL*")

st.info(
    "⚠️ **Demo Mode** — All four tabs use illustrative mock data to showcase the pipeline architecture. "
    "In production, trials are fetched from ClinicalTrials.gov, entities extracted via Claude API, "
    "and enrichment data pulled live from PubMed and ChEMBL. "
    "Set the `TRIALSINTEL_LIVE=1` environment variable to enable live API calls.",
    icon="🔬",
)

# ---------------------------------------------------------------------------
# Load base data
# ---------------------------------------------------------------------------

@st.cache_data
def load_data() -> pd.DataFrame:
    return get_all_trials()

df = load_data()

if df.empty:
    st.warning("No trials in database. Run `python run_pipeline.py` first.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar filters (global, drive Tab 1 display)
# ---------------------------------------------------------------------------

st.sidebar.header("Search & Filter")
disease_filter = st.sidebar.text_input("Disease / Condition", placeholder="e.g. Lung Cancer")
drug_filter = st.sidebar.text_input("Drug / Intervention", placeholder="e.g. Pembrolizumab")

phase_options = ["All"] + sorted(df["phase"].dropna().unique().tolist())
phase_filter = st.sidebar.selectbox("Trial Phase", phase_options)

filtered = search_by_keywords(
    df,
    disease=disease_filter or None,
    drug=drug_filter or None,
    phase=None if phase_filter == "All" else phase_filter,
)

# ---------------------------------------------------------------------------
# Cached enrichment helpers
# ---------------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def cached_gap_analysis(trials_df: pd.DataFrame) -> pd.DataFrame:
    if not _LIVE_MODE:
        return get_mock_gap_analysis()
    result = compute_gap_analysis(trials_df)
    return result if not result.empty else get_mock_gap_analysis()


@st.cache_data(show_spinner=False)
def cached_mesh_categories(trials_df: pd.DataFrame) -> dict:
    if not _LIVE_MODE:
        return MOCK_MESH_CATEGORIES
    result = get_mesh_categories(trials_df)
    return result if result else MOCK_MESH_CATEGORIES


@st.cache_data(show_spinner=False)
def cached_chembl_enrichment(trials_df: pd.DataFrame) -> pd.DataFrame:
    if not _LIVE_MODE:
        return get_mock_chembl_enrichment(trials_df)
    result = enrich_with_chembl(trials_df)
    return result if "chembl_id" in result.columns else get_mock_chembl_enrichment(trials_df)


@st.cache_data(show_spinner=False)
def cached_repurposing(trials_df: pd.DataFrame) -> pd.DataFrame:
    if not _LIVE_MODE:
        return get_mock_repurposing()
    result = find_repurposing_candidates(trials_df)
    return result if not result.empty else get_mock_repurposing()


# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Trials Database",
    "📚 Research Intelligence",
    "💊 Drug Intelligence",
    "🔄 Repurposing Signals",
])

# ===========================================================================
# Tab 1 — Trials Database
# ===========================================================================

with tab1:
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Trials", len(filtered))
    col2.metric("Unique Diseases", filtered["disease"].dropna().nunique())
    col3.metric("Unique Drugs", filtered["drug"].dropna().nunique())
    col4.metric("Unique Sponsors", filtered["sponsor"].dropna().nunique())

    st.divider()

    # Bar chart: trials by phase
    st.subheader("Trials by Phase")
    phase_counts = filtered["phase"].value_counts().reset_index()
    phase_counts.columns = ["Phase", "Count"]
    st.bar_chart(phase_counts.set_index("Phase"))

    st.divider()

    # Data table
    st.subheader(f"Trials ({len(filtered)} results)")
    display_cols = ["nct_id", "title", "drug", "disease", "phase", "sponsor", "mechanism"]
    available_cols = [c for c in display_cols if c in filtered.columns]
    st.dataframe(
        filtered[available_cols],
        use_container_width=True,
        height=400,
    )

# ===========================================================================
# Tab 2 — Research Intelligence
# ===========================================================================

with tab2:
    st.subheader("📚 Publication vs Trial Activity")

    with st.spinner("Fetching publication data from PubMed..."):
        gap_df = cached_gap_analysis(df)

    if gap_df.empty:
        st.info("No gap analysis data available.")
    else:
        st.dataframe(
            gap_df.sort_values("ratio", ascending=False),
            use_container_width=True,
        )

        chart = (
            alt.Chart(gap_df)
            .mark_circle(size=80)
            .encode(
                x=alt.X("trial_count:Q", title="Clinical Trials"),
                y=alt.Y("pubmed_count:Q", title="PubMed Publications"),
                color=alt.Color("signal:N", title="Signal"),
                tooltip=["disease", "trial_count", "pubmed_count", "ratio", "signal"],
            )
            .properties(title="Research vs Clinical Activity", width=700, height=400)
        )
        st.altair_chart(chart, use_container_width=True)

    with st.expander("🏷️ MeSH Category Breakdown"):
        mesh_dict = cached_mesh_categories(df)
        if mesh_dict:
            mesh_df = (
                pd.DataFrame(
                    list(mesh_dict.items()), columns=["MeSH Category", "Count"]
                )
                .sort_values("Count", ascending=False)
                .head(15)
            )
            st.bar_chart(mesh_df.set_index("MeSH Category"))
        else:
            st.info("MeSH data unavailable — PubMed API not reachable in this environment.")

# ===========================================================================
# Tab 3 — Drug Intelligence
# ===========================================================================

with tab3:
    st.subheader("💊 ChEMBL Drug Intelligence")

    with st.spinner("Fetching drug data from ChEMBL..."):
        enriched_df = cached_chembl_enrichment(df)

    selected_drug = st.selectbox(
        "Select Drug",
        sorted(df["drug"].dropna().unique()),
    )

    drug_row = (
        enriched_df[enriched_df["drug"] == selected_drug].iloc[0]
        if not enriched_df[enriched_df["drug"] == selected_drug].empty
        else None
    )

    drug_trials = enriched_df[enriched_df["drug"] == selected_drug]

    if drug_row is not None and "chembl_id" in enriched_df.columns and pd.notna(drug_row.get("chembl_id")):
        chembl_id = drug_row.get("chembl_id", "N/A")
        max_phase = drug_row.get("max_phase", "N/A")
        targets = drug_row.get("targets") or []
        mechanisms = drug_row.get("mechanisms") or []

        col1, col2, col3 = st.columns(3)
        col1.metric("ChEMBL ID", chembl_id)
        col2.metric("Max Phase", max_phase)
        col3.metric("Targets", len(targets))

        st.write("**Mechanisms:**")
        if mechanisms:
            for mech in mechanisms:
                st.write(f"- {mech}")
        else:
            st.info("No mechanism data available.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("ChEMBL ID", "N/A")
        col2.metric("Max Phase", "N/A")
        col3.metric("Targets", 0)

    st.write("**Trials Testing This Drug:**")
    trial_cols = [c for c in ["nct_id", "disease", "phase", "sponsor"] if c in drug_trials.columns]
    st.dataframe(drug_trials[trial_cols], use_container_width=True)

# ===========================================================================
# Tab 4 — Repurposing Signals
# ===========================================================================

with tab4:
    st.subheader("🔄 Drug Repurposing Intelligence")

    with st.spinner("Identifying repurposing candidates..."):
        repurposing_df = cached_repurposing(df)

    if repurposing_df.empty:
        st.info("No repurposing signals found. Run the pipeline with a real API key to populate data.")
    else:
        min_signal = st.slider("Minimum Signal Strength", min_value=1, max_value=5, value=1)

        filtered_repurposing = repurposing_df[repurposing_df["signal_strength"] >= min_signal]

        show_cols = [
            c for c in [
                "drug", "original_indication", "new_indications",
                "new_indication_count", "signal_strength", "signal_label",
            ]
            if c in filtered_repurposing.columns
        ]
        st.dataframe(filtered_repurposing[show_cols], use_container_width=True)

        # Signal strength distribution bar chart
        strength_counts = (
            filtered_repurposing["signal_strength"]
            .value_counts()
            .sort_index()
            .rename_axis("Signal Strength")
            .rename("Count")
        )
        st.bar_chart(strength_counts)

        # Highlight high-signal candidates
        high_signal = filtered_repurposing[filtered_repurposing["signal_strength"] >= 4]
        for _, row in high_signal.iterrows():
            st.success(
                f"💡 {row['drug']}: {row['new_indication_count']} new indication(s) — "
                f"{row['new_indications']} [{row['signal_label']}]"
            )
