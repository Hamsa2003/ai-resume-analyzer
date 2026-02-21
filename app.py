import streamlit as st
import requests
import PyPDF2
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io

# ---------------------------
# 🔑 Replace with your FREE API key from HuggingFace
API_KEY = "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"
API_URL = "https://router.huggingface.co/hf-inference/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {API_KEY}"}
# ---------------------------

st.set_page_config(page_title="AI Resume Analyzer", layout="centered")
st.title("📄 AI Resume Analyzer (ATS Optimizer)")

st.write("Upload your resume and paste Job Description to get ATS Score & Suggestions.")

# File uploader
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf","docx","txt"])

job_description = st.text_area("Paste Job Description Here")

def extract_text_from_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def query_api(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 300,
            "min_length": 50,
            "do_sample": False
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    try:
        result = response.json()

        if isinstance(result, list) and "summary_text" in result[0]:
            return result[0]["summary_text"]

        if "error" in result:
            return f"API Error: {result['error']}"

        return "No text generated."

    except Exception as e:
        return f"Unexpected Error: {str(e)}"

def generate_pdf(content):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    for line in content.split("\n"):
        elements.append(Paragraph(line, styles["Normal"]))
        elements.append(Spacer(1, 5))

    doc.build(elements)
    buffer.seek(0)
    return buffer

if st.button("Analyze Resume"):
    if uploaded_file is not None and job_description != "":
        resume_text = extract_text_from_pdf(uploaded_file)

        st.subheader("📊 Resume Text Extracted")
        st.write(resume_text[:500])

        prompt = f"""
        Compare the following resume and job description.
        Give:
        1. ATS Match Score out of 100
        2. Missing Keywords
        3. Improvement Suggestions

        Resume:
        {resume_text}

        Job Description:
        {job_description}
        """

        with st.spinner("Analyzing with AI..."):
            result = query_api(prompt)

        st.subheader("✅ AI Analysis Result")
        st.write(result)

        pdf_file = generate_pdf(result)

        st.download_button(
            label="📥 Download Analysis as PDF",
            data=pdf_file,
            file_name="ATS_Analysis_Report.pdf",
            mime="application/pdf"
        )

    else:
        st.warning("Please upload resume and paste job description.")