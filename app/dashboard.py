from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent

st.title("Equity Research — Asia")

factors = pd.read_csv(ROOT / "data" / "factors.csv", index_col=0)

st.dataframe(factors)

st.bar_chart(
    factors["risk_adjusted_momentum"]
)