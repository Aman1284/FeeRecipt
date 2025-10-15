

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas
from datetime import datetime
import io
import math
from num2words import num2words

# -----------------------------------------------------
# Utility: Convert number to words
# -----------------------------------------------------
def number_to_words(n):
    """Convert numeric value to Indian English words."""
    return num2words(n, lang='en_IN').replace(',', '').title()

# -----------------------------------------------------
# PDF Generator
# -----------------------------------------------------
def create_fee_certificate(
    letterhead_option, student_name, gender, parent_name, class_name,
    address, monthly_fee, financial_year, date, ref_number
):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Select letterhead
    if letterhead_option == "Just Kids":
        letterhead_path = "assets/justkids.png"
    else:
        letterhead_path = "assets/jkpublic.png"

    # Draw letterhead background
    try:
        letterhead = ImageReader(letterhead_path)
        c.drawImage(letterhead, 0, 0, width=width, height=height, mask="auto")
    except Exception as e:
        st.warning(f"Letterhead missing: {e}")

    # Margins and layout
    left_margin = 80
    right_margin = width - 80
    text_width = right_margin - left_margin
    start_y = height - 260  # starting height after letterhead

    # ---------------- Ref & Date ----------------
    c.setFont("Times-Roman", 12)
    c.drawString(left_margin, start_y, f"Ref.{ref_number}")
    c.drawRightString(right_margin, start_y, f"Dated: {date}")

    # ---------------- Heading ----------------
    c.setFont("Times-Bold", 14)
    c.drawCentredString(width / 2, start_y - 40, "TO WHOM IT MAY CONCERN")

    # ---------------- Gender Logic ----------------
    if gender == "Male":
        prefix = "Master"
        relation = "S/O"
        pronoun = "His"
    else:
        prefix = "Miss"
        relation = "D/O"
        pronoun = "Her"

    # ---------------- Fee Calculations ----------------
    monthly_fee = float(monthly_fee)
    total_fee = monthly_fee * 12
    total_in_words = number_to_words(math.floor(total_fee))

    # ---------------- Body Text ----------------
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontName="Times-Roman",
        fontSize=12,
        leading=18,
        alignment=4,  # Justified
        textColor=colors.black,
    )

    body_text = (
        f"This is to certify that {prefix} {student_name}, {relation} {parent_name}, "
        f"Class {class_name}, residing at {address}. "
        f"{pronoun} Tuition fee is Rs {int(monthly_fee)}/- per month, "
        f"making a total of Rs {int(total_fee)}/- "
        f"({total_in_words} Only) for the Financial Year {financial_year}."
    )

    paragraph = Paragraph(body_text, style=body_style)
    para_width, para_height = paragraph.wrap(text_width, 500)
    y_body_bottom = start_y - 90 - para_height
    paragraph.drawOn(c, left_margin, y_body_bottom)

    # ---------------- Signature Block ----------------
    sig_y = y_body_bottom - 90
    name_y = sig_y - 15

    try:
        signature = ImageReader("assets/Dimple Agarwal.png")
        c.drawImage(signature, right_margin - 150, sig_y, width=130, height=50, mask="auto")
    except Exception as e:
        st.warning(f"Signature missing: {e}")

    # Line under signature
    c.setLineWidth(0.5)
    c.line(right_margin - 200, name_y, right_margin, name_y)

    # Name and Designation
    c.setFont("Times-Bold", 12)
    c.drawRightString(right_margin, name_y - 15, "Principal")
    c.setFont("Times-Roman", 11)
    c.drawRightString(right_margin, name_y - 30, "Just Kids Play School")

    # Save PDF
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# -----------------------------------------------------
# Streamlit UI
# -----------------------------------------------------
st.set_page_config(page_title="Fee Certificate Generator", page_icon="🏫")
st.title("🏫 Fee Certificate PDF Generator")

st.write("Generate 'To Whom It May Concern' fee certificates in official school format.")

# Inputs
letterhead_option = st.radio("Choose Letterhead:", ["Just Kids", "JK Public"], horizontal=True)
student_name = st.text_input("Student Name", "UNNATI CHOUDHARY")
gender = st.radio("Gender", ["Female", "Male"], horizontal=True)
parent_name = st.text_input("Parent Name", "UDAY KUMAR CHOUDHARY")
class_name = st.text_input("Class", "LKG")
address = st.text_area("Address", "SHAHDEO NAGAR, NEAR RAM JANKI MANDIR, RANCHI DIST-RANCHI, JHARKHAND")
monthly_fee = st.number_input("Tuition Fee per Month (Rs)", min_value=0.0, value=1500.0)

financial_years = [
    "2023-24", "2024-25", "2025-26", "2026-27",
    "2027-28", "2028-29", "2029-30"
]
financial_year = st.selectbox("Financial Year", financial_years, index=1)
date = st.text_input("Date", datetime.now().strftime("%d/%m/%Y"))

# ---------------- Reference Number Input ----------------
default_ref_prefix = f"{financial_year}/"
ref_suffix = st.text_input("Reference Number (enter the trailing part)", "33")
ref_number = f"{financial_year}/{ref_suffix}"

# -----------------------------------------------------
# Generate PDF
# -----------------------------------------------------
if st.button("Generate Fee Certificate PDF"):
    pdf_buffer = create_fee_certificate(
        letterhead_option, student_name, gender, parent_name, class_name,
        address, monthly_fee, financial_year, date, ref_number
    )

    st.download_button(
        label="📥 Download Fee Certificate",
        data=pdf_buffer,
        file_name=f"{student_name.replace(' ', '_')}_Fee_Certificate_{financial_year}.pdf",
        mime="application/pdf",
    )
