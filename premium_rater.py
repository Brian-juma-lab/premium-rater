# ==========================================================
# Platinum Life Premium Calculator (Liberty Life Style)
# Author: Brian Juma
# ==========================================================

import streamlit as st
import pandas as pd
from PIL import Image
import os

# --- APP CONFIG ---
st.set_page_config(page_title="Platinum Life Premium Calculator", layout="wide")

# --- DETERMINE FILE PATHS ---
# Use relative paths to work both locally and on Streamlit Cloud
base_path = os.path.dirname(__file__)
data_path = os.path.join(base_path, "Per Mille rates data_v1.xlsx")
logo_path = os.path.join(base_path, "Company logo.png")

# --- LOAD DATA ---
try:
    df = pd.read_excel(data_path)
except FileNotFoundError:
    st.error("❌ Could not find 'Per Mille rates data_v1.xlsx'. Please ensure it's in the same folder as this script.")
    st.stop()

# --- HEADER SECTION WITH LOGO TOP RIGHT ---
col1, col2 = st.columns([4, 1])
with col1:
    st.markdown(
        """
        <h1 style='color:#003366;'>Platinum Life Premium Calculator</h1>
        <hr style='border: 2px solid #FFD700; border-radius: 10px;'>
        """,
        unsafe_allow_html=True
    )
with col2:
    try:
        logo = Image.open(logo_path)
        st.image(logo, width='stretch')
    except FileNotFoundError:
        st.warning("⚠️ Company logo not found. Please ensure 'Company logo.png' is in the same folder.")

# --- CLIENT DETAILS FORM ---
st.subheader("🧾 Client Details")

client_name = st.text_input("Client Name")
age = st.number_input("Age (18–55)", min_value=18, max_value=55, step=1)
gender = st.selectbox("Gender", ["Male", "Female"])
smoker = st.selectbox("Smoker Status", ["Smoker", "Non Smoker"])
education = st.selectbox("Education Level", ["Tertiary", "Non Tertiary"])
sum_assured = st.number_input(
    "Sum Assured (1,000,000 – 35,000,000)",
    min_value=1_000_000,
    max_value=35_000_000,
    step=100_000
)

# --- CALCULATE BUTTON ---
if st.button("💰 Calculate Premium"):

    try:
        rate_row = df[df['Age'] == age]

        if gender == "Male" and smoker == "Smoker" and education == "Tertiary":
            per_mille_rate = rate_row["Male Smoker Tertiary"].values[0]
        elif gender == "Male" and smoker == "Smoker" and education == "Non Tertiary":
            per_mille_rate = rate_row["Male Smoker Non Tertiary"].values[0]
        elif gender == "Male" and smoker == "Non Smoker" and education == "Tertiary":
            per_mille_rate = rate_row["Male Non Smoker Tertiary"].values[0]
        elif gender == "Male" and smoker == "Non Smoker" and education == "Non Tertiary":
            per_mille_rate = rate_row["Male Non Smoker Non Tertiary"].values[0]
        elif gender == "Female" and smoker == "Smoker" and education == "Tertiary":
            per_mille_rate = rate_row["Female Smoker Tertiary"].values[0]
        elif gender == "Female" and smoker == "Smoker" and education == "Non Tertiary":
            per_mille_rate = rate_row["Female Smoker Non Tertiary"].values[0]
        elif gender == "Female" and smoker == "Non Smoker" and education == "Tertiary":
            per_mille_rate = rate_row["Female Non Smoker Tertiary"].values[0]
        else:
            per_mille_rate = rate_row["Female Non Smoker Non Tertiary"].values[0]

        # --- CALCULATIONS ---
        base_premium = (per_mille_rate / 1000) * sum_assured
        phcf = 0.0025 * base_premium  # 0.25%
        stamp_duty = 40  # Fixed
        total_premium = base_premium + phcf + stamp_duty

        # --- OUTPUT SECTION ---
        st.markdown("<hr style='border: 1px solid #FFD700;'>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style='background-color:#F2F4F8; padding:15px; border-radius:10px;'>
            <h3 style='color:#003366;'>Premium Illustration</h3>
            <p><b>Client Name:</b> {client_name}</p>
            <p><b>Age:</b> {age}</p>
            <p><b>Gender:</b> {gender}</p>
            <p><b>Smoker:</b> {smoker}</p>
            <p><b>Education:</b> {education}</p>
            <p><b>Sum Assured:</b> Kshs {sum_assured:,.0f}</p>
            <hr>
            <p><b>Base Premium:</b> Kshs {base_premium:,.2f}</p>
            <p><b>PHCF (0.25%):</b> Kshs {phcf:,.2f}</p>
            <p><b>Stamp Duty (Fixed):</b> Kshs {stamp_duty:,.2f}</p>
            <p style='color:#003366; font-size:20px;'>
                <b>Total Monthly Premium Payable:</b> Kshs {total_premium:,.2f}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # --- TAX RELIEF + DISCLAIMER ---
        st.markdown("""
        <hr style='border: 1px solid #FFD700;'>
        <h4 style='color:#003366;'>Tax Relief</h4>
        <p>Enjoy up to <b>Kshs 60,000 per year</b> in tax relief.</p>

        <h4 style='color:#003366;'>Disclaimer</h4>
        <p style='font-size:14px;'>
        Liberty Life has taken all reasonable steps towards ensuring that the information represented herein is true,
        current and accurate. The illustrative values represented here are based on stated assumptions and are indicative rates only.
        The figures may vary depending on factors such as the age and gender of the client. Accordingly, Liberty Life cannot be held
        liable for any damages arising from any transactions or omissions and the resultant actions arising from the information
        contained in these illustrative values.
        </p>
        """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ An error occurred while calculating: {e}")
