import streamlit as st
from dashboard_streamlit import main

# Set page config for Streamlit dark theme
st.set_page_config(
    page_title="Crypto Analytics Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Run Streamlit-native dashboard
main()
