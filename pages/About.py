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
st.markdown("---")
st.subheader("About the Developer")
st.write("""
**Ahmad Ilu** is a Nigerian Economist and Data Scientist with a passion for leveraging technology
to solve economic problems. He holds a Bachelor's degree in Economics from Northwest University Kano
and a Master's degree (Msc Economics) from Bayero University Kano.
I am passionate about linking economic research with real-world, machine learning applications, 
designing simulations, causal inference analysIs, and policy evaluations that improve decision-making.
I remain committed to expanding my knowledge of complex macroeconomic models, data-driven approaches,
and research tools to deliver accurate, impactful, and forward-looking analysis.
""")


st.markdown("""
            ### Connect with Me
<style>
.social-icons {
    display: flex;
    justify-content: left align-items: center;
    gap: 25px;
    padding-top: 20px;
}
.social-icons img {
    width: 32px;
    height: 32px;
}
</style>

<div class="social-icons">
    <a href="https://twitter.com/Iluahmad_" target="_blank">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/twitter/twitter-original.svg">
    </a>
    <a href="https://linkedin.com/in/ahmadilu" target="_blank">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/linkedin/linkedin-original.svg">
    </a>
    <a href="https://github.com/Iluahmad" target="_blank">
        <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg">
    </a>
    <a href="mailto:aii2400012.pec@buk.edu.ng" target="_blank">
        <img src="https://cdn-icons-png.flaticon.com/512/732/732200.png">
    </a>
</div>
""", unsafe_allow_html=True)
