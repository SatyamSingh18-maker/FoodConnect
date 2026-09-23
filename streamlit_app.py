"""
FoodConnect — Streamlit front end
A donor <-> NGO surplus-food rescue platform, backed by the Flask API in app.py.

Run:
    pip install streamlit pandas qrcode[pil]
    streamlit run streamlit_app.py
(Needs app.py, models.py, matching.py in the same folder — this file calls
the Flask app directly via its test client, no separate server needed.)
"""
import streamlit as st
from datetime import datetime, date, time
import pandas as pd

from app import app as flask_app

st.set_page_config(
    page_title="FoodConnect | Good Food, Less Waste",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)


APP_NAME = "FoodConnect"
TAGLINE = "Good Food. Less Waste. More Hope."

if "accepted_donation" not in st.session_state:
    st.session_state.accepted_donation = None
if "selected_ngo_id" not in st.session_state:
    st.session_state.selected_ngo_id = None

# ============================================================
# GLOBAL STYLE — high-contrast, crisp text, clearly bordered inputs
# ============================================================
PRIMARY = "#0F4C81"      # deep royal blue — headers, primary actions
PRIMARY_DARK = "#0B3A63"
ACCENT = "#137333"       # emerald green — success / positive state
TEXT = "#1A1A1A"         # near-black — all body text on light backgrounds
BORDER = "#CED4DA"       # visible, deliberate input border
PAGE_BG = "#F4F6F9"      # light page background, distinct from white inputs

st.markdown(
    f"""
    <style>
    /* ---------- Base page ---------- */
    .stApp {{ background: {PAGE_BG}; }}
    .block-container {{ max-width: 1450px; padding-top: 1.1rem; padding-bottom: 2rem; }}
    html, body, [class*="css"] {{ color: {TEXT} !important; }}

    /* ---------- Sidebar (dark, white text) ---------- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {PRIMARY_DARK} 0%, #0b3d35 60%, #0f2f2c 100%);
    }}
    section[data-testid="stSidebar"] * {{ color: #FFFFFF !important; }}
    section[data-testid="stSidebar"] label {{ color: #FFFFFF !important; font-weight: 600 !important; }}

    .brand {{ text-align:center; padding:.5rem 0 1.1rem; }}
    .brand .icon {{ font-size:3rem; line-height:1; }}
    .brand .title {{ font-size:1.8rem; font-weight:800; margin-top:.4rem; color:#FFFFFF !important; }}
    .brand .sub {{ font-size:.82rem; color:#E4EEF7 !important; }}

    /* ---------- Hero ---------- */
    .hero {{
        padding: 2rem 2.1rem; border-radius: 20px;
        background: linear-gradient(135deg, {PRIMARY}, {ACCENT});
        color: #FFFFFF; box-shadow: 0 12px 30px rgba(15,76,129,.25); margin-bottom: 1.1rem;
    }}
    .hero h1 {{ margin:0; font-size:2.3rem; font-weight:800; color:#FFFFFF !important; }}
    .hero p {{ margin:.5rem 0 0; font-size:1.02rem; color:#F3F8FF !important; max-width:820px; }}

    /* ---------- Purpose card ---------- */
    .purpose-card {{
        background: #EAF2FB;
        border-left: 6px solid {PRIMARY};
        border-radius: 12px;
        padding: 1rem 1.4rem;
        margin-bottom: 1.4rem;
        color: {TEXT} !important;
    }}
    .purpose-card .p-title {{ font-weight: 800; font-size: 1.05rem; color: {PRIMARY} !important; margin-bottom: .3rem; }}
    .purpose-card p {{ margin: 0; font-size: 0.98rem; color: {TEXT} !important; line-height: 1.5; }}

    /* ---------- Headings & body text — always dark, never gray ---------- */
    .section-title {{ font-size:1.5rem; font-weight:800; color:{TEXT} !important; margin:.5rem 0 1rem; }}
    .subsection-title {{ font-size:1.08rem; font-weight:750; color:{TEXT} !important; margin:.2rem 0 .6rem; }}
    .helper-text {{ color:#3D3D3D !important; font-size:.92rem; }}

    /* ---------- Cards ---------- */
    .card, .ngo-card, .donation-card {{
        background:#FFFFFF; border:1px solid #DDE3EA; border-radius:16px;
        padding:1.1rem; box-shadow:0 5px 16px rgba(15,23,42,.05); margin-bottom:1rem;
        color:{TEXT} !important;
    }}
    .card *, .ngo-card *, .donation-card * {{ color:{TEXT} !important; }}
    .ngo-card {{ border-color:#CFE1F5; }}
    .donation-card {{ border-color:#CBEAD6; }}
    .card-title {{ font-size:1.05rem; font-weight:800; margin-bottom:.35rem; }}

    /* ---------- Status badges — bold, high-contrast ---------- */
    .badge {{ display:inline-block; padding:.32rem .7rem; border-radius:999px; font-size:.78rem; font-weight:800; margin:.15rem .25rem .15rem 0; }}
    .green {{ background:#D2F4DD; color:#0B5C2A !important; }}
    .blue  {{ background:#D8E8FB; color:{PRIMARY_DARK} !important; }}
    .amber {{ background:#FDECC8; color:#7A4E00 !important; }}
    .red   {{ background:#FBD9D9; color:#8A1414 !important; }}

    /* ---------- INPUT CLARITY: strong visible borders + white fill ---------- */
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input,
    div[data-testid="stDateInput"] input,
    div[data-testid="stTimeInput"] input,
    textarea {{
        border: 2px solid {BORDER} !important;
        background: #FFFFFF !important;
        color: {TEXT} !important;
        border-radius: 9px !important;
        font-weight: 500 !important;
    }}
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stNumberInput"] input:focus,
    div[data-testid="stDateInput"] input:focus,
    div[data-testid="stTimeInput"] input:focus,
    textarea:focus {{
        border: 2px solid {PRIMARY} !important;
        box-shadow: 0 0 0 3px rgba(15,76,129,.15) !important;
    }}
    div[data-baseweb="select"] > div {{
        border: 2px solid {BORDER} !important;
        background: #FFFFFF !important;
        border-radius: 9px !important;
    }}
    /* Labels above every input — always dark and bold, never light gray */
    div[data-testid="stTextInput"] label,
    div[data-testid="stNumberInput"] label,
    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"] label,
    div[data-testid="stTimeInput"] label,
    div[data-testid="stTextArea"] label,
    div[data-testid="stCheckbox"] label {{
        color: {TEXT} !important; font-weight: 650 !important; font-size: .93rem !important;
    }}
    /* Help tooltip icon — make it visible, not faint */
    [data-testid="stTooltipIcon"] {{ color: {PRIMARY} !important; opacity: 1 !important; }}

    /* ---------- Buttons — bold primary color, bold white text ---------- */
    div.stButton > button, div[data-testid="stFormSubmitButton"] > button {{
        background: {PRIMARY} !important;
        color: #FFFFFF !important;
        font-weight: 750 !important;
        border: none !important;
        border-radius: 11px !important;
        min-height: 44px !important;
    }}
    div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {{
        background: {PRIMARY_DARK} !important;
    }}

    /* ---------- Metrics ---------- */
    div[data-testid="stMetric"] {{
        background:#FFFFFF; border:1px solid #DDE3EA; border-radius:16px;
        padding:.95rem; box-shadow:0 5px 16px rgba(15,23,42,.045);
    }}
    div[data-testid="stMetricValue"] {{ color:{TEXT} !important; }}
    div[data-testid="stMetricLabel"] {{ color:{TEXT} !important; font-weight:600 !important; }}

    .footer {{ text-align:center; color:#4A4A4A !important; font-size:.8rem; padding:2rem 0 .5rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# FOODLINK VISUAL SYSTEM — reference-inspired light, fresh dashboard shell
# ============================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,700&display=swap');
    :root { --leaf:#14875d; --leaf-dark:#0b6848; --mint:#e8f7f0; --ink:#183238; --muted:#68777a; --line:#e5ece9; }
    .stApp { background:#f7faf9 !important; font-family:'DM Sans',sans-serif !important; color:#1f2937 !important; }
    .block-container { max-width:1400px !important; padding:.5rem 1.25rem 2rem !important; }
    section[data-testid="stSidebar"] { display:none !important; }
    header[data-testid="stHeader"] { background:transparent !important; }
    .top-brand { display:flex; align-items:center; gap:.55rem; }
    .top-brand .mark { font-size:2.05rem; line-height:1; }
    .top-brand .name { color:var(--leaf-dark); font-family:Georgia,serif; font-size:1.35rem; font-weight:700; line-height:1; }
    .top-brand .tagline { color:#7b8586; font-size:.55rem; margin-top:.18rem; }
    .topbar { border-bottom:1px solid var(--line); padding:.35rem 0 .55rem; margin-bottom:.65rem; }
    div[data-testid="stRadio"] > label { display:none !important; }
    div[data-testid="stRadio"] > div { gap:.65rem !important; justify-content:center; flex-wrap:nowrap !important; }
    div[data-testid="stRadio"] input { opacity:0 !important; width:1px !important; height:1px !important; position:absolute !important; pointer-events:auto !important; }
    div[data-testid="stRadio"] label > div:first-child { opacity:0 !important; width:1px !important; overflow:hidden !important; }
    div[data-testid="stRadio"] label { color:#39494b !important; font-size:.75rem !important; padding:.35rem .15rem !important; }
    div[data-testid="stRadio"] label:hover { color:var(--leaf) !important; }
    .hero { border-radius:10px !important; min-height:225px; padding:2.3rem 2.8rem !important; margin:0 -1.25rem !important; display:flex; align-items:center; overflow:hidden; position:relative; background:linear-gradient(90deg,rgba(11,64,44,.98) 0%,rgba(11,64,44,.8) 44%,rgba(11,64,44,.2) 100%),url('https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=1800&q=85') center/cover !important; box-shadow:0 12px 30px rgba(11,107,70,.14) !important; }
    .hero h1 { font-size:2.45rem !important; line-height:1.12; max-width:650px; letter-spacing:-.03em; }
    .hero h1 em { color:#72e0ae; font-style:normal; }
    .hero p { max-width:510px; font-size:.93rem !important; line-height:1.5; }
    .section-title { color:var(--ink) !important; font-size:1.18rem !important; letter-spacing:-.01em; margin:1.2rem 0 .55rem !important; }
    .helper-text { color:var(--muted) !important; font-size:.78rem !important; }
    .purpose-card { display:none !important; }
    .card,.ngo-card,.donation-card { border:1px solid var(--line) !important; border-radius:8px !important; box-shadow:0 4px 16px rgba(29,70,58,.045) !important; padding:1rem !important; }
    .card-title { color:var(--ink) !important; font-size:.9rem !important; }
    div[data-testid="stMetric"] { background:#fff !important; border:1px solid var(--line) !important; border-radius:8px !important; box-shadow:none !important; padding:.75rem !important; }
    div[data-testid="stMetricValue"] { color:var(--leaf-dark) !important; font-size:1.45rem !important; }
    div[data-testid="stMetricLabel"] { color:var(--muted) !important; font-size:.7rem !important; }
    div.stButton > button,div[data-testid="stFormSubmitButton"] > button { background:var(--leaf) !important; border-radius:6px !important; min-height:38px !important; font-size:.78rem !important; }
    div.stButton > button:hover,div[data-testid="stFormSubmitButton"] > button:hover { background:var(--leaf-dark) !important; }
    .dashboard-intro { padding:.9rem 0 .35rem; }
    .dashboard-intro strong { color:var(--ink); font-size:.94rem; }
    .dashboard-intro span { display:block; color:var(--muted); font-size:.75rem; margin-top:.2rem; }
    .impact-strip { background:var(--mint); border-top:1px solid #d8eee4; border-bottom:1px solid #d8eee4; margin:0 -1.25rem; padding:.85rem 1.25rem; }
    .impact-grid { display:grid; grid-template-columns:repeat(4,1fr); }
    .impact-item { text-align:center; padding:.25rem 1rem; border-right:1px solid #d5e9df; }
    .impact-item:last-child { border-right:0; }
    .impact-icon { width:35px; height:35px; display:grid; place-items:center; border:1px solid #bfe5d2; border-radius:50%; margin:0 auto .35rem; background:#f8fffb; font-size:1rem; }
    .impact-item strong { display:block; color:var(--ink); font-size:.76rem; }
    .impact-item span { display:block; color:var(--muted); font-size:.63rem; line-height:1.3; margin-top:.15rem; }
    .dashboard-grid { display:grid; grid-template-columns:minmax(0,1.15fr) minmax(260px,.9fr) minmax(190px,.56fr); gap:.8rem; align-items:start; }
    .kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:.7rem; margin:.25rem 0 1rem; }
    .custom-kpi { display:flex; align-items:center; gap:.6rem; min-height:67px; padding:.75rem; border:1px solid rgba(30,80,60,.08); border-radius:8px; box-shadow:0 4px 12px rgba(29,70,58,.035); }
    .custom-kpi .kpi-icon { width:31px; height:31px; display:grid; place-items:center; border-radius:7px; background:rgba(255,255,255,.7); color:var(--leaf-dark); font-size:1rem; }
    .custom-kpi strong { display:block; color:var(--ink); font-size:1.2rem; line-height:1; }
    .custom-kpi span { display:block; color:var(--muted); font-size:.62rem; margin-top:.25rem; }
    .panel { background:#fff; border:1px solid var(--line); border-radius:8px; padding:.85rem; box-shadow:0 4px 16px rgba(29,70,58,.045); }
    .panel-heading { display:flex; justify-content:space-between; align-items:center; margin-bottom:.65rem; color:var(--ink); font-size:.78rem; font-weight:800; }
    .panel-link { color:var(--leaf); font-size:.64rem; font-weight:700; }
    .food-row { display:grid; grid-template-columns:54px 1fr auto; gap:.6rem; align-items:center; padding:.55rem 0; border-bottom:1px solid #eef3f1; }
    .food-row:last-child { border-bottom:0; }
    .food-image { width:54px; height:54px; border-radius:7px; object-fit:cover; }
    .food-name { color:var(--ink); font-size:.72rem; font-weight:800; }
    .food-meta { color:var(--muted); font-size:.59rem; line-height:1.55; }
    .food-action { background:var(--leaf); color:#fff !important; border-radius:4px; padding:.3rem .45rem; font-size:.58rem; font-weight:700; white-space:nowrap; }
    .activity-item { display:flex; gap:.5rem; padding:.55rem 0; border-bottom:1px solid #eef3f1; }
    .activity-item:last-child { border-bottom:0; }
    .activity-icon { flex:0 0 25px; height:25px; display:grid; place-items:center; border-radius:50%; background:#e2f5ea; font-size:.72rem; }
    .activity-copy { color:var(--muted); font-size:.6rem; line-height:1.4; }
    .activity-copy strong { display:block; color:var(--ink); font-size:.65rem; }
    .footer { border-top:1px solid var(--line); margin-top:1.5rem; color:#879193 !important; font-size:.72rem !important; }
    /* Polished product finish */
    .top-brand .mark { background:#dff5ea; border-radius:50%; width:42px; height:42px; display:grid; place-items:center; font-size:1.55rem; }
    .top-brand .name { letter-spacing:-.025em; }
    div[data-testid="stRadio"] > div { flex-wrap:wrap; }
    div[data-testid="stRadio"] label { border-bottom:2px solid transparent; transition:all .2s ease; }
    div[data-testid="stRadio"] label:has(input:checked) { color:var(--leaf-dark) !important; border-bottom-color:#35b77d; font-weight:700 !important; }
    .hero:after { content:'✦  Good food should reach everyone  ♡'; position:absolute; right:4%; top:36%; color:rgba(255,255,255,.9); font-family:Georgia,serif; font-size:1.05rem; transform:rotate(-5deg); max-width:155px; text-align:center; line-height:1.25; }
    .hero-actions { position:relative; z-index:1; }
    .hero-pill { box-shadow:0 6px 16px rgba(3,34,25,.2); transition:transform .2s ease, box-shadow .2s ease; }
    .hero-pill:hover { transform:translateY(-2px); box-shadow:0 9px 20px rgba(3,34,25,.28); }
    div[data-testid="stMetric"] { position:relative; overflow:hidden; }
    div[data-testid="stMetric"]:before { content:''; position:absolute; inset:0 auto 0 0; width:4px; background:#35b77d; }
    div[data-testid="stMetric"]:nth-child(2):before { background:#55a8dc; }
    div[data-testid="stMetric"]:nth-child(3):before { background:#e8ae4d; }
    div[data-testid="stMetric"]:nth-child(4):before { background:#37a77a; }
    .workflow-card { min-height:88px; transition:transform .2s ease, box-shadow .2s ease; }
    .workflow-card:hover { transform:translateY(-3px); box-shadow:0 10px 24px rgba(29,70,58,.1) !important; }
    .workflow-card .card-title { color:var(--leaf-dark) !important; }
    .donation-card { border-left:4px solid #35b77d !important; }
    .ngo-card { border-left:4px solid #55a8dc !important; }
    .badge { border-radius:5px !important; font-size:.68rem !important; letter-spacing:.02em; }
    .stProgress > div > div > div > div { background:var(--leaf) !important; }
    @media (max-width: 720px) {
        .block-container { padding:.4rem .75rem 1.5rem !important; }
        .hero { margin:0 -.75rem !important; padding:1.8rem 1.2rem !important; min-height:275px; }
        .hero h1 { font-size:1.75rem !important; }
        .hero p { font-size:.82rem !important; max-width:72%; }
        .hero:after { right:3%; top:18%; font-size:.78rem; max-width:85px; }
        .impact-strip { margin:0 -.75rem; padding:.75rem; }
        .top-brand .tagline { display:none; }
        div[data-testid="stRadio"] > div { gap:.3rem !important; justify-content:flex-start; }
        div[data-testid="stRadio"] label { font-size:.65rem !important; }
        .impact-grid { grid-template-columns:repeat(2,1fr); gap:.5rem 0; }
        .impact-item:nth-child(2) { border-right:0; }
        .dashboard-grid { grid-template-columns:1fr; }
        .kpi-grid { grid-template-columns:repeat(2,1fr); }
    }
    @media (min-width: 721px) and (max-width: 1100px) {
        .top-brand .tagline { display:none; }
        .top-brand .name { font-size:1.1rem; }
        div[data-testid="stRadio"] > div { gap:.25rem !important; }
        div[data-testid="stRadio"] label { font-size:.68rem !important; }
        .hero h1 { font-size:2.1rem !important; }
        .kpi-grid { grid-template-columns:repeat(2,1fr); }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================
# Flask app runs inside the same Streamlit process
flask_client = flask_app.test_client()


def api_get(endpoint):
    try:
        response = flask_client.get(endpoint)

        data = response.get_json(silent=True)

        if data is None:
            data = {}

        return response.status_code, data

    except Exception as exc:
        return 503, {
            "error": f"FoodConnect backend is currently unavailable: {exc}"
        }


def api_post(endpoint, payload=None):
    try:
        response = flask_client.post(
            endpoint,
            json=payload or {}
        )

        data = response.get_json(silent=True)

        if data is None:
            data = {}

        return response.status_code, data

    except Exception as exc:
        return 503, {
            "error": f"FoodConnect backend is currently unavailable: {exc}"
        }


def load_ngos():
    code, data = api_get("/api/ngos")
    return data if code == 200 and isinstance(data, list) else []


def load_donations(status_filter=None):
    endpoint = "/api/donations"
    if status_filter:
        endpoint += f"?status={status_filter}"
    code, data = api_get(endpoint)
    return data if code == 200 and isinstance(data, list) else []


def analytics():
    code, data = api_get("/api/analytics")
    if code == 200 and isinstance(data, dict):
        return data
    return {"total_donations": 0, "open": 0, "accepted": 0, "completed": 0}


def page_header(title, subtitle):
    st.markdown(
        f'<div class="section-title">{title}</div>'
        f'<div class="helper-text">{subtitle}</div>',
        unsafe_allow_html=True,
    )


def purpose_card(text):
    st.markdown(
        f'<div class="purpose-card">'
        f'<div class="p-title">💡 What This Page Does</div>'
        f'<p>{text}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def status_badge(status):
    values = {
        "open": ("🟢 OPEN", "green"),
        "accepted": ("🟡 ACCEPTED", "amber"),
        "completed": ("✅ COMPLETED", "blue"),
        "expired": ("🔴 EXPIRED", "red"),
    }
    label, css = values.get(status, (str(status).upper(), "blue"))
    return f'<span class="badge {css}">{label}</span>'


def show_qr(token):
    if not token:
        st.warning("No pickup token was generated.")
        return
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.QRCode(version=1, box_size=8, border=4)
        qr.add_data(token)
        qr.make(fit=True)
        image = qr.make_image()
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        st.image(buffer.getvalue(), width=240)
    except ImportError:
        st.info("For a real scannable QR image, install: pip install qrcode[pil]")
    st.code(token, language=None)


def render_impact_strip():
    items = [
        ("🍽", "Restaurants", "List surplus food easily and quickly."),
        ("↔", "NGOs", "Receive food alerts and collect nearby."),
        ("♧", "Communities", "Food reaches people who need it most."),
        ("🌿", "Less Waste", "A step towards a healthier planet."),
    ]
    markup = '<div class="impact-strip"><div class="impact-grid">'
    for icon, title, description in items:
        markup += f'<div class="impact-item"><div class="impact-icon">{icon}</div><strong>{title}</strong><span>{description}</span></div>'
    st.markdown(markup + '</div></div>', unsafe_allow_html=True)


def render_food_listing(donation, image_url, title=None):
    food_name = title or ("Veg Food Donation" if donation.get("food_type") == "veg" else "Fresh Food Donation")
    donor = donation.get("donor_name", "Local restaurant")
    quantity = donation.get("quantity_desc", "Ready to share")
    deadline = donation.get("pickup_deadline", "Today")
    st.markdown(
        f'<div class="food-row"><img class="food-image" src="{image_url}" alt="Food listing">'
        f'<div><div class="food-name">{food_name}</div><div class="food-meta">🏪 {donor}<br>📦 {quantity} &nbsp; • &nbsp; ⏰ {deadline[:16].replace("T", ", ")}</div></div>'
        f'<div><span class="badge green">Available</span><br><span class="food-action">View Details</span></div></div>',
        unsafe_allow_html=True,
    )


def render_activity_panel(donations):
    activities = []
    for donation in donations[:3]:
        activities.append(("🍽", donation.get("donor_name", "Restaurant"), f'listed {donation.get("quantity_desc", "food")}'))
    activities.extend([
        ("▣", "Hope Foundation", "requested food from a restaurant"),
        ("✓", "Food collected", "pickup successfully completed"),
    ])
    markup = '<div class="panel"><div class="panel-heading">Recent Activity</div>'
    for icon, title, detail in activities[:4]:
        markup += f'<div class="activity-item"><div class="activity-icon">{icon}</div><div class="activity-copy"><strong>{title}</strong>{detail}<br><span>Recently</span></div></div>'
    st.markdown(markup + '</div>', unsafe_allow_html=True)


# ============================================================
# TOP NAVIGATION
# ============================================================
nav_left, nav_center, nav_right = st.columns([1.4, 4.5, 1.1], vertical_alignment="center")
with nav_left:
    st.markdown(
        '<div class="topbar"><div class="top-brand"><div class="mark">🌿</div><div><div class="name">FoodConnect</div><div class="tagline">Good Food • Less Waste • More Hope</div></div></div></div>',
        unsafe_allow_html=True,
    )
with nav_center:
    page = st.radio(
        "Navigate",
        [
            "Home",
            "Donate Food",
            "Register NGO",
            "NGO Directory",
            "NGO Pickup",
            "Donation History",
            "Analytics",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )
with nav_right:
    if st.button("↻ Refresh", width="stretch"):
        st.rerun()

# ============================================================
# HERO
# ============================================================
st.markdown(
    """
    <div class="hero">
        <div>
            <h1>Connecting Restaurants<br>with NGOs to <em>End Food Waste</em></h1>
            <p>Surplus food from your restaurant can bring smiles to those in need. Together, we can feed more and waste less.</p>
            <div class="hero-actions"><span class="hero-pill">🍴 I'm a Restaurant</span><span class="hero-pill secondary">♟ I'm an NGO</span></div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)
render_impact_strip()

# ============================================================
# PAGES
# ============================================================

if page == "Home":
    purpose_card(
        "This is your home screen. It shows how many donations are open, accepted, or "
        "completed right now, and gives you one-click shortcuts to every other page."
    )
    st.markdown(
        '<div class="dashboard-intro"><strong>Welcome to FoodConnect!</strong><span>Here is what is happening across your food rescue network today.</span></div>',
        unsafe_allow_html=True,
    )
    page_header("Dashboard", "Good food, less waste, more hope.")
    a = analytics()
    ngos = load_ngos()
    donations = load_donations()
    rescued = sum(str(d.get("quantity_desc", "")).lower().count("kg") for d in donations if d.get("status") == "completed")
    kpis = [
        ("🍴", a.get("open", 0), "Food Listings", "#e7f7ef"),
        ("♧", len(ngos), "NGOs Connected", "#eaf4fc"),
        ("♨", f'{a.get("completed", 0) * 20}+', "Meals Shared", "#fff7e5"),
        ("🌿", f'{rescued or a.get("completed", 0) * 30} kg', "Food Rescued", "#eef8f1"),
    ]
    kpi_markup = '<div class="kpi-grid">'
    for icon, value, label, color in kpis:
        kpi_markup += f'<div class="custom-kpi" style="background:{color}"><div class="kpi-icon">{icon}</div><div><strong>{value}</strong><span>{label}</span></div></div>'
    st.markdown(kpi_markup + '</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">⚡ Quick Actions</div>', unsafe_allow_html=True)
    q1, q2, q3 = st.columns(3)
    with q1:
        st.markdown('<div class="card workflow-card"><div class="card-title">🍱 Donate Food</div><div class="helper-text">Post surplus food and find suitable nearby NGOs.</div></div>', unsafe_allow_html=True)
    with q2:
        st.markdown('<div class="card workflow-card"><div class="card-title">🏢 Register NGO</div><div class="helper-text">Add NGO location, capacity, vehicle and response information.</div></div>', unsafe_allow_html=True)
    with q3:
        st.markdown('<div class="card workflow-card"><div class="card-title">🚚 Pickup Food</div><div class="helper-text">View open donations, accept pickups and confirm collection.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">🔄 How FoodConnect Works</div>', unsafe_allow_html=True)
    steps = [("1️⃣", "Donate", "Donor posts surplus food."), ("2️⃣", "Match", "Nearby eligible NGOs are identified."), ("3️⃣", "Accept", "An NGO accepts a suitable pickup."), ("4️⃣", "Complete", "Pickup is confirmed.")]
    cols = st.columns(4)
    for col, (num, title, desc) in zip(cols, steps):
        with col:
            st.markdown(f'<div class="card workflow-card"><div style="font-size:1.6rem">{num}</div><div class="card-title">{title}</div><div class="helper-text">{desc}</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">Today at FoodConnect</div>', unsafe_allow_html=True)
    recent = sorted(donations, key=lambda x: x.get("created_at", ""), reverse=True)
    food_images = [
        "https://images.unsplash.com/photo-1603133872878-684f208fb84b?auto=format&fit=crop&w=160&q=80",
        "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=160&q=80",
        "https://images.unsplash.com/photo-1617692855027-33b14f061079?auto=format&fit=crop&w=160&q=80",
    ]
    listing_markup = '<div class="panel"><div class="panel-heading">Recently Available Food <span class="panel-link">View All →</span></div>'
    for index, donation in enumerate(recent[:3]):
        food_name = ["Veg Fried Rice", "Paneer Curry", "Butter Naan"][index]
        listing_markup += f'<div class="food-row"><img class="food-image" src="{food_images[index]}" alt="{food_name}"><div><div class="food-name">{food_name}</div><div class="food-meta">🏪 {donation.get("donor_name", "Local restaurant")}<br>📦 {donation.get("quantity_desc", "Ready to share")} &nbsp; • &nbsp; 📍 Nearby</div></div><div><span class="badge green">Available</span><br><span class="food-action">View Details</span></div></div>'
    if not recent:
        listing_markup += '<div class="helper-text">No food listings yet. Your next donation can help a community.</div>'
    st.markdown(listing_markup + '</div>', unsafe_allow_html=True)
    map_col, activity_col = st.columns([1.4, .8])
    with map_col:
        st.markdown('<div class="panel-heading" style="margin-top:.8rem">Nearby Restaurants <span class="panel-link">View Map →</span></div>', unsafe_allow_html=True)
        points = [{"lat": n["lat"], "lon": n["lng"]} for n in ngos if n.get("lat") is not None and n.get("lng") is not None]
        if points:
            st.map(pd.DataFrame(points), width="stretch", height=270)
        else:
            st.info("No restaurant or NGO locations are available yet.")
    with activity_col:
        st.markdown('<div style="margin-top:.8rem"></div>', unsafe_allow_html=True)
        render_activity_panel(recent)

elif page == "Donate Food":
    purpose_card(
        "Use this form if you have surplus food to give away. Fill in your details and the "
        "pickup timing, and FoodConnect will instantly show you the nearest NGOs able to collect it."
    )
    page_header("🍱 Donate Surplus Food", "Provide the food details and pickup timing.")
    with st.form("donation_form", clear_on_submit=False):
        st.markdown('<div class="subsection-title">👤 Donor Information</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            donor_name = st.text_input(
                "Donor Name", value="Sharma Wedding Hall",
                help="Type the name of the person, venue, or business donating the food.",
            )
        with c2:
            donor_phone = st.text_input(
                "Donor Phone", value="+91 9876543210",
                help="A phone number the NGO can call to coordinate pickup.",
            )

        st.markdown('<div class="subsection-title">📍 Pickup Location</div>', unsafe_allow_html=True)
        location_text = st.text_input(
            "Location", value="Andheri West, Mumbai",
            help="The address or area name where the food should be picked up from.",
        )
        c1, c2 = st.columns(2)
        with c1:
            lat = st.number_input(
                "Latitude", value=19.070000, format="%.6f",
                help="GPS latitude of the pickup point. Leave the default if unsure — it's a real Mumbai coordinate for testing.",
            )
        with c2:
            lng = st.number_input(
                "Longitude", value=72.880000, format="%.6f",
                help="GPS longitude of the pickup point. Leave the default if unsure.",
            )

        st.markdown('<div class="subsection-title">🍱 Food Details</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            food_type = st.selectbox(
                "Food Type", ["veg", "non-veg"],
                help="Choose whether the surplus food is vegetarian or non-vegetarian.",
            )
        with c2:
            quantity = st.text_input(
                "Quantity", value="500 plates",
                help="A rough estimate of how much food there is, e.g. '500 plates' or '50 kg'.",
            )

        st.markdown('<div class="subsection-title">⏰ Pickup Timing</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            cooked_date = st.date_input("Cooked Date", value=date.today(), help="The date the food was prepared.")
            cooked_time = st.time_input("Cooked Time", value=time(18, 0), format="12h", help="The time the food was prepared.")
        with c2:
            deadline_date = st.date_input("Pickup Deadline Date", value=date.today(), help="The last date this food is safe to be picked up.")
            deadline_time = st.time_input("Pickup Deadline Time", value=time(21, 0), format="12h", help="The last time this food is safe to be picked up. Must be after the cooked time.")

        uploaded_photo = st.file_uploader("Food Photo", type=["png", "jpg", "jpeg"], help="Optional photo for the food listing.")
        notes = st.text_area(
            "📝 Notes", value="Food is packed and ready. Enter through Gate 2.",
            help="Anything the pickup team should know — entry instructions, contact person, container details.",
        )
        submitted = st.form_submit_button("🚀 Post Food Donation", width="stretch")

    if submitted:
        if not donor_name.strip():
            st.error("Please enter the donor name.")
        elif not donor_phone.strip():
            st.error("Please enter the donor phone number.")
        elif not location_text.strip():
            st.error("Please enter the pickup location.")
        elif not quantity.strip():
            st.error("Please enter the food quantity.")
        else:
            cooked_dt = datetime.combine(cooked_date, cooked_time)
            deadline_dt = datetime.combine(deadline_date, deadline_time)
            if deadline_dt <= cooked_dt:
                st.error("Pickup deadline must be after cooked time.")
            else:
                payload = {
                    "donor_name": donor_name.strip(),
                    "donor_phone": donor_phone.strip(),
                    "location_text": location_text.strip(),
                    "lat": lat,
                    "lng": lng,
                    "food_type": food_type,
                    "quantity_desc": quantity.strip(),
                    "cooked_time": cooked_dt.isoformat(),
                    "pickup_deadline": deadline_dt.isoformat(),
                    "notes": notes.strip() + (f" Photo: {uploaded_photo.name}" if uploaded_photo else ""),
                }
                code, result = api_post("/api/donations", payload)
                if code == 201:
                    st.success("🎉 Food donation posted successfully!")
                    d = result.get("donation", {})
                    if d:
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Donation ID", d.get("id", "-"))
                        c2.metric("Food Type", str(d.get("food_type", "-")).upper())
                        c3.metric("Quantity", d.get("quantity_desc", "-"))
                    st.markdown('<div class="section-title">🏢 Recommended NGOs</div>', unsafe_allow_html=True)
                    matches = result.get("notify", [])
                    if matches:
                        for rank, match in enumerate(matches, start=1):
                            ngo = match["ngo"]
                            st.markdown(
                                f'<div class="ngo-card"><div class="card-title">#{rank} {ngo.get("name", "NGO")}</div>'
                                f'<div class="helper-text">📍 {match.get("distance_km", "-")} km away &nbsp; • &nbsp; 📞 {ngo.get("phone", "-")}</div>'
                                f'<div><span class="badge green">Capacity: {ngo.get("capacity", 0)}</span>'
                                f'<span class="badge blue">Response: {ngo.get("avg_response_minutes", "-")} min</span></div></div>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.warning("No eligible NGOs were found for this donation.")
                else:
                    st.error(f"Donation failed: {result}")

elif page == "Register NGO":
    purpose_card(
        "Add a new NGO to the network here. Once registered, this NGO becomes eligible to "
        "receive donation matches based on its location, vehicle availability, and capacity."
    )
    page_header("🏢 Register NGO", "Add an NGO to the FoodConnect network.")
    with st.form("ngo_form", clear_on_submit=False):
        st.markdown('<div class="subsection-title">🏢 Organization Information</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("NGO Name", value="Helping Hands", help="The official name of the organization.")
        with c2:
            phone = st.text_input("Phone", value="+91 9800000001", help="A contact number donors or admins can reach the NGO on.")
        st.markdown('<div class="subsection-title">📍 NGO Location</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            lat = st.number_input("Latitude", value=19.076000, format="%.6f", help="GPS latitude of the NGO's base location.")
        with c2:
            lng = st.number_input("Longitude", value=72.877700, format="%.6f", help="GPS longitude of the NGO's base location.")
        st.markdown('<div class="subsection-title">🚚 Pickup Capacity</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            vehicle = st.checkbox("🚚 Vehicle Available", value=True, help="Tick this if the NGO currently has a vehicle free to collect donations.")
        with c2:
            capacity = st.number_input("Available Capacity", min_value=0, value=100, help="How many meals/plates worth of food this NGO can still collect today.")
        response_time = st.number_input("Average Response Time (minutes)", min_value=0, value=20, help="How quickly this NGO typically responds to a pickup request, in minutes.")
        verified = st.checkbox("✅ Verified NGO (demo)", value=True, help="Only verified NGOs are matched to donations. Leave ticked for this demo.")
        submitted = st.form_submit_button("🏢 Register NGO", width="stretch")

    if submitted:
        if not name.strip():
            st.error("Please enter the NGO name.")
        elif not phone.strip():
            st.error("Please enter the NGO phone.")
        else:
            payload = {
                "name": name.strip(),
                "phone": phone.strip(),
                "lat": lat,
                "lng": lng,
                "vehicle_available": vehicle,
                "capacity": capacity,
                "avg_response_minutes": response_time,
                "verified": verified,
            }
            code, result = api_post("/api/ngos", payload)
            if code == 201:
                st.success("🎉 NGO registered successfully!")
                c1, c2, c3 = st.columns(3)
                c1.metric("NGO ID", result.get("id", "-"))
                c2.metric("Capacity", result.get("capacity", 0))
                c3.metric("Response", f'{result.get("avg_response_minutes", "-")} min')
            else:
                st.error(f"Registration failed: {result}")

elif page == "NGO Directory":
    purpose_card(
        "Browse every NGO currently registered in FoodConnect. Use the search box to quickly "
        "find a specific organization by name."
    )
    page_header("🏢 NGO Directory", "Browse the current FoodConnect NGO network.")
    ngos = load_ngos()
    if not ngos:
        st.info("No NGOs are registered yet.")
    else:
        verified = sum(1 for n in ngos if n.get("verified"))
        vehicle_count = sum(1 for n in ngos if n.get("vehicle_available"))
        c1, c2, c3 = st.columns(3)
        c1.metric("Total NGOs", len(ngos))
        c2.metric("Verified NGOs", verified)
        c3.metric("Vehicle Available", vehicle_count)
        st.markdown("---")
        search = st.text_input("🔎 Search NGO", value="", placeholder="Type an NGO name, e.g. Helping Hands", help="Filters the list below as you type.")
        filtered = [n for n in ngos if not search.strip() or search.lower() in n.get("name", "").lower()]
        if not filtered:
            st.info("No NGOs match your search.")
        else:
            for i in range(0, len(filtered), 2):
                cols = st.columns(2)
                for col, ngo in zip(cols, filtered[i:i + 2]):
                    v = '<span class="badge green">✅ Verified</span>' if ngo.get("verified") else '<span class="badge red">⚠️ Not Verified</span>'
                    vehicle = '<span class="badge blue">🚚 Vehicle</span>' if ngo.get("vehicle_available") else '<span class="badge amber">🚫 No Vehicle</span>'
                    with col:
                        st.markdown(
                            f'<div class="ngo-card"><div class="card-title">🏢 {ngo.get("name", "Unknown NGO")}</div>'
                            f'<div class="helper-text">📞 {ngo.get("phone", "-")}</div><div>{v}{vehicle}</div>'
                            f'<div class="helper-text">📦 Capacity: <b>{ngo.get("capacity", 0)}</b></div>'
                            f'<div class="helper-text">⏱️ Avg response: <b>{ngo.get("avg_response_minutes", "-")} min</b></div>'
                            f'<div class="helper-text">📍 {ngo.get("lat", "-")}, {ngo.get("lng", "-")}</div></div>',
                            unsafe_allow_html=True,
                        )

elif page == "NGO Pickup":
    purpose_card(
        "This is the working screen for NGO staff. Pick your NGO, review open donations nearby, "
        "accept one to collect, then confirm the handoff using the pickup token."
    )
    page_header("🚚 NGO Pickup Dashboard", "Select an NGO, review open donations and manage the pickup flow.")
    ngos = load_ngos()
    if not ngos:
        st.warning("No NGOs are registered yet. Register an NGO first.")
    else:
        options = {f'{n["name"]} — ID {n["id"]}': n["id"] for n in ngos}
        selected_label = st.selectbox("🏢 Select NGO", list(options.keys()), help="Choose which NGO you're acting as for this pickup session.")
        selected_ngo_id = options[selected_label]
        st.session_state.selected_ngo_id = selected_ngo_id
        selected_ngo = next(n for n in ngos if n["id"] == selected_ngo_id)
        st.markdown(
            f'<div class="ngo-card"><div class="card-title">🏢 {selected_ngo.get("name", "NGO")}</div>'
            f'<div class="helper-text">📦 Capacity: <b>{selected_ngo.get("capacity", 0)}</b> &nbsp; • &nbsp; '
            f'🚚 Vehicle: <b>{"Available" if selected_ngo.get("vehicle_available") else "Not Available"}</b> &nbsp; • &nbsp; '
            f'⏱️ Response: <b>{selected_ngo.get("avg_response_minutes", "-")} min</b></div></div>',
            unsafe_allow_html=True,
        )

        if st.session_state.accepted_donation:
            accepted = st.session_state.accepted_donation
            st.markdown('<div class="section-title">🔐 Active Pickup</div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f'<div class="card"><div class="card-title">🍱 Pickup Details</div>'
                    f'<div class="helper-text"><b>Donor:</b> {accepted.get("donor_name", "-")}<br>'
                    f'<b>Location:</b> {accepted.get("location_text", "-")}<br>'
                    f'<b>Quantity:</b> {accepted.get("quantity_desc", "-")}<br>'
                    f'<b>Phone:</b> {accepted.get("donor_phone", "-")}</div></div>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown('<div class="card"><div class="card-title">🔑 Pickup QR</div><div class="helper-text">Scan or use the token to confirm handoff.</div></div>', unsafe_allow_html=True)
                show_qr(accepted.get("qr_token"))

            entered = st.text_input(
                "Enter pickup token to confirm", type="password",
                help="Paste the QR token shown above (or scanned from the code) to confirm this donation was picked up.",
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Confirm Pickup", width="stretch"):
                    code, result = api_post(f'/api/donations/{accepted["id"]}/confirm-pickup', {"qr_token": entered})
                    if code == 200:
                        st.success("🎉 Pickup confirmed successfully!")
                        st.session_state.accepted_donation = None
                        st.rerun()
                    else:
                        st.error(result)
            with c2:
                if st.button("❌ Clear Active Pickup", width="stretch"):
                    st.session_state.accepted_donation = None
                    st.rerun()

        st.markdown('<div class="section-title">🍱 Available Donations</div>', unsafe_allow_html=True)
        open_donations = load_donations("open")
        if not open_donations:
            st.success("🎉 No open donations are currently waiting for pickup.")
        else:
            st.caption(f"{len(open_donations)} open donation(s) available")
            for donation in open_donations:
                st.markdown('<div class="donation-card">', unsafe_allow_html=True)
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f'### 🍱 {donation.get("donor_name", "Unknown donor")}')
                    st.write(f'📍 **Location:** {donation.get("location_text", "-")}')
                    st.write(f'📞 **Phone:** {donation.get("donor_phone", "-")}')
                    st.write(f'🥗 **Food:** {str(donation.get("food_type", "-")).upper()}')
                    st.write(f'📦 **Quantity:** {donation.get("quantity_desc", "-")}')
                    st.write(f'⏰ **Deadline:** {donation.get("pickup_deadline", "-")}')
                    if donation.get("notes"):
                        st.write(f'📝 **Notes:** {donation.get("notes")}')
                with c2:
                    st.metric("Donation ID", donation.get("id", "-"))
                    if st.button("✅ Accept & Pick Up", key=f'accept_{donation["id"]}', width="stretch"):
                        code, result = api_post(
                            f'/api/donations/{donation["id"]}/accept',
                            {"ngo_id": selected_ngo_id, "qr_token": donation.get("qr_token")},
                        )
                        if code == 200:
                            if not result.get("qr_token"):
                                _, refreshed = api_get(f'/api/donations/{donation["id"]}')
                                result["qr_token"] = (refreshed or {}).get("qr_token")
                            st.session_state.accepted_donation = result
                            st.success("Donation accepted!")
                            st.rerun()
                        else:
                            st.error(result)
                st.markdown('</div>', unsafe_allow_html=True)

elif page == "Donation History":
    purpose_card(
        "A searchable log of every donation ever posted, so you can look back at what's been "
        "given, accepted, and completed over time."
    )
    page_header("📋 Donation History", "Browse donations and filter by current status.")
    choice = st.selectbox(
        "Filter", ["All", "Open", "Accepted", "Completed"],
        help="Narrow the list down to only donations in a particular state.",
    )
    api_filter = {"All": None, "Open": "open", "Accepted": "accepted", "Completed": "completed"}[choice]
    donations = load_donations(api_filter)
    if not donations:
        st.info("No donations found for the selected filter.")
    else:
        for d in donations:
            st.markdown(
                f'<div class="donation-card"><div class="card-title">🍱 {d.get("donor_name", "Unknown donor")}</div>'
                f'<div>{status_badge(d.get("status", "unknown"))}</div>'
                f'<div class="helper-text"><b>Donation ID:</b> {d.get("id", "-")}<br>'
                f'<b>Location:</b> {d.get("location_text", "-")}<br>'
                f'<b>Food:</b> {d.get("food_type", "-")}<br>'
                f'<b>Quantity:</b> {d.get("quantity_desc", "-")}<br>'
                f'<b>Pickup deadline:</b> {d.get("pickup_deadline", "-")}<br>'
                f'<b>Accepted NGO:</b> {d.get("accepted_by_ngo_name") or "Not assigned"}</div></div>',
                unsafe_allow_html=True,
            )

elif page == "Analytics":
    purpose_card(
        "See how FoodConnect is performing overall — how many donations were completed versus "
        "still open, and the platform's overall completion rate."
    )
    page_header("📊 Analytics", "A clear view of FoodConnect donation performance.")
    a = analytics()
    total = int(a.get("total_donations", 0) or 0)
    open_count = int(a.get("open", 0) or 0)
    accepted_count = int(a.get("accepted", 0) or 0)
    completed_count = int(a.get("completed", 0) or 0)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🍱 Total", total)
    c2.metric("🟢 Open", open_count)
    c3.metric("🟡 Accepted", accepted_count)
    c4.metric("✅ Completed", completed_count)
    rate = completed_count / total if total else 0
    st.markdown('<div class="section-title">🎯 Completion Rate</div>', unsafe_allow_html=True)
    st.progress(rate)
    st.write(f"**{rate * 100:.1f}%** of recorded donations have been completed.")
    st.markdown('<div class="section-title">📊 Status Distribution</div>', unsafe_allow_html=True)
    chart = pd.DataFrame({"Status": ["Open", "Accepted", "Completed"], "Donations": [open_count, accepted_count, completed_count]})
    st.bar_chart(chart.set_index("Status"), width="stretch")

st.markdown(
    '<div class="footer">🌿 <b>FoodConnect</b> — Good Food • Less Waste • More Hope.<br>SPM Project Prototype</div>',
    unsafe_allow_html=True,
)

