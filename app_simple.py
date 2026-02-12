import streamlit as st
from dashboard_simple import main

# Set page config
st.set_page_config(
    page_title="Crypto Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Run simple beautiful dashboard
main()
