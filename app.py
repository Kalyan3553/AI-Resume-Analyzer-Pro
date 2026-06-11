import streamlit as st
import plotly.graph_objects as go
import os
from resume_parser import extract_text
from skill_matcher import find_skills
from scorer import calculate_score
from missing_skills import find_missing_skills
from ats_score import calculate_ats_score
from company_matcher import company_match

os.makedirs("resume", exist_ok=True)

st.set_page_config(
    page_title="AI Resume Analyzer Pro",
    page_icon="🚀",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Animated mesh background ── */
.stApp {
    background: #070714;
    color: #E8E6F0;
    overflow-x: hidden;
}
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background:
        radial-gradient(ellipse 80% 60% at 10% 0%,   rgba(99,60,255,0.22) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 90% 10%,  rgba(236,72,153,0.15) 0%, transparent 55%),
        radial-gradient(ellipse 70% 60% at 50% 100%, rgba(6,182,212,0.12)  0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 80% 70%,  rgba(124,58,237,0.10) 0%, transparent 50%);
    animation: bgShift 12s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
}
@keyframes bgShift {
    0%   { opacity: 1;    filter: hue-rotate(0deg); }
    50%  { opacity: 0.85; filter: hue-rotate(20deg); }
    100% { opacity: 1;    filter: hue-rotate(-15deg); }
}

/* Noise grain overlay */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.04'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.5;
}

/* Push all streamlit content above overlays */
.block-container { position: relative; z-index: 1; padding-top: 2rem !important; }

/* ── Hero ── */
.hero {
    background: linear-gradient(135deg, rgba(99,60,255,0.18) 0%, rgba(236,72,153,0.10) 100%);
    border: 1px solid rgba(108,99,255,0.35);
    border-radius: 22px;
    padding: 2.2rem 2.5rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    backdrop-filter: blur(12px);
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(108,99,255,0.3) 0%, transparent 70%);
    animation: pulse 4s ease-in-out infinite;
}
@keyframes pulse {
    0%, 100% { transform: scale(1);   opacity: 0.6; }
    50%       { transform: scale(1.2); opacity: 1; }
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 28px; font-weight: 700;
    color: #fff; margin: 0 0 8px;
    letter-spacing: -0.5px;
}
.hero p { font-size: 14px; color: #9B97CC; margin: 0; }
.hero-badge {
    background: linear-gradient(135deg, #6C3FFF, #EC4899);
    color: #fff; font-size: 11px; font-weight: 700;
    letter-spacing: 0.1em; padding: 4px 14px;
    border-radius: 99px; text-transform: uppercase;
}

/* ── Section label ── */
.slabel {
    font-size: 10px; font-weight: 700; color: #7C6FFF;
    letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 10px;
}

/* Premium Dropdown */
div[data-baseweb="select"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(108,99,255,0.4) !important;
    border-radius: 14px !important;
}

div[data-baseweb="select"] * {
    color: white !important;
    font-size: 15px !important;
    font-weight: 600 !important;
}

div[data-baseweb="popover"] {
    background: #111827 !important;
}

/* ── Company logo cards ── */
.company-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 1.5rem;
}
.company-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 20px 12px;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s ease;
    position: relative;
    overflow: hidden;
}
.company-card:hover {
    background: rgba(108,99,255,0.10);
    border-color: rgba(108,99,255,0.4);
    transform: translateY(-2px);
}
.company-card.active {
    background: rgba(108,99,255,0.15);
    border-color: #6C63FF;
    box-shadow: 0 0 0 3px rgba(108,99,255,0.15), 0 8px 30px rgba(108,99,255,0.2);
}
.company-card.active::after {
    content: '✓';
    position: absolute;
    top: 8px; right: 10px;
    font-size: 11px; font-weight: 700;
    color: #6C63FF;
}

/* ── Streamlit buttons — base reset ── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1.5px dashed rgba(108,99,255,0.4) !important;
    border-radius: 14px !important;
}
[data-testid="stFileUploader"] * { color: #8B87B8 !important; }

/* ── Metric cards ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin: 1.75rem 0;
}
.mcard {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.4rem 1.5rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    animation: cardIn 0.5s ease both;
}
.mcard:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0,0,0,0.3);
}
@keyframes cardIn {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}
.mcard:nth-child(1) { animation-delay: 0.05s; }
.mcard:nth-child(2) { animation-delay: 0.10s; }
.mcard:nth-child(3) { animation-delay: 0.15s; }
.mcard:nth-child(4) { animation-delay: 0.20s; }
.mcard::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 50% 0%, var(--glow) 0%, transparent 65%);
    opacity: 0.18;
}
.mcard::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
}
.mcard-icon { font-size: 22px; margin-bottom: 8px; }
.mcard-val {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 32px; font-weight: 700;
    color: var(--accent); line-height: 1; margin-bottom: 6px;
}
.mcard-lbl { font-size: 12px; color: #8B87B8; font-weight: 500; }
.mcard-sub { font-size: 10px; color: #3E3B60; margin-top: 4px; }

/* ── Section cards ── */
.scard {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    backdrop-filter: blur(8px);
    animation: cardIn 0.4s ease both;
    transition: border-color 0.3s;
}
.scard:hover { border-color: rgba(108,99,255,0.3); }
.scard-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 15px; font-weight: 700; color: #E8E6F0;
    margin-bottom: 1.1rem;
    display: flex; align-items: center; gap: 9px;
}
.scard-title .icon {
    width: 30px; height: 30px; border-radius: 9px;
    background: rgba(108,99,255,0.15);
    border: 1px solid rgba(108,99,255,0.25);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 15px;
}

/* ── Skill badges ── */
.bwrap { display: flex; flex-wrap: wrap; gap: 8px; }
.badge {
    font-size: 12px; font-weight: 600;
    padding: 5px 13px; border-radius: 99px;
    border: 1px solid transparent;
    transition: transform 0.15s;
}
.badge:hover { transform: scale(1.05); }
.b-found { background: rgba(74,222,128,0.1);  color: #4ADE80; border-color: rgba(74,222,128,0.25); }
.b-miss  { background: rgba(248,113,113,0.1); color: #F87171; border-color: rgba(248,113,113,0.25); }
.b-match { background: rgba(167,139,250,0.1); color: #A78BFA; border-color: rgba(167,139,250,0.25); }
.b-req   { background: rgba(251,176,64,0.1);  color: #FBB040; border-color: rgba(251,176,64,0.25); }

/* ── Progress ── */
.prog-row { display: flex; justify-content: space-between; font-size: 13px; color: #8B87B8; margin-bottom: 8px; }
.prog-row strong { color: #A78BFA; font-size: 16px; }
.prog-bg { height: 8px; background: rgba(255,255,255,0.05); border-radius: 99px; overflow: hidden; border: 1px solid rgba(255,255,255,0.07); }
.prog-fill { height: 100%; border-radius: 99px; background: linear-gradient(90deg, #6C3FFF, #EC4899); box-shadow: 0 0 10px rgba(108,63,255,0.5); }
.prog-hint { font-size: 11px; color: #4A4770; margin-top: 8px; }

/* ── Suggestions ── */
.sugg-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 10px 0; border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 13px; color: #C4C0E8;
}
.sugg-item:last-child { border-bottom: none; }
.sugg-num {
    width: 24px; height: 24px; border-radius: 7px;
    background: rgba(108,63,255,0.15); color: #A78BFA;
    font-size: 11px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; border: 1px solid rgba(108,99,255,0.25);
}

/* ── Resume preview ── */
.rprev {
    background: rgba(0,0,0,0.3);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 12px; padding: 1rem 1.25rem;
    font-family: 'Courier New', monospace; font-size: 12px;
    color: #5A5780; line-height: 1.75;
    max-height: 260px; overflow-y: auto; white-space: pre-wrap;
}

/* ── Empty state ── */
.empty {
    text-align: center; padding: 4rem 1rem;
    color: #3E3B60; font-size: 14px;
}
.empty .big { font-size: 48px; margin-bottom: 14px; }

/* ── Divider ── */
.div { border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 0.5rem 0 1.25rem; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div>
        <h1>🚀 AI Resume Analyzer Pro</h1>
        <p>Instant skill gap analysis — see how you stack up at top companies</p>
    </div>
    <span class="hero-badge">Pro</span>
</div>
""", unsafe_allow_html=True)

# ── Company logo picker ────────────────────────────────────────────────────────
COMPANIES = [
    "Google",
    "Amazon",
    "IBM",
    "Cisco",
    "Cognizant",
    "Tech Mahindra",
    "Infosys",
    "Microsoft",
    "TCS",
    "Wipro"
]

# Inline SVG logos — no external CDN needed, always render
LOGOS = {
    "TCS": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60" width="90" height="28">
        <text x="0" y="44" font-family="Arial Black,sans-serif" font-weight="900" font-size="52" fill="#FFFFFF" letter-spacing="-2">TCS</text>
    </svg>""",

    "Infosys": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 60" width="110" height="28">
        <text x="0" y="44" font-family="Arial,sans-serif" font-weight="700" font-size="40" fill="#FFFFFF">infosys</text>
    </svg>""",

    "Amazon": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 80" width="90" height="40">
        <text x="0" y="38" font-family="Arial,sans-serif" font-weight="900" font-size="36" fill="#FFFFFF">amazon</text>
        <path d="M5 52 Q55 72 110 52" stroke="#FF9900" stroke-width="4" fill="none" stroke-linecap="round"/>
        <polygon points="108,46 116,54 104,56" fill="#FF9900"/>
    </svg>""",

    "Google": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 60" width="100" height="30">
        <text x="0" y="44" font-family="Arial,sans-serif" font-weight="700" font-size="44" fill="none">
            <tspan fill="#4285F4">G</tspan><tspan fill="#EA4335">o</tspan><tspan fill="#FBBC05">o</tspan><tspan fill="#4285F4">g</tspan><tspan fill="#34A853">l</tspan><tspan fill="#EA4335">e</tspan>
        </text>
    </svg>""",
}

logo_map = {
    "Google": "logos/google.png",
    "Amazon": "logos/amazon.png",
    "IBM": "logos/ibm.png",
    "Cisco": "logos/cisco.png",
    "Cognizant": "logos/cognizant.png",
    "Tech Mahindra": "logos/tech_mahindra.png",
    "Infosys": "logos/infosys.png",
    "Microsoft": "logos/microsoft.png",
    "TCS": "logos/tcs.png",
    "Wipro": "logos/wipro.png"
}

# Brand accent colors per company
COLORS = {
    "Google": "#4285F4",
    "Amazon": "#FF9900",
    "IBM": "#1261FE",
    "Cisco": "#1BA0D7",
    "Cognizant": "#0057B8",
    "Tech Mahindra": "#E31837",
    "Infosys": "#007CC3",
    "Microsoft": "#F25022",
    "TCS": "#0066CC",
    "Wipro": "#8E44AD"
}

st.markdown(
    '<div class="slabel">🏢 Select Target Company</div>',
    unsafe_allow_html=True
)

company = st.selectbox(
    "Select Company",
    COMPANIES,
    label_visibility="collapsed"
)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns([1,4])

with col1:
    st.image(
        logo_map[company],
        width=90
    )

with col2:
    st.markdown(
        f"""
        <h2 style='color:white;margin-top:20px;'>
        {company}
        </h2>
        """,
        unsafe_allow_html=True
    )

# ── File uploader ──────────────────────────────────────────────────────────────
st.markdown('<div class="slabel">📎 Upload your resume (PDF)</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")
st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

# ── Analyze button — fully self-contained style ────────────────────────────────
st.markdown("""
<style>
div[data-testid="stButton"].analyze-btn > button,
.stButton.analyze-btn > button {
    background: linear-gradient(135deg,#6C3FFF 0%,#EC4899 100%) !important;
}
</style>
""", unsafe_allow_html=True)

# Override ALL stButton styles back to gradient for the analyze button
# by placing it after the per-column overrides above
st.markdown("""
<style>
/* Reset the last stButton on the page to be the gradient analyze button */
section.main .block-container > div > div:last-child .stButton > button {
    background: linear-gradient(135deg, #6C3FFF 0%, #EC4899 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.75rem 2rem !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    width: 100% !important;
    height: auto !important;
    min-height: unset !important;
    margin-top: 0 !important;
    box-shadow: 0 4px 24px rgba(108,63,255,0.4) !important;
    letter-spacing: 0.04em !important;
}
</style>
""", unsafe_allow_html=True)
analyze_clicked = st.button("🚀  Analyze Resume", use_container_width=True, key="analyze_btn")

# ── Main ───────────────────────────────────────────────────────────────────────
COMPANY_FILES = {
    "Google": "company_skills/google.csv",
    "Amazon": "company_skills/amazon.csv",
    "IBM": "company_skills/IBM.csv",
    "Cisco": "company_skills/cisco.csv",
    "Cognizant": "company_skills/cognizant.csv",
    "Tech Mahindra": "company_skills/tech_mahindra.csv",
    "Infosys": "company_skills/infosys.csv",
    "Microsoft": "company_skills/microsoft.csv",
    "TCS": "company_skills/tcs.csv",
    "Wipro": "company_skills/wipro.csv"
}

if uploaded_file and analyze_clicked:
    with st.spinner("Analyzing your resume..."):
        with open("resume/temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())
        resume_text    = extract_text("resume/temp.pdf")
        skills         = find_skills(resume_text)
        score          = calculate_score(skills, resume_text)
        ats_score      = calculate_ats_score(resume_text)
        missing_skills = find_missing_skills(skills)
        company_score, matched_skills, company_missing = company_match(
            COMPANY_FILES[company], skills
        )

    # ── Metric cards ──────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="metric-row">
        <div class="mcard" style="--accent:#7C6FFF; --glow:rgba(124,111,255,1);">
            <div class="mcard-icon">📝</div>
            <div class="mcard-val">{score}</div>
            <div class="mcard-lbl">Resume Score</div>
            <div class="mcard-sub">out of 100</div>
        </div>
        <div class="mcard" style="--accent:#34D399; --glow:rgba(52,211,153,1);">
            <div class="mcard-icon">🤖</div>
            <div class="mcard-val">{ats_score}</div>
            <div class="mcard-lbl">ATS Score</div>
            <div class="mcard-sub">out of 100</div>
        </div>
        <div class="mcard" style="--accent:#FBB040; --glow:rgba(251,176,64,1);">
            <div class="mcard-icon">⚡</div>
            <div class="mcard-val">{len(skills)}</div>
            <div class="mcard-lbl">Skills Found</div>
            <div class="mcard-sub">detected in resume</div>
        </div>
        <div class="mcard" style="--accent:#F472B6; --glow:rgba(244,114,182,1);">
            <div class="mcard-icon">🏢</div>
            <div class="mcard-val">{company_score}%</div>
            <div class="mcard-lbl">Company Match</div>
            <div class="mcard-sub">{company}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Pie chart ─────────────────────────────────────────────────────────────
    n_match   = len(matched_skills)
    n_missing = len(company_missing)
    n_other   = max(0, len(skills) - n_match)

    fig = go.Figure(go.Pie(
        labels=["Matched", "Missing", "Other Skills"],
        values=[n_match, n_missing, n_other],
        hole=0.65,
        marker=dict(colors=["#7C6FFF", "#F87171", "#FBB040"],
                    line=dict(color="#070714", width=3)),
        textinfo="percent+label",
        textfont=dict(family="Inter", size=12, color="#E8E6F0"),
        hovertemplate="<b>%{label}</b><br>%{value} skills (%{percent})<extra></extra>"
    ))
    fig.add_annotation(
        text=f"<b>{company_score}%</b><br><span>match</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, color="#E8E6F0", family="Space Grotesk"), align="center"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=20, b=20, l=20, r=20), height=500,
        showlegend=True,
        legend=dict(font=dict(color="#8B87B8", size=12, family="Inter"),
                    bgcolor="rgba(0,0,0,0)", orientation="v",
                    x=0.75, y=0.5, xanchor="left", yanchor="middle")
    )
    st.markdown('<div class="scard"><div class="scard-title"><span class="icon">📊</span> Skill Distribution</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Skills Found + Missing ─────────────────────────────────────────────────
    sk1, sk2 = st.columns(2)
    with sk1:
        found_html = " ".join(f'<span class="badge b-found">{s}</span>' for s in skills) \
                     or '<span style="color:#4A4770">No skills detected</span>'
        st.markdown(f"""
        <div class="scard">
            <div class="scard-title"><span class="icon">✅</span> Skills Found <span style="font-size:12px;color:#4A4770;font-weight:400;margin-left:4px;">({len(skills)})</span></div>
            <div class="bwrap">{found_html}</div>
        </div>""", unsafe_allow_html=True)

    with sk2:
        miss_html = " ".join(f'<span class="badge b-miss">{s}</span>' for s in missing_skills[:15]) \
                    or '<span style="color:#4ADE80">🎉 No missing skills!</span>'
        st.markdown(f"""
        <div class="scard">
            <div class="scard-title"><span class="icon">❌</span> Missing Skills <span style="font-size:12px;color:#4A4770;font-weight:400;margin-left:4px;">({min(len(missing_skills),15)} shown)</span></div>
            <div class="bwrap">{miss_html}</div>
        </div>""", unsafe_allow_html=True)

    # ── Company match ──────────────────────────────────────────────────────────
    cm1, cm2 = st.columns(2)
    with cm1:
        match_html = " ".join(f'<span class="badge b-match">{s}</span>' for s in matched_skills) \
                     or '<span style="color:#4A4770">No matches yet</span>'
        prog_hint  = "✅ All requirements met!" if company_score == 100 \
                     else f"⚡ {len(company_missing)} more skill(s) to reach 100%"
        st.markdown(f"""
        <div class="scard">
            <div class="scard-title"><span class="icon">🏆</span> Matched — {company}</div>
            <div class="prog-row"><span>Match score</span><strong>{company_score}%</strong></div>
            <div class="prog-bg"><div class="prog-fill" style="width:{company_score}%;"></div></div>
            <div class="prog-hint">{prog_hint}</div>
            <div style="height:12px;"></div>
            <div class="bwrap">{match_html}</div>
        </div>""", unsafe_allow_html=True)

    with cm2:
        req_html = " ".join(f'<span class="badge b-req">{s}</span>' for s in company_missing) \
                   or '<span style="color:#4ADE80">🎉 All covered!</span>'
        st.markdown(f"""
        <div class="scard">
            <div class="scard-title"><span class="icon">⚠️</span> Still Required by {company}</div>
            <div class="bwrap">{req_html}</div>
        </div>""", unsafe_allow_html=True)

    # ── Suggestions ───────────────────────────────────────────────────────────
    if company_missing:
        items_html = "".join(
            f'<div class="sugg-item"><div class="sugg-num">{i+1}</div>'
            f'<div>Learn <strong style="color:#A78BFA">{skill}</strong> to boost your {company} match score</div></div>'
            for i, skill in enumerate(company_missing)
        )
    else:
        items_html = '<div style="color:#4ADE80;font-size:13px;padding:8px 0;">✅ Your resume covers all requirements for this role.</div>'

    st.markdown(f"""
    <div class="scard">
        <div class="scard-title"><span class="icon">💡</span> Suggestions</div>
        {items_html}
    </div>""", unsafe_allow_html=True)

    # ── Resume preview ─────────────────────────────────────────────────────────
    preview = resume_text[:2000] + ("…" if len(resume_text) > 2000 else "")
    st.markdown(f"""
    <div class="scard">
        <div class="scard-title"><span class="icon">📄</span> Resume Preview</div>
        <div class="rprev">{preview}</div>
    </div>""", unsafe_allow_html=True)

elif uploaded_file and not analyze_clicked:
    st.markdown("""
    <div class="empty">
        <div class="big">📎</div>
        Resume uploaded — click <strong style="color:#7C6FFF;">Analyze Resume</strong> to continue
    </div>""", unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="empty">
        <div class="big">🚀</div>
        Select a company, upload your PDF resume, and hit Analyze
    </div>""", unsafe_allow_html=True)