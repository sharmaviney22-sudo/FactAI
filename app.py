import streamlit as st
import fitz  # PyMuPDF
from groq import Groq
import json
import re
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactGuard AI - Precision Fact Checking",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

[data-testid="stAppViewContainer"] {
    background: #0f0f1a;
    background-image: 
        linear-gradient(rgba(56, 189, 248, 0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(56, 189, 248, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
}

[data-testid="stHeader"] {
    background: rgba(15, 15, 26, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(56, 189, 248, 0.2);
}

/* Main container */
.main-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem;
}

/* Navigation */
.nav-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 1px solid rgba(56, 189, 248, 0.15);
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-icon {
    font-size: 2rem;
}

.logo-text {
    font-family: 'Inter', sans-serif;
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

.nav-links {
    display: flex;
    gap: 2rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
}

.nav-links span {
    color: #94a3b8;
    cursor: pointer;
    transition: color 0.3s;
}

.nav-links span:hover {
    color: #38bdf8;
}

/* Hero section */
.hero-section {
    text-align: center;
    padding: 3rem 1rem 4rem;
    background: linear-gradient(135deg, rgba(56, 189, 248, 0.05) 0%, rgba(192, 132, 252, 0.05) 100%);
    border-radius: 24px;
    margin-bottom: 3rem;
    border: 1px solid rgba(56, 189, 248, 0.1);
}

.main-title {
    font-family: 'Inter', sans-serif;
    font-weight: 800;
    font-size: clamp(2.5rem, 7vw, 5rem);
    letter-spacing: -2px;
    background: linear-gradient(135deg, #38bdf8 0%, #a78bfa 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
}

.tagline {
    font-family: 'Inter', sans-serif;
    font-size: 1.2rem;
    color: #94a3b8;
    margin-bottom: 0.5rem;
}

.subtitle {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: #64748b;
    letter-spacing: 1px;
}

/* Upload area */
.upload-area {
    background: rgba(30, 41, 59, 0.5);
    border: 2px dashed rgba(56, 189, 248, 0.3);
    border-radius: 20px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s;
    margin-bottom: 2rem;
}

.upload-area:hover {
    border-color: #38bdf8;
    background: rgba(56, 189, 248, 0.05);
}

.upload-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
}

/* Button styling */
.analyze-btn {
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    font-size: 1rem;
    font-weight: 600;
    border-radius: 12px;
    width: 100%;
    cursor: pointer;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
}

.analyze-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}

.analyze-btn:hover::before {
    left: 100%;
}

.analyze-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(56, 189, 248, 0.4);
}

/* Stats grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: rgba(30, 41, 59, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(56, 189, 248, 0.15);
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s;
}

.stat-card:hover {
    transform: translateY(-5px);
    border-color: rgba(56, 189, 248, 0.4);
    box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}

.stat-number {
    font-family: 'Inter', sans-serif;
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
}

/* Results section */
.results-section {
    margin-top: 2rem;
}

.section-header {
    font-family: 'Inter', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 10px;
}

.section-header::before {
    content: '';
    width: 4px;
    height: 24px;
    background: linear-gradient(135deg, #38bdf8, #818cf8);
    border-radius: 2px;
}

/* Claim cards */
.claim-card {
    background: rgba(30, 41, 59, 0.4);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border-left: 4px solid;
    transition: all 0.3s;
}

.claim-card:hover {
    transform: translateX(5px);
    background: rgba(30, 41, 59, 0.6);
}

.claim-card.verified {
    border-left-color: #10b981;
}

.claim-card.inaccurate {
    border-left-color: #f59e0b;
}

.claim-card.false {
    border-left-color: #ef4444;
}

.claim-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.claim-badge {
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.badge-verified {
    background: rgba(16, 185, 129, 0.2);
    color: #10b981;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-inaccurate {
    background: rgba(245, 158, 11, 0.2);
    color: #f59e0b;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-false {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.claim-text {
    font-family: 'Inter', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    color: #f1f5f9;
    margin-bottom: 0.75rem;
    line-height: 1.5;
}

.claim-explanation {
    font-family: 'Inter', sans-serif;
    font-size: 0.85rem;
    color: #94a3b8;
    line-height: 1.6;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(148, 163, 184, 0.1);
}

/* Loading animation */
.loading-wrapper {
    text-align: center;
    padding: 3rem;
}

.loading-spinner {
    width: 50px;
    height: 50px;
    border: 3px solid rgba(56, 189, 248, 0.2);
    border-top-color: #38bdf8;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

/* Footer */
.footer {
    margin-top: 4rem;
    padding: 2rem;
    text-align: center;
    border-top: 1px solid rgba(56, 189, 248, 0.1);
    font-family: 'Inter', sans-serif;
    font-size: 0.8rem;
    color: #64748b;
}

/* Responsive */
@media (max-width: 768px) {
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .nav-links {
        display: none;
    }
}

/* Custom file uploader */
[data-testid="stFileUploader"] {
    background: transparent;
}

[data-testid="stFileUploader"] > div:first-child {
    background: transparent;
}

/* Success message */
.success-message {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    color: #10b981;
    font-size: 0.9rem;
    margin-top: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers (same as before) ───────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file) -> str:
    data = uploaded_file.read()
    doc = fitz.open(stream=data, filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def analyze_claims(text: str, api_key: str) -> list:
    client = Groq(api_key=api_key)
    
    prompt = f"""You are an expert fact-checker AI. Analyze the following document text and:

1. Extract ALL specific, verifiable claims — focus on:
   - Statistics and numbers (e.g., "X% of users", "revenue of $Y billion")
   - Dates and timelines
   - Named entities with attributed facts
   - Technical/scientific claims
   - Financial figures

2. For EACH claim, verify it using your knowledge and flag if it seems outdated or potentially false.

3. Classify each claim as:
   - "Verified" — claim is accurate and matches known data
   - "Inaccurate" — claim is outdated or partially wrong
   - "False" — claim is clearly incorrect or fabricated

Return a JSON array of objects. Each object must have EXACTLY these keys:
- "claim": the exact claim from the document (string)
- "status": one of "Verified", "Inaccurate", or "False" (string)
- "explanation": brief explanation of your verdict, including the correct fact if wrong (string)

Extract at least 5 claims. Return ONLY valid JSON. No markdown, no preamble.

Document text:
\"\"\"
{text[:6000]}
\"\"\"
"""
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a fact-checking AI. Always respond with valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"^```json\s*", "", raw)
        raw = re.sub(r"```$", "", raw)
        raw = re.sub(r"^```\s*", "", raw)
        
        data = json.loads(raw)
        
        if isinstance(data, dict):
            if "claims" in data:
                claims_data = data["claims"]
            elif "results" in data:
                claims_data = data["results"]
            else:
                claims_data = []
                for value in data.values():
                    if isinstance(value, list):
                        claims_data = value
                        break
        elif isinstance(data, list):
            claims_data = data
        else:
            claims_data = []
        
        validated = []
        for claim in claims_data:
            if isinstance(claim, dict) and all(k in claim for k in ["claim", "status", "explanation"]):
                validated.append(claim)
        
        return validated
        
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return []


# ── UI Implementation ────────────────────────────────────────────────────────

# Get API key
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.environ.get("GROQ_API_KEY", "")
    
    if not api_key:
        st.error("""
        ⚠️ **API Key Missing**
        
        Please add your Groq API key to Streamlit Secrets:
        1. Go to your app settings on Streamlit Cloud
        2. Add secret: `GROQ_API_KEY` = `your_key_here`
        
        *For local development: set environment variable `GROQ_API_KEY`*
        """)
        st.stop()

# UI Layout
st.markdown("""
<div class="main-container">
    <div class="nav-bar">
        <div class="logo">
            <div class="logo-icon">🛡️</div>
            <div class="logo-text">FactGuard AI</div>
        </div>
        <div class="nav-links">
            <span>Dashboard</span>
            <span>Analytics</span>
            <span>Documentation</span>
            <span>Support</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="main-title">Precision Fact Checking<br>for Critical Documents</div>
    <div class="tagline">AI-Powered Verification | Real-time Analysis | Comprehensive Reports</div>
    <div class="subtitle">Powered by Groq's Llama 3.3 70B</div>
</div>
""", unsafe_allow_html=True)

# Upload Section
st.markdown("""
<div class="upload-area">
    <div class="upload-icon">📄</div>
    <h3 style="margin-bottom: 0.5rem; color: #f1f5f9;">Upload Your Document</h3>
    <p style="color: #94a3b8; margin-bottom: 1rem;">Supported format: PDF</p>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "",
    type=["pdf"],
    label_visibility="collapsed"
)

if uploaded_file:
    st.markdown(f"""
    <div class="success-message">
        ✅ Successfully loaded: <strong>{uploaded_file.name}</strong>
    </div>
    """, unsafe_allow_html=True)

# Analyze Button
st.markdown("<br>", unsafe_allow_html=True)
run = st.button("🔍 ANALYZE DOCUMENT", use_container_width=True, type="primary")

if run:
    if not uploaded_file:
        st.error("⚠️ Please upload a PDF document first.")
    else:
        with st.spinner(""):
            st.markdown("""
            <div class="loading-wrapper">
                <div class="loading-spinner"></div>
                <p style="color: #94a3b8;">Extracting text from PDF...</p>
            </div>
            """, unsafe_allow_html=True)
            doc_text = extract_text_from_pdf(uploaded_file)

        if len(doc_text.strip()) < 50:
            st.error("⚠️ Could not extract readable text. Try a text-based PDF.")
        else:
            with st.spinner(""):
                st.markdown("""
                <div class="loading-wrapper">
                    <div class="loading-spinner"></div>
                    <p style="color: #94a3b8;">🤖 Groq AI is analyzing claims...</p>
                </div>
                """, unsafe_allow_html=True)
                claims = analyze_claims(doc_text, api_key)

            if claims and len(claims) > 0:
                verified = [c for c in claims if c.get("status") == "Verified"]
                inaccurate = [c for c in claims if c.get("status") == "Inaccurate"]
                false_ = [c for c in claims if c.get("status") == "False"]

                # Stats Section
                st.markdown("""
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" style="color: #f1f5f9;">""" + str(len(claims)) + """</div>
                        <div class="stat-label">Total Claims</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #10b981;">""" + str(len(verified)) + """</div>
                        <div class="stat-label">Verified ✓</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #f59e0b;">""" + str(len(inaccurate)) + """</div>
                        <div class="stat-label">Inaccurate ⚠</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #ef4444;">""" + str(len(false_)) + """</div>
                        <div class="stat-label">False ✗</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Results Section
                st.markdown('<div class="results-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">Detailed Analysis</div>', unsafe_allow_html=True)

                # False Claims First (most critical)
                if false_:
                    for item in false_:
                        st.markdown(f"""
                        <div class="claim-card false">
                            <div class="claim-header">
                                <span class="claim-badge badge-false">❌ FALSE</span>
                            </div>
                            <div class="claim-text">"{item.get('claim', 'N/A')}"</div>
                            <div class="claim-explanation">→ {item.get('explanation', 'No explanation')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Inaccurate Claims
                if inaccurate:
                    for item in inaccurate:
                        st.markdown(f"""
                        <div class="claim-card inaccurate">
                            <div class="claim-header">
                                <span class="claim-badge badge-inaccurate">⚠ INACCURATE</span>
                            </div>
                            <div class="claim-text">"{item.get('claim', 'N/A')}"</div>
                            <div class="claim-explanation">→ {item.get('explanation', 'No explanation')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Verified Claims
                if verified:
                    for item in verified:
                        st.markdown(f"""
                        <div class="claim-card verified">
                            <div class="claim-header">
                                <span class="claim-badge badge-verified">✓ VERIFIED</span>
                            </div>
                            <div class="claim-text">"{item.get('claim', 'N/A')}"</div>
                            <div class="claim-explanation">→ {item.get('explanation', 'No explanation')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ No valid claims were extracted from the document. Please try a different PDF or check the content format.")

# Footer
st.markdown("""
<div class="footer">
    <p>FactGuard AI · Powered by Groq's Llama 3.3 70B · Built for Precision & Reliability</p>
    <p style="font-size: 0.7rem; margin-top: 0.5rem;">© 2024 FactGuard AI · All Rights Reserved</p>
</div>
""", unsafe_allow_html=True)
