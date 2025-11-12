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
**Ahmad Ilu** is a Nigerian Economist and data scientist with a passion for leveraging technology
to solve economic problems. He holds a Bachelor's degree in Economics from Northwest University Kano
and a Master's degree (Msc Economics) from Bayero University Kano.
I am passionate about linking economic research with real-world, machine learning applications, 
designing simulations, causal analyses, and policy evaluations that improve decision-making.
I remain committed to expanding my knowledge of complex macroeconomic models, data-driven approaches,
and research tools to deliver accurate, impactful, and forward-looking analysis.
""")

st.markdown("""
<br>

### Connect with Me

<div style='display: flex; gap: 15px; align-items: center;'>

<!-- Twitter -->
<a href='https://twitter.com/Iluahmad_' target='_blank'>
<img src='https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/x.svg' width='28'/>
</a>

<!-- LinkedIn -->
<a href='http://linkedin.com/in/ahmadilu' target='_blank'>
<img src='https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/linkedin.svg' width='28'/>
</a>

<!-- GitHub -->
<a href='https://github.com/Iluahmad' target='_blank'>
<img src='https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/github.svg' width='28'/>
</a>

<!-- Gmail -->
<a href='mailto:aii2400012.pec@buk.edu.ng' target='_blank'>
<img src='https://cdn.jsdelivr.net/gh/simple-icons/simple-icons/icons/gmail.svg' width='28'/>
</a>

</div>

""", unsafe_allow_html=True)

