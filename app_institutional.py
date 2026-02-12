import streamlit as st
from dashboard_institutional import main

# Set page config for institutional look
st.set_page_config(
    page_title="Crypto Analytics Pro - Institutional Trading Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Run institutional dashboard
main()
