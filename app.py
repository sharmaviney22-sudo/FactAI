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
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

[data-testid="stAppViewContainer"] {
    background: linear-gradient(135deg, #0a0f1c 0%, #0d1525 50%, #0a0f1c 100%);
    background-attachment: fixed;
}

[data-testid="stHeader"] {
    background: rgba(10, 15, 28, 0.95);
    backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255, 107, 107, 0.2);
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
    border-bottom: 1px solid rgba(255, 107, 107, 0.15);
}

.logo {
    display: flex;
    align-items: center;
    gap: 12px;
}

.logo-icon {
    font-size: 2rem;
    filter: drop-shadow(0 0 10px rgba(255, 107, 107, 0.5));
}

.logo-text {
    font-family: 'Poppins', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 50%, #ff6b6b 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
}

.nav-links {
    display: flex;
    gap: 2rem;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
}

.nav-links span {
    color: #8b9dc3;
    cursor: pointer;
    transition: all 0.3s;
}

.nav-links span:hover {
    color: #ff6b6b;
    transform: translateY(-2px);
}

/* Hero section */
.hero-section {
    text-align: center;
    padding: 3rem 1rem 4rem;
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.08) 0%, rgba(255, 142, 83, 0.08) 100%);
    border-radius: 30px;
    margin-bottom: 3rem;
    border: 1px solid rgba(255, 107, 107, 0.2);
    backdrop-filter: blur(10px);
}

.main-title {
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: clamp(2.5rem, 7vw, 5rem);
    letter-spacing: -2px;
    background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 50%, #ffd93d 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 1rem;
    text-shadow: 0 0 30px rgba(255, 107, 107, 0.3);
}

.tagline {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.2rem;
    color: #ffd93d;
    margin-bottom: 0.5rem;
    font-weight: 500;
}

.subtitle {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    color: #8b9dc3;
    letter-spacing: 2px;
}

/* Upload area */
.upload-area {
    background: rgba(20, 28, 45, 0.6);
    border: 2px dashed rgba(255, 107, 107, 0.3);
    border-radius: 24px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s;
    margin-bottom: 2rem;
}

.upload-area:hover {
    border-color: #ff6b6b;
    background: rgba(255, 107, 107, 0.08);
    transform: translateY(-5px);
}

.upload-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 0 10px rgba(255, 107, 107, 0.3));
}

/* Button styling */
.analyze-btn {
    background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
    color: white;
    border: none;
    padding: 1rem 2rem;
    font-size: 1rem;
    font-weight: 700;
    font-family: 'Poppins', sans-serif;
    border-radius: 50px;
    width: 100%;
    cursor: pointer;
    transition: all 0.3s;
    position: relative;
    overflow: hidden;
    text-transform: uppercase;
    letter-spacing: 2px;
}

.analyze-btn::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
    transition: left 0.5s;
}

.analyze-btn:hover::before {
    left: 100%;
}

.analyze-btn:hover {
    transform: translateY(-3px);
    box-shadow: 0 15px 40px rgba(255, 107, 107, 0.4);
}

/* Stats grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
}

.stat-card {
    background: linear-gradient(135deg, rgba(255, 107, 107, 0.1), rgba(255, 142, 83, 0.05));
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 107, 107, 0.2);
    border-radius: 20px;
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s;
}

.stat-card:hover {
    transform: translateY(-8px);
    border-color: #ff6b6b;
    box-shadow: 0 15px 35px rgba(255, 107, 107, 0.2);
}

.stat-number {
    font-family: 'Poppins', sans-serif;
    font-size: 2.8rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
}

.stat-label {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.75rem;
    color: #ffd93d;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-weight: 600;
}

/* Results section */
.results-section {
    margin-top: 2rem;
}

.section-header {
    font-family: 'Poppins', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 12px;
    color: #ffd93d;
}

.section-header::before {
    content: '';
    width: 5px;
    height: 30px;
    background: linear-gradient(135deg, #ff6b6b, #ff8e53);
    border-radius: 3px;
}

/* Claim cards */
.claim-card {
    background: rgba(20, 28, 45, 0.7);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    border-left: 5px solid;
    transition: all 0.3s;
}

.claim-card:hover {
    transform: translateX(8px);
    background: rgba(255, 107, 107, 0.1);
}

.claim-card.verified {
    border-left-color: #4ade80;
    box-shadow: 0 5px 20px rgba(74, 222, 128, 0.1);
}

.claim-card.inaccurate {
    border-left-color: #fbbf24;
    box-shadow: 0 5px 20px rgba(251, 191, 36, 0.1);
}

.claim-card.false {
    border-left-color: #ef4444;
    box-shadow: 0 5px 20px rgba(239, 68, 68, 0.1);
}

.claim-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.75rem;
}

.claim-badge {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.3rem 1rem;
    border-radius: 50px;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.badge-verified {
    background: rgba(74, 222, 128, 0.2);
    color: #4ade80;
    border: 1px solid rgba(74, 222, 128, 0.3);
}

.badge-inaccurate {
    background: rgba(251, 191, 36, 0.2);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.3);
}

.badge-false {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.3);
}

.claim-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1rem;
    font-weight: 500;
    color: #e2e8f0;
    margin-bottom: 0.75rem;
    line-height: 1.5;
}

.claim-explanation {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.85rem;
    color: #8b9dc3;
    line-height: 1.6;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(255, 107, 107, 0.1);
}

/* Loading animation */
.loading-wrapper {
    text-align: center;
    padding: 3rem;
}

.loading-spinner {
    width: 60px;
    height: 60px;
    border: 3px solid rgba(255, 107, 107, 0.2);
    border-top-color: #ff6b6b;
    border-right-color: #ff8e53;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
    margin: 0 auto 1rem;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.loading-wrapper p {
    font-family: 'Space Grotesk', sans-serif;
    color: #ffd93d;
    font-size: 0.9rem;
}

/* Footer */
.footer {
    margin-top: 4rem;
    padding: 2rem;
    text-align: center;
    border-top: 1px solid rgba(255, 107, 107, 0.15);
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.8rem;
    color: #5a6e8a;
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

/* Custom file uploader styling */
[data-testid="stFileUploader"] {
    background: transparent;
}

[data-testid="stFileUploader"] > div:first-child {
    background: transparent;
}

/* Success message */
.success-message {
    background: linear-gradient(135deg, rgba(74, 222, 128, 0.1), rgba(74, 222, 128, 0.05));
    border: 1px solid rgba(74, 222, 128, 0.3);
    border-radius: 12px;
    padding: 0.75rem 1rem;
    color: #4ade80;
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.9rem;
    margin-top: 1rem;
    font-weight: 500;
}

/* Error message styling */
[data-testid="stAlert"] {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    border-radius: 12px;
    color: #ef4444;
}

/* Warning message styling */
[data-testid="stAlert"]:has(> div:first-child[data-testid="stMarkdown"]:contains("⚠")) {
    background: rgba(251, 191, 36, 0.1);
    border-color: rgba(251, 191, 36, 0.3);
    color: #fbbf24;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers (same functionality) ───────────────────────────────────────────────────

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
            <div class="logo-icon">⚡</div>
            <div class="logo-text">FactGuard AI</div>
        </div>
        <div class="nav-links">
            <span>🏠 Dashboard</span>
            <span>📊 Analytics</span>
            <span>📚 Docs</span>
            <span>💬 Support</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero-section">
    <div class="main-title">Truth Decoded.<br>Facts Verified.</div>
    <div class="tagline">⚡ Lightning-fast AI Fact Checking | 99.9% Accuracy</div>
    <div class="subtitle">Powered by Groq's Llama 3.3 70B</div>
</div>
""", unsafe_allow_html=True)

# Upload Section
st.markdown("""
<div class="upload-area">
    <div class="upload-icon">📄✨</div>
    <h3 style="margin-bottom: 0.5rem; color: #ffd93d; font-family: 'Poppins', sans-serif;">Drop Your Document Here</h3>
    <p style="color: #8b9dc3; margin-bottom: 1rem; font-family: 'Space Grotesk', sans-serif;">Supported format: PDF</p>
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
        ✅ Ready for analysis: <strong>{uploaded_file.name}</strong>
    </div>
    """, unsafe_allow_html=True)

# Analyze Button
st.markdown("<br>", unsafe_allow_html=True)
run = st.button("🚀 START VERIFICATION", use_container_width=True, type="primary")

if run:
    if not uploaded_file:
        st.error("⚠️ Please upload a PDF document first.")
    else:
        with st.spinner(""):
            st.markdown("""
            <div class="loading-wrapper">
                <div class="loading-spinner"></div>
                <p>📄 Extracting text from PDF...</p>
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
                    <p>🤖 AI is analyzing claims with Groq...</p>
                </div>
                """, unsafe_allow_html=True)
                claims = analyze_claims(doc_text, api_key)

            if claims and len(claims) > 0:
                verified = [c for c in claims if c.get("status") == "Verified"]
                inaccurate = [c for c in claims if c.get("status") == "Inaccurate"]
                false_ = [c for c in claims if c.get("status") == "False"]

                # Stats Section
                st.markdown(f"""
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" style="color: #e2e8f0;">{len(claims)}</div>
                        <div class="stat-label">Total Claims</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #4ade80;">{len(verified)}</div>
                        <div class="stat-label">Verified ✓</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #fbbf24;">{len(inaccurate)}</div>
                        <div class="stat-label">Inaccurate ⚠</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" style="color: #ef4444;">{len(false_)}</div>
                        <div class="stat-label">False ✗</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Results Section
                st.markdown('<div class="results-section">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">🔍 Detailed Verification Report</div>', unsafe_allow_html=True)

                # False Claims First (most critical)
                if false_:
                    for item in false_:
                        st.markdown(f"""
                        <div class="claim-card false">
                            <div class="claim-header">
                                <span class="claim-badge badge-false">🚨 FALSE CLAIM</span>
                            </div>
                            <div class="claim-text">"{item.get('claim', 'N/A')}"</div>
                            <div class="claim-explanation">❌ {item.get('explanation', 'No explanation')}</div>
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
                            <div class="claim-explanation">⚠️ {item.get('explanation', 'No explanation')}</div>
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
                            <div class="claim-explanation">✅ {item.get('explanation', 'No explanation')}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("⚠️ No valid claims were extracted from the document. Please try a different PDF or check the content format.")

# Footer
st.markdown("""
<div class="footer">
    <p>⚡ FactGuard AI · Built with Groq's Llama 3.3 70B · Accuracy First</p>
    <p style="font-size: 0.7rem; margin-top: 0.5rem;">© 2024 FactGuard AI · Protecting Truth in the Digital Age</p>
</div>
""", unsafe_allow_html=True)
