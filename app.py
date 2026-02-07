import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Crypto Volatility & Risk Analyzer",
    layout="centered"
)

# Title
st.title("📈 Crypto Volatility & Risk Analyzer")
st.subheader("Understand crypto risk using daily price volatility")

st.markdown("---")

# Input section
col1, col2 = st.columns(2)

with col1:
    crypto_name = st.text_input(
        "🪙 Cryptocurrency Name",
        placeholder="e.g., Bitcoin"
    )

with col2:
    price_change = st.number_input(
        "📊 Daily Price Change (%)",
        min_value=0.0,
        step=0.1
    )

st.markdown("---")

# Button
if st.button("🔍 Analyze Risk"):
    if crypto_name.strip() == "":
        st.warning("⚠️ Please enter a cryptocurrency name.")
    else:
        if price_change > 10:
            risk = "🔴 High Risk"
            explanation = "High volatility detected. Prices can change rapidly, leading to higher potential losses."
        elif price_change > 5:
            risk = "🟠 Medium Risk"
            explanation = "Moderate volatility. Suitable for balanced risk-takers."
        else:
            risk = "🟢 Low Risk"
            explanation = "Low volatility. Generally more stable for cautious investors."

        st.success(f"**{crypto_name} — Risk Level: {risk}**")
        st.info(explanation)

