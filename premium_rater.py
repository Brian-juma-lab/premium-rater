# ==========================================================
# Platinum Life Premium Autorator 
# Author: Brian Juma
# ==========================================================

import streamlit as st
import pandas as pd
from PIL import Image
import os
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
import base64

# --- APP CONFIG ---
st.set_page_config(page_title="Platinum Life Premium Autorater", layout="wide")

# --- FILE PATHS ---
base_path = os.path.dirname(__file__)
data_path = os.path.join(base_path, "Per Mille rates data_v1.xlsx")
logo_path = os.path.join(base_path, "Company logo.png")

# --- LOAD DATA ---
try:
    df = pd.read_excel(data_path)
except FileNotFoundError:
    st.error("❌ Could not find 'Per Mille rates data_v1.xlsx'. Please ensure it's in the same folder as this script.")
    st.stop()

# --- LOAD LOGO ---
def load_logo_base64(path):
    try:
        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        st.warning("⚠️ Company logo not found. Please ensure 'Company logo.png' is in the same folder.")
        return None

logo_base64 = load_logo_base64(logo_path)

# --- PAGE STYLE ---
st.markdown("""
<style>
    .block-container {padding-top: 0rem !important;}
    .main-container {display: flex; flex-direction: column; align-items: center; justify-content: flex-start;}
    .quote-card {background-color: #ffffff; width: 15cm; padding: 25px 25px; border-radius: 20px; box-shadow: 0 0 15px rgba(0, 0, 50, 0.1); margin-top: 15px;}
    .quote-title {color: #003366; font-weight: 900; font-size: 3vw; margin-top: 15px; margin-bottom: 0; text-align: center; letter-spacing: 0.5px;}
    .header-logo {width: 25vw; max-width: 180px; height: auto; margin-bottom: 1vh;}
    .section-header {color: #003366; font-weight: 800; font-size: 20px; text-align: center; margin-bottom: 20px;}
    label, .stTextInput label, .stSelectbox label, .stNumberInput label {color: #003366 !important; font-weight: 600 !important;}
    div.stButton > button:first-child {background-color: #003366; color: white; font-weight: bold; border: none; border-radius: 8px; padding: 12px 0; transition: all 0.3s ease;}
    div.stButton > button:first-child:hover {transform: scale(1.03); background-color: #00224f;}
    .gold-line {border-top: 2px solid #d4af37; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if "page" not in st.session_state:
    st.session_state.page = "form"

# --- PREMIUM CALCULATION FUNCTION ---
def calculate_premium(age, gender, smoker, education, sum_assured):
    rate_row = df[df['Age'] == age]
    if rate_row.empty:
        st.error("⚠️ No matching rate found for this age.")
        return 0, 0, 0, 0

    if gender == "Male" and smoker == "Smoker" and education == "Tertiary":
        rate = rate_row["Male Smoker Tertiary"].values[0]
    elif gender == "Male" and smoker == "Smoker" and education == "Non Tertiary":
        rate = rate_row["Male Smoker Non Tertiary"].values[0]
    elif gender == "Male" and smoker == "Non Smoker" and education == "Tertiary":
        rate = rate_row["Male Non Smoker Tertiary"].values[0]
    elif gender == "Male" and smoker == "Non Smoker" and education == "Non Tertiary":
        rate = rate_row["Male Non Smoker Non Tertiary"].values[0]
    elif gender == "Female" and smoker == "Smoker" and education == "Tertiary":
        rate = rate_row["Female Smoker Tertiary"].values[0]
    elif gender == "Female" and smoker == "Smoker" and education == "Non Tertiary":
        rate = rate_row["Female Smoker Non Tertiary"].values[0]
    elif gender == "Female" and smoker == "Non Smoker" and education == "Tertiary":
        rate = rate_row["Female Non Smoker Tertiary"].values[0]
    else:
        rate = rate_row["Female Non Smoker Non Tertiary"].values[0]

    base = (rate / 1000) * sum_assured
    phcf = 0.0025 * base
    stamp = 40
    total = base + phcf + stamp
    return base, phcf, stamp, total

# --- PDF GENERATION FUNCTION ---
def generate_pdf():
    """Generates a simple PDF quotation using ReportLab based on session data."""
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # --- Header Logo (Top Right) ---
    logo_path_local = os.path.join(base_path, "Company logo.png")
    if os.path.exists(logo_path_local):
        logo_width = 100
        logo_height = 60
        c.drawImage(logo_path_local, width - logo_width - 50, height - logo_height - 40,
                    width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')

    # --- Header Title ---
    c.setFillColorRGB(0, 0, 0.6)  # Dark Blue
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 80, "PLATINUM LIFE QUOTATION")

    # --- Draw Line ---
    c.setStrokeColorRGB(0, 0, 0.6)
    c.setLineWidth(1)
    c.line(50, height - 90, width - 50, height - 90)

    # --- Retrieve Values ---
    client_name = st.session_state.get("client_name", "")
    age = st.session_state.get("age", 0)
    gender = st.session_state.get("gender", "")
    smoker = st.session_state.get("smoker", "")
    education = st.session_state.get("education", "")
    sum_assured = st.session_state.get("sum_assured", 0)
    base = st.session_state.get("base", 0.0)
    phcf = st.session_state.get("phcf", 0.0)
    stamp = st.session_state.get("stamp", 40.0)
    total = st.session_state.get("total", 0.0)
    presenter_name = st.session_state.get("presenter_name_display", "")
    distribution_channel = st.session_state.get("distribution_channel_display", "")
    presenter_code = st.session_state.get("presenter_code_display", "")

    # --- Client Details ---
    y = height - 140
    c.setFillColorRGB(0, 0, 0.6)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Client Details:")
    y -= 20
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(70, y, f"Client Name: {client_name}")
    y -= 15
    c.drawString(70, y, f"Age: {age}")
    y -= 15
    c.drawString(70, y, f"Gender: {gender}")
    y -= 15
    c.drawString(70, y, f"Smoker: {smoker}")
    y -= 15
    c.drawString(70, y, f"Education Level: {education}")
    y -= 15
    c.drawString(70, y, f"Sum Assured: KShs {sum_assured:,.2f}")

    # --- Premium Breakdown ---
    y -= 40
    c.setFillColorRGB(0, 0, 0.6)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Premium Breakdown:")
    y -= 20
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(70, y, f"Base Premium: KShs {base:,.2f}")
    y -= 15
    c.drawString(70, y, f"PHCF Levy: KShs {phcf:,.2f}")
    y -= 15
    c.drawString(70, y, f"Stamp Duty: KShs {stamp:,.2f}")

    # --- Total Monthly Premium ---
    y -= 30
    c.setFillColorRGB(0, 0, 0.6)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Total Monthly Premium:")
    y -= 20
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(70, y, f"KShs {total:,.2f}")

    # --- Presenter Details ---
    y -= 50
    c.setFillColorRGB(0, 0, 0.6)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Presenter Details:")
    y -= 20
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(70, y, f"Presenter Name: {presenter_name}")
    y -= 15
    c.drawString(70, y, f"Distribution Channel: {distribution_channel}")
    y -= 15
    c.drawString(70, y, f"Presenter Code: {presenter_code}")

    # --- Tax Relief Section ---
    y -= 40
    c.setFillColorRGB(0, 0, 0.6)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Tax Relief:")
    y -= 20
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 12)
    c.drawString(70, y, "Enjoy up to Kshs 60,000 per year in tax relief.")

    # --- Disclaimer Section ---
    y -= 60
    c.setFillColorRGB(0, 0, 0.6)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Disclaimer:")
    y -= 20
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    text = (
        "Liberty Life has taken all reasonable steps towards ensuring that the information represented herein is true, "
        "current and accurate. The illustrative values represented here are based on stated assumptions and are indicative "
        "rates only. The figures may vary dependent on factors such as the age and gender of client. Accordingly, Liberty "
        "Life cannot be held liable for any damages arising from any transactions or omissions and the resultant actions "
        "arising from the information contained in the illustrative values."
    )
    text_obj = c.beginText(70, y - 15)
    text_obj.textLines(text)
    c.drawText(text_obj)

    # --- Save PDF ---
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --- PAGE 1: CLIENT FORM ---
if st.session_state.page == "form":
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    if logo_base64:
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/png;base64,{logo_base64}' class='header-logo'/></div>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<h2 class='quote-title' style='color:#003366; text-align:center;'>PLATINUM LIFE PREMIUM AUTORATER</h2>",
        unsafe_allow_html=True
    )
    st.markdown("<div class='quote-card'>", unsafe_allow_html=True)
    st.markdown(
        "<h3 class='section-header' style='color:#003366; text-align:center;'>CLIENT DETAILS</h3>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([2, 1], gap="large")

    # --- LEFT COLUMN: CLIENT DETAILS ---
    with col1:
        client_name = st.text_input("Client Name", placeholder="Enter client's full name")
        age = st.number_input("Age (Last Birthday)", min_value=18, max_value=55, step=1, value=30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        smoker = st.selectbox("Smoker Status", ["Smoker", "Non Smoker"])
        education = st.selectbox("Education Level", ["Tertiary", "Non Tertiary"])
        sum_assured = st.number_input(
            "Sum Assured (1,000,000 – 35,000,000)",
            min_value=1_000_000,
            max_value=35_000_000,
            step=500_000,
            value=1_000_000
        )

    # --- RIGHT COLUMN: PRESENTER DETAILS ---
    with col2:
        st.markdown("<div style='margin-top:60px;'>", unsafe_allow_html=True)
        presenter_name_display = st.text_input("Presenter Name", key="presenter_name_display")
        distribution_channel_display = st.text_input("Distribution Channel", key="distribution_channel_display")
        presenter_code_display = st.text_input("Presenter Code", key="presenter_code_display")

        st.markdown("<div style='margin-top:40px; text-align:center;'>", unsafe_allow_html=True)
        calculate_btn = st.button("Generate Quotation", use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)

    # --- SAVE ALL INPUTS TO SESSION STATE & NAVIGATE TO PAGE 2 ---
    if calculate_btn:
        base, phcf, stamp, total = calculate_premium(age, gender, smoker, education, sum_assured)

        # Store all client and presenter details in session state
        st.session_state.update({
            "client_name": client_name,
            "age": age,
            "gender": gender,
            "smoker": smoker,
            "education": education,
            "sum_assured": sum_assured,
            "base": base,
            "phcf": phcf,
            "stamp": stamp,
            "total": total,
            "page": "quotation"
        })

        st.rerun()

# --- PAGE 2: QUOTATION ---
elif st.session_state.page == "quotation":
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)

    # --- HEADER SECTION ---
    if logo_base64:
        st.markdown(
            f"<div style='text-align:center;'><img src='data:image/png;base64,{logo_base64}' class='header-logo'/></div>",
            unsafe_allow_html=True
        )

    st.markdown(
        "<h2 class='quote-title' style='color:#003366; text-align:center;'>PLATINUM LIFE QUOTATION</h2>",
        unsafe_allow_html=True
    )

    form_col, right_col = st.columns([2, 1])

    # --- LEFT COLUMN: QUOTATION DETAILS ---
    with form_col:
        st.markdown(
            """
            <div style='border: 2px solid #003366; border-radius: 10px; padding: 20px; margin-right: 30px; background-color: #f9f9f9;'>
                <h3 style='color:#003366; text-align:center; margin-top:0;'>QUOTATION DETAILS</h3>
            """,
            unsafe_allow_html=True
        )

        # Retrieve client details
        client_name = st.session_state.get("client_name", "")
        age = st.session_state.get("age", 0)
        gender = st.session_state.get("gender", "")
        smoker = st.session_state.get("smoker", "")
        education = st.session_state.get("education", "")
        sum_assured = st.session_state.get("sum_assured", 0)
        base = st.session_state.get("base", 0.0)
        phcf = st.session_state.get("phcf", 0.0)

        # --- STYLING FOR INFO BOXES ---
        st.markdown(
            """
            <style>
            .info-box {
                background-color: #f9f9f9;
                padding: 12px 16px;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
                box-shadow: 0px 1px 3px rgba(0,0,0,0.1);
                margin-bottom: 10px;
            }
            .info-label {
                color: #004080;
                font-weight: 600;
                font-size: 15px;
                margin-bottom: 2px;
            }
            .info-value {
                font-size: 14px;
                color: #333333;
                margin-top: 0;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

        # --- DISPLAY DETAILS IN 3 COLUMNS ---
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(
                f"""
                <div class='info-box'><div class='info-label'>Client Name</div><div class='info-value'>{client_name}</div></div>
                <div class='info-box'><div class='info-label'>Age (Last Birthday)</div><div class='info-value'>{age}</div></div>
                <div class='info-box'><div class='info-label'>Gender</div><div class='info-value'>{gender}</div></div>
                """,
                unsafe_allow_html=True
            )

        with col2:
            st.markdown(
                f"""
                <div class='info-box'><div class='info-label'>Smoker Status</div><div class='info-value'>{smoker}</div></div>
                <div class='info-box'><div class='info-label'>Education Level</div><div class='info-value'>{education}</div></div>
                <div class='info-box'><div class='info-label'>Sum Assured (KShs)</div><div class='info-value'>{sum_assured:,.0f}</div></div>
                """,
                unsafe_allow_html=True
            )

        with col3:
            st.markdown(
                f"""
                <div class='info-box'><div class='info-label'>Base Premium (KShs)</div><div class='info-value'>{base:,.2f}</div></div>
                <div class='info-box'><div class='info-label'>PHCF (0.25%) (KShs)</div><div class='info-value'>{phcf:,.2f}</div></div>
                <div class='info-box'><div class='info-label'>Stamp Duty (KShs)</div><div class='info-value'>{40.00:,.2f}</div></div>
                """,
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # --- TAX RELIEF SECTION ---
        st.markdown(
            """
            <div style='
                border:1px solid #cccccc;
                border-radius:8px;
                padding:10px 15px;
                margin-top:20px;
                font-size:13px;
                font-style:italic;
                background-color:#fdfdfd;
                color:Darkblue;
                text-align:left;
            '>
                <p><b>Tax Relief:</b> Enjoy up to <b>KShs 60,000</b> per year in tax relief on your life insurance premiums!</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- DISCLAIMER SECTION ---
        st.markdown(
            """
            <div style='
                border:1px solid #cccccc;
                border-radius:8px;
                padding:10px 15px;
                margin-top:20px;
                font-size:13px;
                font-style:italic;
                background-color:#fdfdfd;
                color:Darkblue;
            '>
                <p><b>Disclaimer:</b> Liberty Life has taken all reasonable steps towards ensuring that the information represented herein is true,
                current and accurate. The illustrative values represented here are based on stated assumptions and are indicative rates only.
                The figures may vary depending on factors such as the age and gender of the client. Accordingly, Liberty Life cannot be held liable
                for any damages arising from any transactions or omissions and the resultant actions arising from the information contained in these
                illustrative values. by Liberty Life Assurance Kenya Ltd.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --- RIGHT COLUMN: TOTAL + PRESENTER + BUTTONS ---
    with right_col:
        # --- TOTAL PREMIUM BOX ---
        st.markdown(
            f"""
            <div style='
                border:2px solid #003366;
                border-radius:10px;
                padding:20px;
                background-color:#f9f9f9;
                text-align:center;
            '>
                <h3 style='color:#003366; margin-bottom:10px;'>Total Monthly Premium:</h3>
                <h2 style='color:black; font-weight:bold; margin-top:0;'>KShs {st.session_state.get('total', 0):,.2f}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- PRESENTER DETAILS DISPLAY ---
        presenter_name = st.session_state.get("presenter_name_display", "")
        distribution_channel = st.session_state.get("distribution_channel_display", "")
        presenter_code = st.session_state.get("presenter_code_display", "")

        st.markdown(
            f"""
            <div style='
                border:1px solid #cccccc;
                border-radius:8px;
                padding:10px 15px;
                margin-top:10px;
                font-size:13px;
                background-color:#fdfdfd;
                color:Darkblue;
                text-align:left;
            '>
                <p><b>Presenter Details:</b><br>
                <b>Name:</b> {presenter_name if presenter_name else '__________________'}<br>
                <b>Distribution Channel:</b> {distribution_channel if distribution_channel else '__________________'}<br>
                <b>Code:</b> {presenter_code if presenter_code else '__________________'}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # --- ACTION BUTTONS ---
        if st.button(" Go Back", use_container_width=True):
            st.session_state.page = "form"
            st.rerun()

        if st.button("⬇️ Download Quotation (PDF)", use_container_width=True):
        # Ensure presenter details are saved before PDF generation
           st.session_state["presenter_name_display"] = st.session_state.get("presenter_name_display", presenter_name)
           st.session_state["distribution_channel_display"] = st.session_state.get("distribution_channel_display", distribution_channel)
           st.session_state["presenter_code_display"] = st.session_state.get("presenter_code_display", presenter_code)

           pdf_bytes = generate_pdf()

           st.download_button(
               label="Click here to download PDF",
               data=pdf_bytes,
               file_name="Platinum_Life_Quotation.pdf",
               mime="application/pdf",
               use_container_width=True
        )
