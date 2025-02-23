import streamlit as st
import io
import re
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os
import qrcode
from PIL import Image


def create_pdf(
    content: str,
    subject: str,
    signature_paths: dict,
    custom_logo=None,
    watermark_text="Verified Legal Document",
) -> bytes:
    try:
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        header_height = 120
        if custom_logo:
            logo = ImageReader(custom_logo)
        else:
            logo_path = "indian_govt_logo.png"
            if os.path.exists(logo_path):
                logo = ImageReader(logo_path)
            else:
                logo = None

        if logo:
            c.drawImage(
                logo,
                width / 2 - 50,
                height - header_height,
                width=100,
                height=100,
                mask="auto",
            )
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, height - header_height - 15, "Made By Tech 99")

        c.setLineWidth(1.5)
        c.line(40, height - header_height - 25, width - 40, height - header_height - 25)

        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width / 2, height - header_height - 50, subject)
        c.setLineWidth(1)
        c.line(50, height - header_height - 60, width - 50, height - header_height - 60)

        c.saveState()
        c.setFont("Helvetica", 60)
        c.setFillColorRGB(0.9, 0.9, 0.9, alpha=0.3)
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, watermark_text)
        c.restoreState()

        c.setFont("Helvetica", 12)
        y = height - header_height - 80
        margin = 50
        lines = []
        max_chars_per_line = 90
        for paragraph in content.split("\n"):
            if paragraph.strip() == "":
                lines.append("")
            else:
                while len(paragraph) > max_chars_per_line:
                    lines.append(paragraph[:max_chars_per_line])
                    paragraph = paragraph[max_chars_per_line:]
                lines.append(paragraph)
                lines.append("")
        for line in lines:
            c.drawString(margin, y, line)
            y -= 15
            if y < 200:
                c.showPage()

                if logo:
                    c.drawImage(
                        logo,
                        width / 2 - 50,
                        height - header_height,
                        width=100,
                        height=100,
                        mask="auto",
                    )
                c.setFont("Helvetica-Bold", 14)
                c.drawCentredString(
                    width / 2, height - header_height - 15, "Made By Tech 99"
                )
                c.setLineWidth(1.5)
                c.line(
                    40,
                    height - header_height - 25,
                    width - 40,
                    height - header_height - 25,
                )
                y = height - header_height - 80
                c.setFont("Helvetica", 12)

        c.setFont("Helvetica-Oblique", 10)
        c.drawCentredString(width / 2, 40, "© Made By Tech 99 | Official Document")

        qr_data = "https://your-verification-page.com/verify?docid=12345"
        qr_img = qrcode.make(qr_data)
        qr_buffer = io.BytesIO()
        qr_img.save(qr_buffer, format="PNG")
        qr_buffer.seek(0)
        qr_reader = ImageReader(qr_buffer)
        c.drawImage(qr_reader, width - 150, 20, width=100, height=100, mask="auto")
        c.setFont("Helvetica", 8)
        c.drawCentredString(width - 100, 15, "Scan to Verify")

        sig_y = 150
        sig_box_width = 120
        sig_box_height = 60
        gap = 50
        total_width = 3 * sig_box_width + 2 * gap
        start_x = (width - total_width) / 2

        sig_labels = ["Signature 1", "Signature 2", "Signature 3"]
        sig_keys = ["Party 1", "Party 2", "Guarantor"]

        for idx, label in enumerate(sig_labels):
            sig_x = start_x + idx * (sig_box_width + gap)
            c.rect(sig_x, sig_y, sig_box_width, sig_box_height, stroke=1, fill=0)
            key = sig_keys[idx]
            if key in signature_paths and signature_paths[key]:
                sig_bytes = signature_paths[key].read()
                sig = ImageReader(io.BytesIO(sig_bytes))
                c.drawImage(
                    sig,
                    sig_x,
                    sig_y,
                    width=sig_box_width,
                    height=sig_box_height,
                    mask="auto",
                )
            c.setFont("Helvetica", 10)
            c.drawCentredString(sig_x + sig_box_width / 2, sig_y - 15, label)

        c.save()
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
        return b""


st.set_page_config(page_title="Legal Document Generator", page_icon="📜", layout="wide")

st.markdown(
    """
    <style>
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    .fadeIn {
        animation: fadeIn 1.5s ease-in-out;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.title("📜 Legal Document Generator")
    st.markdown(
        """
    Welcome to the **Legal Document Generator**! 
    This tool helps you create professional legal documents in PDF format.
    """
    )
    st.markdown("---")
    st.markdown("### Steps:")
    st.markdown("1. Select the type of document.")
    st.markdown("2. Fill in the required details.")
    st.markdown("3. Upload signatures (if required).")
    st.markdown("4. Generate and download your document.")
    st.markdown("---")
    st.markdown("Made with ❤️ by **Tech 99**")
if "form_data" not in st.session_state:
    st.session_state.form_data = {}

doc_types = [
    "Last Will and Testament",
    "Employment Contract",
    "Non-Disclosure Agreement (NDA)",
    "Lease Agreement",
    "Marriage Agreement",
]
doc_type = st.selectbox("Select the type of legal document:", doc_types)

custom_logo_file = st.file_uploader(
    "Upload a custom logo (Optional)", type=["png", "jpg", "jpeg"], key="custom_logo"
)


def validate_date(input_date):
    return bool(re.match(r"\d{4}-\d{2}-\d{2}$", input_date))


def validate_number(input_text):
    return input_text.isdigit()


def save_input(key, value):
    st.session_state.form_data[key] = value
    return value


def get_text_input(label, key, optional=False):
    value = st.text_input(label, st.session_state.form_data.get(key, ""), key=key)
    if value:
        save_input(key, value)
    if not value and not optional:
        st.warning(f"⚠ {label} is required.")
        return None
    return value


prompt = ""
valid_input = True
current_date = datetime.date.today()
subject = f"Subject: {doc_type}"

progress_bar = st.progress(0)

if doc_type == "Last Will and Testament":
    st.subheader("📜 Last Will and Testament Details")

    col1, col2 = st.columns(2)
    with col1:
        testator = get_text_input("Enter the name of the testator:", "testator")
        executor = get_text_input("Enter the name of the executor:", "executor")
    with col2:
        beneficiary = get_text_input(
            "Enter the name of the beneficiary:", "beneficiary"
        )
        will_date = get_text_input(
            "Enter the date of the will (YYYY-MM-DD):", "will_date"
        )
        if will_date and not validate_date(will_date):
            st.error("❌ Invalid date format! Please enter in YYYY-MM-DD format.")
            valid_input = False

    st.markdown("---")
    st.markdown("### Upload Signatures")
    signature_testator = st.file_uploader(
        "Upload Signature of Testator", type=["png", "jpg", "jpeg"], key="sig_testator"
    )
    signature_executor = st.file_uploader(
        "Upload Signature of Executor", type=["png", "jpg", "jpeg"], key="sig_executor"
    )

    signature_paths = {"Party 1": signature_testator, "Party 2": signature_executor}

    if st.button("📝 Generate Last Will and Testament"):
        if not all([testator, executor, beneficiary, will_date]):
            st.error("❌ All fields are required!")
            valid_input = False
        else:
            prompt = f"""
LAST WILL AND TESTAMENT

This Last Will and Testament is made on {current_date}.

BY

Testator: {testator}
Executor: {executor}
Beneficiary: {beneficiary}

Will Date: {will_date}
"""

elif doc_type == "Employment Contract":
    st.subheader("💼 Employment Contract Details")

    col1, col2 = st.columns(2)
    with col1:
        employer = get_text_input("Enter the employer's name:", "employer")
        employee = get_text_input("Enter the employee's name:", "employee")
    with col2:
        start_date = get_text_input("Enter the start date (YYYY-MM-DD):", "start_date")
        if start_date and not validate_date(start_date):
            st.error("❌ Invalid date format! Please enter in YYYY-MM-DD format.")
            valid_input = False

    position = get_text_input("Enter the job position:", "position")
    salary = get_text_input("Enter the salary (numeric value):", "salary")

    if salary and not validate_number(salary):
        st.error("❌ Salary must be a numeric value!")
        valid_input = False

    st.markdown("---")
    st.markdown("### Upload Signatures")
    signature_employer = st.file_uploader(
        "Upload Signature of Employer", type=["png", "jpg", "jpeg"], key="sig_employer"
    )
    signature_employee = st.file_uploader(
        "Upload Signature of Employee", type=["png", "jpg", "jpeg"], key="sig_employee"
    )

    signature_paths = {"Party 1": signature_employer, "Party 2": signature_employee}

    if st.button("📝 Generate Employment Contract"):
        if not all([employer, employee, start_date, position, salary]):
            st.error("❌ All fields are required!")
            valid_input = False
        else:
            prompt = f"""
EMPLOYMENT CONTRACT

This Employment Contract is made on {current_date}.

BETWEEN

1. Employer: {employer}
2. Employee: {employee}

Start Date: {start_date}
Position: {position}
Salary: {salary}
"""

elif doc_type == "Non-Disclosure Agreement (NDA)":
    st.subheader("🔒 Non-Disclosure Agreement (NDA) Details")

    col1, col2 = st.columns(2)
    with col1:
        disclosing_party = get_text_input(
            "Enter the name of the disclosing party:", "disclosing_party"
        )
        receiving_party = get_text_input(
            "Enter the name of the receiving party:", "receiving_party"
        )
    with col2:
        nda_start_date = get_text_input(
            "Enter the start date of the NDA (YYYY-MM-DD):", "nda_start_date"
        )
        if nda_start_date and not validate_date(nda_start_date):
            st.error("❌ Invalid date format! Please enter in YYYY-MM-DD format.")
            valid_input = False

    confidentiality_period = get_text_input(
        "Enter the confidentiality period (in months):", "confidentiality_period"
    )
    if confidentiality_period and not validate_number(confidentiality_period):
        st.error("❌ Confidentiality period must be a numeric value!")
        valid_input = False

    st.markdown("---")
    st.markdown("### Upload Signatures")
    signature_disclosing = st.file_uploader(
        "Upload Signature of Disclosing Party",
        type=["png", "jpg", "jpeg"],
        key="sig_disclosing",
    )
    signature_receiving = st.file_uploader(
        "Upload Signature of Receiving Party",
        type=["png", "jpg", "jpeg"],
        key="sig_receiving",
    )

    signature_paths = {"Party 1": signature_disclosing, "Party 2": signature_receiving}

    if st.button("📝 Generate Non-Disclosure Agreement (NDA)"):
        if not all(
            [disclosing_party, receiving_party, nda_start_date, confidentiality_period]
        ):
            st.error("❌ All fields are required!")
            valid_input = False
        else:
            prompt = f"""
NON-DISCLOSURE AGREEMENT (NDA)

This Non-Disclosure Agreement is made on {current_date}.

BETWEEN

1. Disclosing Party: {disclosing_party}
2. Receiving Party: {receiving_party}

Start Date: {nda_start_date}
Confidentiality Period: {confidentiality_period} months
"""

elif doc_type == "Lease Agreement":
    st.subheader("🏠 Lease Agreement Details")

    col1, col2 = st.columns(2)
    with col1:
        landlord = get_text_input("Enter the name of the landlord:", "landlord")
        tenant = get_text_input("Enter the name of the tenant:", "tenant")
    with col2:
        lease_start_date = get_text_input(
            "Enter the start date of the lease (YYYY-MM-DD):", "lease_start_date"
        )
        if lease_start_date and not validate_date(lease_start_date):
            st.error("❌ Invalid date format! Please enter in YYYY-MM-DD format.")
            valid_input = False

    lease_end_date = get_text_input(
        "Enter the end date of the lease (YYYY-MM-DD):", "lease_end_date"
    )
    if lease_end_date and not validate_date(lease_end_date):
        st.error("❌ Invalid date format! Please enter in YYYY-MM-DD format.")
        valid_input = False

    rent_amount = get_text_input(
        "Enter the monthly rent amount (numeric value):", "rent_amount"
    )
    if rent_amount and not validate_number(rent_amount):
        st.error("❌ Rent amount must be a numeric value!")
        valid_input = False

    st.markdown("---")
    st.markdown("### Upload Signatures")
    signature_landlord = st.file_uploader(
        "Upload Signature of Landlord", type=["png", "jpg", "jpeg"], key="sig_landlord"
    )
    signature_tenant = st.file_uploader(
        "Upload Signature of Tenant", type=["png", "jpg", "jpeg"], key="sig_tenant"
    )

    signature_paths = {"Party 1": signature_landlord, "Party 2": signature_tenant}

    if st.button("📝 Generate Lease Agreement"):
        if not all([landlord, tenant, lease_start_date, lease_end_date, rent_amount]):
            st.error("❌ All fields are required!")
            valid_input = False
        else:
            prompt = f"""
LEASE AGREEMENT

This Lease Agreement is made on {current_date}.

BETWEEN

1. Landlord: {landlord}
2. Tenant: {tenant}

Lease Start Date: {lease_start_date}
Lease End Date: {lease_end_date}
Monthly Rent: {rent_amount}
"""

elif doc_type == "Marriage Agreement":
    st.subheader("💍 Marriage Agreement Details")

    col1, col2 = st.columns(2)
    with col1:
        party1 = get_text_input("Enter the full name of the first party:", "party1")
        father1 = get_text_input("Enter the father name of the first party:", "father1")
        mother1 = get_text_input("Enter the mother name of the first party:", "mother1")
    with col2:
        party2 = get_text_input("Enter the full name of the second party:", "party2")
        father2 = get_text_input(
            "Enter the father name of the second party:", "father2"
        )
        mother2 = get_text_input(
            "Enter the mother name of the second party:", "mother2"
        )

    place_of_marriage = get_text_input(
        "Enter the place of marriage:", "place_of_marriage"
    )
    marriage_date = get_text_input(
        "Enter the marriage date (YYYY-MM-DD):", "marriage_date"
    )
    if marriage_date and not validate_date(marriage_date):
        st.error("❌ Invalid date format! Please enter in YYYY-MM-DD format.")
        valid_input = False

    st.markdown("---")
    st.markdown("### Upload Signatures")
    signature_party1 = st.file_uploader(
        "Upload Signature of Party 1", type=["png", "jpg", "jpeg"], key="sig_party1"
    )
    signature_party2 = st.file_uploader(
        "Upload Signature of Party 2", type=["png", "jpg", "jpeg"], key="sig_party2"
    )
    signature_guarantor = st.file_uploader(
        "Upload Signature of Guarantor",
        type=["png", "jpg", "jpeg"],
        key="sig_guarantor",
    )

    signature_paths = {
        "Party 1": signature_party1,
        "Party 2": signature_party2,
        "Guarantor": signature_guarantor,
    }

    if st.button("📝 Generate Marriage Agreement"):
        if not all(
            [
                party1,
                party2,
                marriage_date,
                place_of_marriage,
                father1,
                mother1,
                father2,
                mother2,
            ]
        ):
            st.error("❌ All fields are required!")
            valid_input = False
        else:
            prompt = f"""
MARRIAGE AGREEMENT

This Marriage Agreement is made on {current_date}.

BETWEEN

1. {party1}, son/daughter of {father1} and {mother1}.
2. {party2}, son/daughter of {father2} and {mother2}.

Marriage Date: {marriage_date}
Location: {place_of_marriage}
"""

file_name = st.text_input(
    "Enter the desired PDF file name (e.g., my_document.pdf):", "legal_document.pdf"
)

if prompt:
    st.subheader("🔍 Live Preview of Your Document")
    st.text_area("Document Content Preview:", value=prompt, height=300)

if prompt and valid_input:
    with st.spinner("⏳ Generating document..."):
        custom_logo = None
        if custom_logo_file:
            custom_logo = io.BytesIO(custom_logo_file.read())
        pdf_bytes = create_pdf(
            prompt, subject, signature_paths, custom_logo=custom_logo
        )
    st.success("✅ Document Generated!")
    st.download_button(
        "📥 Download PDF", data=pdf_bytes, file_name=file_name, mime="application/pdf"
    )
