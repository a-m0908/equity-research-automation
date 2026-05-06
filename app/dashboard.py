import streamlit as st
import pandas as pd

st.title("Equity Research Automation")

factors = pd.read_csv(
    "data/factors.csv",
    index_col=0
)

st.dataframe(factors)

st.bar_chart(
    factors["risk_adjusted_momentum"]
)