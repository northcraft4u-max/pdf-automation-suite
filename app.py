import io
import os
import tempfile
import zipfile
import fitz
import pandas as pd
import streamlit as st
import tabula
from fpdf import FPDF

st.set_page_config(page_title="PDF Automation Suite", layout="wide")

st.set_page_config(page_title="PDF Automation Suite", layout="wide")

def load_css(file_name):
    css_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css("style.css")

# Track which box/tool is currently open
if "tool" not in st.session_state:
    st.session_state.tool = "home"

def go_to(tool_name):
    st.session_state.tool = tool_name

# Helper to safely save FPDF output as bytes
def fpdf_to_bytes(pdf_obj):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        temp_path = tmp.name
    pdf_obj.output(temp_path)
    with open(temp_path, "rb") as f:
        data = f.read()
    os.remove(temp_path)
    return data

# ==========================================
# HOME SCREEN: 4 CLICKABLE BOXES
# ==========================================
if st.session_state.tool == "home":
    st.title("PDF Automation Suite")
    st.write("Choose a tool below to upload your files and run the automation.")

    # Row 1: Tools 1 & 2
    r1_col1, r1_col2 = st.columns(2)
    with r1_col1:
        with st.container(key="card1", border=True):
            st.subheader("1. Create PDF Document")
            st.write("Upload an image and enter text to generate a formatted PDF.")
            if st.button("Open Tool", key="btn1", use_container_width=True):
                go_to("create_pdf")
                st.rerun()

    with r1_col2:
        with st.container(key="card2", border=True):
            st.subheader("2. Bulk PDFs from Excel")
            st.write("Upload an Excel file (.xlsx) to generate one PDF per row.")
            if st.button("Open Tool", key="btn2", use_container_width=True):
                go_to("excel_to_pdf")
                st.rerun()

    # Row 2: Tools 3 & 4
    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        with st.container(key="card3", border=True):
            st.subheader("3. Extract Text from PDF")
            st.write("Upload any PDF to pull out all its readable text.")
            if st.button("Open Tool", key="btn3", use_container_width=True):
                go_to("extract_text")
                st.rerun()

    with r2_col2:
        with st.container(key="card4", border=True):
            st.subheader("4. Extract Tables from PDF")
            st.write("Upload a PDF with tables and export them cleanly to CSV.")
            if st.button("Open Tool", key="btn4", use_container_width=True):
                go_to("extract_table")
                st.rerun()

# ==========================================
# TOOL 1: CREATE PDF DOCUMENT
# ==========================================
elif st.session_state.tool == "create_pdf":
    st.button("← Back to Home", on_click=go_to, args=("home",))
    st.header("1. Create PDF Document")

    img_file = st.file_uploader("Upload an Image (optional)", type=["jpg", "jpeg", "png"])
    title = st.text_input("Title", value="Malayan Tiger")
    description = st.text_area("Description", value="Enter your paragraph here...")
    label1 = st.text_input("Label 1", value="Kingdom")
    val1 = st.text_input("Value 1", value="Animalia")
    label2 = st.text_input("Label 2", value="Phylum")
    val2 = st.text_input("Value 2", value="Chordata")

    if st.button("Generate PDF", type="primary"):
        pdf = FPDF(orientation="P", unit="pt", format="A4")
        pdf.add_page()

        img_temp_path = None
        if img_file is not None:
            suffix = os.path.splitext(img_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_img:
                tmp_img.write(img_file.read())
                img_temp_path = tmp_img.name
            pdf.image(img_temp_path, w=80, h=50)

        pdf.set_font(family="Times", style="B", size=24)
        pdf.cell(w=0, h=50, txt=title, align="C", ln=1)

        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=0, h=15, txt="Description", ln=1)

        pdf.set_font(family="Times", size=12)
        pdf.multi_cell(w=0, h=15, txt=description)

        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=100, h=25, txt=f"{label1}:")
        pdf.set_font(family="Times", size=14)
        pdf.cell(w=100, h=25, txt=val1, ln=1)

        pdf.set_font(family="Times", style="B", size=14)
        pdf.cell(w=100, h=25, txt=f"{label2}:")
        pdf.set_font(family="Times", size=14)
        pdf.cell(w=100, h=25, txt=val2, ln=1)

        pdf_bytes = fpdf_to_bytes(pdf)
        if img_temp_path and os.path.exists(img_temp_path):
            os.remove(img_temp_path)

        st.success("PDF generated!")
        st.download_button("Download output.pdf", data=pdf_bytes, file_name="output.pdf", mime="application/pdf")

# ==========================================
# TOOL 2: BULK PDFs FROM EXCEL
# ==========================================
elif st.session_state.tool == "excel_to_pdf":
    st.button("← Back to Home", on_click=go_to, args=("home",))
    st.header("2. Bulk PDFs from Excel")

    excel_file = st.file_uploader("Upload Excel Spreadsheet (.xlsx)", type=["xlsx"])

    if excel_file is not None:
        df = pd.read_excel(excel_file)
        st.dataframe(df)

        if st.button("Generate All PDFs", type="primary"):
            zip_buffer = io.BytesIO()
            title_col = df.columns[0]  # Uses the first column (e.g., 'name') as title

            with zipfile.ZipFile(zip_buffer, "w") as zf:
                for _, row in df.iterrows():
                    pdf = FPDF(orientation="P", unit="pt", format="A4")
                    pdf.add_page()

                    pdf.set_font(family="Times", style="B", size=24)
                    pdf.cell(w=0, h=50, txt=str(row[title_col]), align="C", ln=1)

                    for column in df.columns[1:]:
                        pdf.set_font(family="Times", style="B", size=14)
                        pdf.cell(w=120, h=25, txt=f"{str(column).title()}:")

                        pdf.set_font(family="Times", size=14)
                        pdf.cell(w=0, h=25, txt=str(row[column]), ln=1)

                    pdf_bytes = fpdf_to_bytes(pdf)
                    zf.writestr(f"{row[title_col]}.pdf", pdf_bytes)

            st.success(f"Generated {len(df)} PDFs!")
            st.download_button(
                "Download All PDFs (.zip)",
                data=zip_buffer.getvalue(),
                file_name="bulk_pdf_reports.zip",
                mime="application/zip",
            )

# ==========================================
# TOOL 3: EXTRACT TEXT FROM PDF
# ==========================================
elif st.session_state.tool == "extract_text":
    st.button("← Back to Home", on_click=go_to, args=("home",))
    st.header("3. Extract Text from PDF")

    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if pdf_file is not None and st.button("Extract Text", type="primary"):
        with fitz.open(stream=pdf_file.read(), filetype="pdf") as pdf:
            extracted_text = "".join(page.get_text() for page in pdf)

        st.text_area("Extracted Text", value=extracted_text, height=350)
        st.download_button("Download as .txt", data=extracted_text, file_name="extracted_text.txt", mime="text/plain")

# ==========================================
# TOOL 4: EXTRACT TABLES FROM PDF
# ==========================================
elif st.session_state.tool == "extract_table":
    st.button("← Back to Home", on_click=go_to, args=("home",))
    st.header("4. Extract Tables from PDF")

    pdf_file = st.file_uploader("Upload a PDF with tables", type=["pdf"])
    page_num = st.number_input("Page Number to Scan", min_value=1, value=1, step=1)

    if pdf_file is not None and st.button("Extract Table to CSV", type="primary"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
            tmp_pdf.write(pdf_file.read())
            temp_pdf_path = tmp_pdf.name

        try:
            tables = tabula.read_pdf(temp_pdf_path, pages=int(page_num))
            if tables:
                st.dataframe(tables[0])
                csv_data = tables[0].to_csv(index=False).encode("utf-8")
                st.download_button("Download output.csv", data=csv_data, file_name="output.csv", mime="text/csv")
            else:
                st.warning("No tables were found on that page.")
        finally:
            os.remove(temp_pdf_path)