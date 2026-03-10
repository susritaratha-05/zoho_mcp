"""
frontend/streamlit.py
=====================
PD HR Chatbot — Qwery-style UI
Dark magenta sidebar · Workspace selector · Centered chat · Search bar with mic
"""

import os
import sys
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests
import streamlit as st
from utils.config import settings

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PD HR Support",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE       = settings.fastapi_url
ALLOWED_DOMAIN = settings.allowed_domain

# ── Global CSS — Qwery style ──────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Syne:wght@700;800&display=swap');

/* ── Reset & base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #f7f7f8 !important;
    font-family: 'DM Sans', sans-serif;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="collapsedControl"] { display: none !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #c0155a !important;
    width: 260px !important;
    min-width: 260px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

/* ── Logo bar ── */
.pd-logo-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 18px 20px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.15);
}
.pd-logo-icon {
    width: 36px; height: 36px;
    background: #1a1a2e;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; font-weight: 800; color: #fff;
    font-family: 'Syne', sans-serif;
    letter-spacing: -1px;
}
.pd-logo-text {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem; font-weight: 800;
    color: #fff; letter-spacing: 0.5px;
}

/* ── Sidebar nav items ── */
.pd-nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 11px 20px;
    color: rgba(255,255,255,0.85);
    font-size: 0.88rem; font-weight: 500;
    cursor: pointer;
    border-radius: 8px;
    margin: 2px 10px;
    transition: background 0.15s;
    text-decoration: none;
}
.pd-nav-item:hover { background: rgba(255,255,255,0.12); }
.pd-nav-item.active {
    background: rgba(255,255,255,0.18);
    color: #fff; font-weight: 600;
}
.pd-nav-icon { font-size: 1rem; width: 20px; text-align: center; }

/* ── Sidebar section label ── */
.pd-section-label {
    font-size: 0.7rem; font-weight: 600;
    color: rgba(255,255,255,0.5);
    text-transform: uppercase; letter-spacing: 1.2px;
    padding: 14px 20px 6px;
}

/* ── Workspace item ── */
.pd-workspace {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 20px;
    margin: 2px 10px;
    border-radius: 8px;
    color: rgba(255,255,255,0.85);
    font-size: 0.85rem; cursor: pointer;
    transition: background 0.15s;
    border: 1px solid rgba(255,255,255,0.2);
}
.pd-workspace:hover { background: rgba(255,255,255,0.1); }
.pd-workspace-icon {
    width: 28px; height: 28px;
    background: rgba(255,255,255,0.2);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem;
}

/* ── User profile bottom ── */
.pd-user-bar {
    margin-top: auto;
    padding: 14px 20px;
    border-top: 1px solid rgba(255,255,255,0.15);
    display: flex; align-items: center; gap: 10px;
}
.pd-avatar {
    width: 34px; height: 34px;
    background: #1a1a2e;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem; font-weight: 700; color: #fff;
    flex-shrink: 0;
}
.pd-user-name {
    color: #fff; font-size: 0.88rem; font-weight: 600; flex: 1;
}
.pd-user-menu { color: rgba(255,255,255,0.6); font-size: 1rem; cursor: pointer; }

/* ── Main content ── */
[data-testid="stMain"], .main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
.block-container { padding: 0 !important; }

/* ── Chat area ── */
.pd-chat-area {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px 120px;
    background: #f7f7f8;
}

/* ── Hero ── */
.pd-hero { text-align: center; margin-bottom: 32px; }
.pd-hero-logo {
    width: 80px; height: 80px;
    background: #1a7a4a;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 2.2rem;
    margin: 0 auto 18px;
    box-shadow: 0 4px 20px rgba(26,122,74,0.3);
}
.pd-hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.7rem; font-weight: 800;
    color: #1a1a2e; margin-bottom: 8px;
}
.pd-hero-sub {
    font-size: 0.92rem; color: #666;
    max-width: 480px; line-height: 1.5;
}
.pd-greeting {
    margin-top: 28px;
    font-size: 1.05rem; color: #333;
    font-weight: 500; line-height: 1.7;
}

/* ── Search bar ── */
.pd-search-wrap {
    width: 100%; max-width: 680px;
    position: relative; margin-top: 32px;
}
.pd-search-bar {
    width: 100%;
    padding: 18px 60px 18px 22px;
    border: 1.5px solid #e0e0e0;
    border-radius: 14px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem; color: #333;
    background: #fff;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
}
.pd-search-bar:focus {
    border-color: #c0155a;
    box-shadow: 0 2px 18px rgba(192,21,90,0.12);
}
.pd-mic-btn {
    position: absolute; right: 10px; top: 50%;
    transform: translateY(-50%);
    width: 40px; height: 40px;
    background: #c0155a;
    border: none; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer; color: #fff; font-size: 1rem;
    transition: background 0.15s;
}
.pd-mic-btn:hover { background: #a01048; }

/* ── Disclaimer ── */
.pd-disclaimer {
    margin-top: 14px;
    font-size: 0.75rem; color: #999;
    text-align: center; max-width: 600px;
}

/* ── Chat messages ── */
.pd-messages { width: 100%; max-width: 680px; margin-bottom: 20px; }
.pd-msg { display: flex; gap: 12px; margin-bottom: 18px; align-items: flex-start; }
.pd-msg.user { flex-direction: row-reverse; }
.pd-msg-avatar {
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.8rem; font-weight: 700; flex-shrink: 0;
}
.pd-msg-avatar.bot { background: #1a7a4a; color: #fff; }
.pd-msg-avatar.usr { background: #c0155a; color: #fff; }
.pd-msg-bubble {
    max-width: 78%;
    padding: 12px 16px;
    border-radius: 14px;
    font-size: 0.9rem; line-height: 1.6; color: #1a1a2e;
}
.pd-msg-bubble.bot { background: #fff; box-shadow: 0 1px 6px rgba(0,0,0,0.07); border-radius: 4px 14px 14px 14px; }
.pd-msg-bubble.usr { background: #c0155a; color: #fff; border-radius: 14px 4px 14px 14px; }

/* ── Login overlay ── */
.pd-login-card {
    background: #fff;
    border-radius: 18px;
    padding: 40px 36px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.1);
    width: 100%; max-width: 420px;
    text-align: center;
}
.pd-login-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.4rem; font-weight: 800;
    color: #1a1a2e; margin-bottom: 6px;
}
.pd-login-sub { font-size: 0.85rem; color: #888; margin-bottom: 28px; }

/* ── Streamlit widget overrides ── */
.stTextInput input, .stTextInput input:focus {
    border: 1.5px solid #e0e0e0 !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    padding: 10px 14px !important;
    box-shadow: none !important;
    color: #1a1a2e !important;
    background: #fafafa !important;
}
.stTextInput input:focus { border-color: #c0155a !important; }
.stButton button {
    background: #c0155a !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 10px 20px !important;
    transition: background 0.15s !important;
}
.stButton button:hover { background: #a01048 !important; }
.stSpinner > div { border-top-color: #c0155a !important; }
</style>
""", unsafe_allow_html=True)


# ── Session defaults ──────────────────────────────────────────────────────────
for k, v in {
    "logged_in":    False,
    "user_email":   "",
    "user_name":    "",
    "access_token": "",
    "employee_id":  "",
    "messages":     [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo
    st.markdown("""
    <div class="pd-logo-bar">
        <div class="pd-logo-icon">PD</div>
        <div class="pd-logo-text">PRODEVANS</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # Nav
    st.markdown("""
    <div class="pd-nav-item active">
        <span class="pd-nav-icon">💬</span> PD HR Support
    </div>
    """, unsafe_allow_html=True)

    # Workspace
    st.markdown('<div class="pd-section-label">Workspace</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="pd-workspace">
        <div class="pd-workspace-icon">⚙️</div>
        <span>Select Workspace</span>
    </div>
    """, unsafe_allow_html=True)

    # User bar
    if st.session_state["logged_in"]:
        initials = "".join(p[0].upper() for p in st.session_state["user_name"].split()[:2])
        name     = st.session_state["user_name"]
        st.markdown(f"""
        <div class="pd-user-bar">
            <div class="pd-avatar">{initials}</div>
            <div class="pd-user-name">{name}</div>
            <div class="pd-user-menu">⋮</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🚪 Logout", use_container_width=True):
            for k in ["logged_in","user_email","user_name","access_token","employee_id","messages"]:
                st.session_state[k] = "" if k != "messages" and k != "logged_in" else ([] if k == "messages" else False)
            st.rerun()
    else:
        st.markdown("""
        <div class="pd-user-bar">
            <div class="pd-avatar">?</div>
            <div class="pd-user-name">Not logged in</div>
        </div>
        """, unsafe_allow_html=True)



# LOGIN SCREEN

DOMAIN = "prodevans.com"   # hardcoded to avoid any env-loading race condition

if not st.session_state["logged_in"]:
    st.markdown('<div class="pd-chat-area">', unsafe_allow_html=True)

    st.markdown("""
    <div class="pd-hero">
        <div class="pd-hero-logo">📖</div>
        <div class="pd-hero-title">PD HR Support</div>
        <div class="pd-hero-sub">Sign in with your Prodevans email to access the HR assistant.</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="pd-login-card">', unsafe_allow_html=True)
        st.markdown('<div class="pd-login-title">Welcome Back</div>', unsafe_allow_html=True)
        st.markdown('<div class="pd-login-sub">Only @prodevans.com accounts are allowed</div>', unsafe_allow_html=True)

        email  = st.text_input("Work Email", placeholder="yourname@prodevans.com", key="inp_email")
        name   = st.text_input("Full Name",  placeholder="e.g. Anjali Mahapatra", key="inp_name")
        token  = st.text_input("Zoho Access Token", placeholder="Paste token here", type="password", key="inp_token")

        if st.button("Login", use_container_width=True):
            # Read directly from widget session state keys
            clean_email = st.session_state.get("inp_email", "").strip().lower()
            clean_name  = st.session_state.get("inp_name",  "").strip()
            clean_token = st.session_state.get("inp_token", "").strip()

            if not clean_email.endswith("@prodevans.com"):
                st.error("Only @prodevans.com accounts are allowed.")
            elif not clean_name:
                st.warning("Please enter your full name.")
            elif not clean_token:
                st.warning("Please paste your Zoho access token.")
            else:
                st.session_state["logged_in"]    = True
                st.session_state["user_email"]   = clean_email
                st.session_state["user_name"]    = clean_name
                st.session_state["access_token"] = clean_token
                st.session_state["messages"]     = []
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CHAT SCREEN
# ══════════════════════════════════════════════════════════════════════════════
first_name = st.session_state["user_name"].split()[0]
has_messages = bool(st.session_state["messages"])

st.markdown('<div class="pd-chat-area">', unsafe_allow_html=True)

# ── Hero (shown when no messages yet) ─────────────────────────────────────────
if not has_messages:
    st.markdown(f"""
    <div class="pd-hero">
        <div class="pd-hero-logo">📖</div>
        <div class="pd-hero-title">PD HR Support</div>
        <div class="pd-hero-sub">
            You can chat about Prodevans HR policies, Organisation's structure etc. in this workspace.
        </div>
        <div class="pd-greeting">Hi, {first_name}!<br>I am your AI assistant. How can I help you today?</div>
    </div>
    """, unsafe_allow_html=True)

# ── Message history ────────────────────────────────────────────────────────────
if has_messages:
    st.markdown('<div class="pd-messages">', unsafe_allow_html=True)
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            initials = "".join(p[0].upper() for p in st.session_state["user_name"].split()[:2])
            st.markdown(f"""
            <div class="pd-msg user">
                <div class="pd-msg-avatar usr">{initials}</div>
                <div class="pd-msg-bubble usr">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="pd-msg">
                <div class="pd-msg-avatar bot">📖</div>
                <div class="pd-msg-bubble bot">{msg["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ── Stream helper ─────────────────────────────────────────────────────────────
def stream_from_api(user_message: str) -> str:
    payload = {
        "employee_email": st.session_state["user_email"],
        "employee_name":  st.session_state["user_name"],
        "employee_id":    st.session_state.get("employee_id", ""),
        "access_token":   st.session_state.get("access_token", ""),
        "conversation":   st.session_state["messages"],
    }
    full_text   = ""
    placeholder = st.empty()
    try:
        with requests.post(
            f"{API_BASE}/chat/stream",
            json=payload, stream=True, timeout=120,
        ) as http_response:
            if http_response.status_code != 200:
                err = f"API error {http_response.status_code}: {http_response.text}"
                placeholder.error(err)
                return err
            for raw_line in http_response.iter_lines():
                if not raw_line:
                    continue
                line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
                if not line.startswith("data: "):
                    continue
                token = line[6:]
                if token == "[DONE]":
                    break
                token = token.replace("\\n", "\n")
                full_text += token
                placeholder.markdown(full_text + "▌")
        placeholder.markdown(full_text if full_text else "Sorry, I couldn\'t get a response. Please try again.")
    except requests.exceptions.ConnectionError:
        full_text = "Could not connect to the HR API. Make sure FastAPI is running on port 8000."
        placeholder.error(full_text)
    except Exception as e:
        full_text = f"Error: {str(e)}"
        placeholder.error(full_text)
    return full_text


# ── Search bar with mic ───────────────────────────────────────────────────────
st.markdown('<div class="pd-search-wrap">', unsafe_allow_html=True)

user_input = st.chat_input("Search here...")

st.markdown("""
<div style="position:relative; margin-top:-52px; pointer-events:none; display:flex; justify-content:flex-end; padding-right:10px;">
    <button class="pd-mic-btn" style="pointer-events:auto;" title="Voice input">🎤</button>
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Disclaimer ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="pd-disclaimer">
    This is Generative AI driven intelligent search. However, hallucination can occur,
    manual verification of results required. Please clear chat for next search.
</div>
""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Handle input ───────────────────────────────────────────────────────────────
if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    reply = stream_from_api(user_input)
    st.session_state["messages"].append({"role": "assistant", "content": reply})
    st.rerun()