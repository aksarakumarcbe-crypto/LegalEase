from __future__ import annotations
import base64
import html
import os
from pathlib import Path
import sys
import requests
import streamlit as st
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
load_dotenv(ROOT_DIR / ".env")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
APP_NAME = os.getenv("APP_NAME", "LegalEase")

st.set_page_config(page_title=APP_NAME, page_icon="⚖️", layout="wide")

st.markdown("""
<style>
.main { background:#f6f7fb; }
.block-container { padding-top:1.5rem; max-width:1250px; }
.hero { padding:1.4rem 1.6rem; border-radius:20px; background:linear-gradient(135deg,#111827,#312e81); color:white; margin-bottom:1rem; }
.hero h1 { margin:0; font-size:2.3rem; }
.hero p { margin:.35rem 0 0; opacity:.86; }
.preview { background:#111827; color:#f9fafb; padding:1.25rem; border-radius:16px; max-height:620px; overflow-y:auto; border:1px solid #374151; line-height:1.65; }
.preview p { margin:0 0 .8rem; }
.notice { padding:.8rem 1rem; border-radius:12px; background:#fff7ed; border:1px solid #fed7aa; color:#7c2d12; }
</style>
""", unsafe_allow_html=True)

for key, default in [("document",""),("model",""),("demo_mode",False),("message","")]:
    if key not in st.session_state:
        st.session_state[key] = default

logo = ROOT_DIR / "assets" / "logo.svg"
if logo.exists():
    encoded = base64.b64encode(logo.read_bytes()).decode()
    st.markdown(
        f'<div style="text-align:center"><img src="data:image/svg+xml;base64,{encoded}" width="120"></div>',
        unsafe_allow_html=True
    )

st.markdown(
    '<div class="hero"><h1>⚖️ LegalEase</h1><p>AI-powered legal document drafting with editable previews and TXT, DOCX and PDF export.</p></div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="notice"><b>Important:</b> LegalEase creates AI-assisted drafts, not legal advice. Review important documents with a qualified legal professional before signing or relying on them.</div>',
    unsafe_allow_html=True
)

with st.sidebar:
    st.header("Document details")
    document_type = st.selectbox(
        "Document type",
        [
            "Employment Contract",
            "Non-Disclosure Agreement (NDA)",
            "Lease Agreement",
            "Freelance Work Contract",
            "Employment Offer Letter",
            "Service Agreement",
            "Partnership Agreement",
            "Custom Legal Agreement",
        ],
    )
    custom_type = st.text_input("Custom document type (optional)", placeholder="e.g. Vendor Agreement")
    parties = st.text_area("Parties involved", placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)", height=100)
    terms = st.text_area(
        "Terms & conditions",
        placeholder="Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice",
        height=170,
        help="Separate clauses with semicolons."
    )
    dates = st.text_input("Effective date / dates", placeholder="October 1, 2026")
    governing_law = st.text_input("Governing law / jurisdiction (optional)", placeholder="e.g. Tamil Nadu, India")
    company_name = st.text_input("Company / brand name (optional)", value=os.getenv("COMPANY_NAME","LegalEase"))
    additional_instructions = st.text_area("Additional instructions (optional)", placeholder="Formal style; include a detailed termination section.", height=100)
    generate = st.button("✨ Generate Document", type="primary", use_container_width=True)

if generate:
    chosen_type = custom_type.strip() or document_type
    missing = [name for name, value in [
        ("parties", parties), ("terms", terms), ("effective date", dates)
    ] if not value.strip()]
    if missing:
        st.error("Please provide: " + ", ".join(missing) + ".")
    else:
        payload = {
            "document_type": chosen_type,
            "parties": parties,
            "terms": terms,
            "dates": dates,
            "governing_law": governing_law,
            "company_name": company_name,
            "additional_instructions": additional_instructions,
        }
        with st.spinner("Generating your legal draft..."):
            try:
                response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()
                st.session_state.document = data["document"]
                st.session_state.model = data.get("model","")
                st.session_state.demo_mode = data.get("demo_mode",False)
                st.session_state.message = data.get("message","")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to FastAPI. Start: `uvicorn backend.main:app --reload --port 8000`")
            except requests.exceptions.RequestException as exc:
                st.error(f"Backend request failed: {exc}")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")

if st.session_state.document:
    st.divider()
    if st.session_state.demo_mode:
        st.warning(st.session_state.message or "Local demo mode is active.")
    else:
        st.success(f"Generated using Gemini model: {st.session_state.model}")

    left, right = st.columns([1.05,1])
    with left:
        st.subheader("Editable document")
        edited = st.text_area(
            "Edit the generated text",
            value=st.session_state.document,
            height=620,
            label_visibility="collapsed"
        )
        if edited != st.session_state.document:
            st.session_state.document = edited

    with right:
        st.subheader("Live preview")
        safe = html.escape(st.session_state.document)
        preview = safe.replace("\n\n","</p><p>").replace("\n","<br>")
        st.markdown(f'<div class="preview"><p>{preview}</p></div>', unsafe_allow_html=True)

    st.subheader("Download")
    st.caption("Downloads are generated locally from the edited text.")

    from backend.utils.document_export import format_docx, format_pdf, format_txt

    chosen_type = custom_type.strip() or document_type
    txt_bytes = format_txt(st.session_state.document)
    docx_bytes = format_docx(st.session_state.document, chosen_type, company_name)
    pdf_bytes = format_pdf(st.session_state.document, chosen_type, company_name)

    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button("⬇️ Download TXT", txt_bytes, "legalease_document.txt", "text/plain", use_container_width=True)
    with d2:
        st.download_button(
            "⬇️ Download DOCX",
            docx_bytes,
            "legalease_document.docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    with d3:
        st.download_button("⬇️ Download PDF", pdf_bytes, "legalease_document.pdf", "application/pdf", use_container_width=True)
else:
    st.info("Fill in the fields in the left sidebar and click **Generate Document**.")

st.divider()
st.caption("LegalEase • AI-assisted legal drafting • Local-first demo application")
