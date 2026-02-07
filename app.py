import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Crypto Volatility & Risk Analyzer",
    layout="centered"
)

# Title
st.title("📈 Crypto Volatility and Risk Analyzer")

# Description
st.write("Analyze cryptocurrency volatility and identify risk level easily.")

# Input fields
crypto_name = st.text_input("Enter Cryptocurrency Name (e.g., Bitcoin)")
price_change = st.number_input(
    "Enter Daily Price Change (%)",
    min_value=0.0,
    step=0.1
)

# Button
if st.button("Analyze Risk"):
    if price_change > 10:
        risk = "🔴 High Risk"
    elif price_change > 5:
        risk = "🟠 Medium Risk"
    else:
        risk = "🟢 Low Risk"

    st.success(f"{crypto_name} Risk Level: {risk}")
