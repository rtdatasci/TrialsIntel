import streamlit as st
import pandas as pd
from src.database import get_all_trials
from src.search import search_by_keywords

st.set_page_config(
    page_title="TrialsIntel",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 TrialsIntel")
st.markdown("*AI-powered clinical trial intelligence — powered by Claude + ClinicalTrials.gov*")

st.info(
    "⚠️ **Demo Mode** — This dashboard displays illustrative mock data to showcase the pipeline architecture. "
    "In production, data is fetched from the real ClinicalTrials.gov API and entities are extracted using the Claude API. "
    "Trial descriptions and entity labels are representative examples only.",
    icon="🔬",
)

# Load data
@st.cache_data
def load_data() -> pd.DataFrame:
    return get_all_trials()

df = load_data()

if df.empty:
    st.warning("No trials in database. Run `python run_pipeline.py` first.")
    st.stop()

# Sidebar filters
st.sidebar.header("Search & Filter")
disease_filter = st.sidebar.text_input("Disease / Condition", placeholder="e.g. Lung Cancer")
drug_filter = st.sidebar.text_input("Drug / Intervention", placeholder="e.g. Pembrolizumab")

phase_options = ["All"] + sorted(df["phase"].dropna().unique().tolist())
phase_filter = st.sidebar.selectbox("Trial Phase", phase_options)

# Apply filters
filtered = search_by_keywords(
    df,
    disease=disease_filter or None,
    drug=drug_filter or None,
    phase=None if phase_filter == "All" else phase_filter,
)

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
