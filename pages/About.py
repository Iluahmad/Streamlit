import streamlit as st

st.set_page_config(page_title="About", page_icon="ℹ️", layout="wide")

st.title("About the Nigeria Fiscal-Monetary Policy Simulator")

st.write("""
This simulator is built as a compact policy laboratory for Nigeria, blending fiscal, monetary, 
and structural channels into an integrated five-year projection engine.

It allows policymakers, analysts, students and researchers to test assumptions, 
apply shocks, and explore alternative futures without touching the real economy.
""")

st.markdown("---")

st.subheader("Download Technical Note")

with open("Nigerian_simulator.pdf", "rb") as f:
    pdf_bytes = f.read()

st.download_button(
    label="📄 Download Full Technical Note (PDF)",
    data=pdf_bytes,
    file_name="Nigerian_simulator.pdf",
    mime="application/pdf"
)

