import json
import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# 1. Page Configuration
st.set_page_config(
    page_title="Custom ChatGPT - your personal AI studio",
    page_icon="🤖",
    layout="wide"
)

# File path for persistent chat history
HISTORY_FILE = "chat_history.json"


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                chats = {}
                for cid, msgs in data.get("all_chats", {}).items():
                    reconstructed = []
                    for m in msgs:
                        if m["type"] == "system":
                            reconstructed.append(SystemMessage(content=m["content"]))
                        elif m["type"] == "human":
                            reconstructed.append(HumanMessage(content=m["content"]))
                        elif m["type"] == "ai":
                            reconstructed.append(AIMessage(content=m["content"]))
                    chats[cid] = reconstructed
                return chats, data.get("chat_titles", {})
        except Exception:
            pass
    return {}, {}


def save_history():
    data = {"all_chats": {}, "chat_titles": st.session_state.chat_titles}
    for cid, msgs in st.session_state.all_chats.items():
        serialized = []
        for m in msgs:
            if isinstance(m, SystemMessage):
                serialized.append({"type": "system", "content": m.content})
            elif isinstance(m, HumanMessage):
                serialized.append({"type": "human", "content": m.content})
            elif isinstance(m, AIMessage):
                serialized.append({"type": "ai", "content": m.content})
        data["all_chats"][cid] = serialized
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# API Key Verification Function
def verify_api_key(api_key):
    try:
        test_llm = ChatOpenAI(
            model_name="gpt-4o-mini",
            openai_api_key=api_key,
            max_tokens=5
        )
        test_llm.invoke("Hi")
        return True
    except Exception:
        return False


# 2. Session State & Reload Persistence
query_params = st.query_params

if "api_key_valid" not in st.session_state:
    if "key" in query_params and verify_api_key(query_params["key"]):
        st.session_state.user_api_key = query_params["key"]
        st.session_state.api_key_valid = True
    else:
        st.session_state.api_key_valid = False
        st.session_state.user_api_key = ""

# Load persistent chat history from disk
if "history_loaded" not in st.session_state:
    loaded_chats, loaded_titles = load_history()
    st.session_state.all_chats = loaded_chats
    st.session_state.chat_titles = loaded_titles
    st.session_state.history_loaded = True

if not st.session_state.all_chats:
    st.session_state.all_chats["Chat 1"] = []
    st.session_state.chat_titles["Chat 1"] = "New Chat"

if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in st.session_state.all_chats:
    st.session_state.current_chat_id = list(st.session_state.all_chats.keys())[0]

if "system_role" not in st.session_state:
    st.session_state.system_role = "You are a helpful assistant."

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

if "selected_theme" not in st.session_state:
    st.session_state.selected_theme = "🌸 Rose Pastel (Light)"


# Helper function to derive display title
def get_chat_display_title(chat_id):
    title = st.session_state.chat_titles.get(chat_id, "New Chat")
    if title != "New Chat":
        return title
    
    msgs = st.session_state.all_chats.get(chat_id, [])
    for msg in msgs:
        if isinstance(msg, HumanMessage) and msg.content.strip():
            clean_text = msg.content.strip().replace("\n", " ")
            return clean_text[:26] + "..." if len(clean_text) > 26 else clean_text
            
    return chat_id


# 3. Comprehensive Theme Configuration
themes_config = {
    "🌸 Rose Pastel (Light)": {
        "bg": "radial-gradient(circle at 80% 20%, #fde2e4 0%, #f8f0fc 40%, #f3f4f6 100%)",
        "sidebar_bg": "rgba(255, 255, 255, 0.78)",
        "card_bg": "rgba(255, 255, 255, 0.85)",
        "card_border": "rgba(255, 255, 255, 1)",
        "text_main": "#111827",
        "text_sub": "#4b5563",
        "placeholder": "#6b7280",
        "accent_grad": "linear-gradient(270deg, #ec4899, #8b5cf6, #3b82f6, #ec4899)",
        "btn_grad": "linear-gradient(90deg, #8b5cf6 0%, #ec4899 100%)",
        "shadow": "rgba(138, 80, 249, 0.18)",
        "status_bg": "#ffffff",
        "status_border": "#f3f4f6",
        "input_bg": "#ffffff"
    },
    "🌿 Emerald Mint (Light)": {
        "bg": "radial-gradient(circle at 80% 20%, #d1fae5 0%, #e0f2fe 40%, #f0fdf4 100%)",
        "sidebar_bg": "rgba(255, 255, 255, 0.82)",
        "card_bg": "rgba(255, 255, 255, 0.88)",
        "card_border": "rgba(255, 255, 255, 1)",
        "text_main": "#064e3b",
        "text_sub": "#047857",
        "placeholder": "#059669",
        "accent_grad": "linear-gradient(270deg, #10b981, #0284c7, #3b82f6, #10b981)",
        "btn_grad": "linear-gradient(90deg, #059669 0%, #0284c7 100%)",
        "shadow": "rgba(16, 185, 129, 0.20)",
        "status_bg": "#ffffff",
        "status_border": "#e6fffa",
        "input_bg": "#ffffff"
    },
    "🌌 Midnight Violet (Dark)": {
        "bg": "radial-gradient(circle at 80% 20%, #1e1b4b 0%, #0f172a 50%, #020617 100%)",
        "sidebar_bg": "rgba(15, 23, 42, 0.95)",
        "card_bg": "rgba(30, 41, 59, 0.90)",
        "card_border": "rgba(129, 140, 248, 0.5)",
        "text_main": "#ffffff",
        "text_sub": "#cbd5e1",
        "placeholder": "#94a3b8",
        "accent_grad": "linear-gradient(270deg, #a855f7, #ec4899, #6366f1, #a855f7)",
        "btn_grad": "linear-gradient(90deg, #c084fc 0%, #f43f5e 100%)",
        "shadow": "rgba(168, 85, 247, 0.35)",
        "status_bg": "#1e293b",
        "status_border": "#334155",
        "input_bg": "#1e293b"
    },
    "⚡ Cyberpunk Neon (Dark)": {
        "bg": "radial-gradient(circle at 80% 20%, #18002e 0%, #090014 50%, #030008 100%)",
        "sidebar_bg": "rgba(12, 5, 24, 0.95)",
        "card_bg": "rgba(25, 12, 45, 0.92)",
        "card_border": "rgba(0, 240, 255, 0.6)",
        "text_main": "#ffffff",
        "text_sub": "#a7f3d0",
        "placeholder": "#38bdf8",
        "accent_grad": "linear-gradient(270deg, #00f0ff, #ff007f, #7000ff, #00f0ff)",
        "btn_grad": "linear-gradient(90deg, #00f0ff 0%, #d946ef 100%)",
        "shadow": "rgba(0, 240, 255, 0.40)",
        "status_bg": "#190c2d",
        "status_border": "#581c87",
        "input_bg": "#190c2d"
    }
}

current_theme = themes_config[st.session_state.selected_theme]

# CSS Overrides
custom_css = f"""
<style>
    /* App Canvas */
    .stApp {{
        background: {current_theme['bg']} !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        color: {current_theme['text_main']} !important;
    }}

    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Form Container Styling for Landing Auth Card */
    div[data-testid="stForm"] {{
        background: {current_theme['card_bg']} !important;
        border: 1px solid {current_theme['card_border']} !important;
        border-radius: 28px !important;
        padding: 35px 28px 25px 28px !important;
        box-shadow: 0 20px 50px {current_theme['shadow']} !important;
        backdrop-filter: blur(16px) !important;
        margin-top: 20px;
    }}

    .badge-pill-pink {{
        background: {current_theme['status_bg']} !important;
        color: {current_theme['text_main']} !important;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        display: inline-block;
        border: 1px solid {current_theme['card_border']} !important;
    }}

    .card-input-label {{
        text-align: left;
        font-size: 13px;
        font-weight: 600;
        color: {current_theme['text_main']} !important;
        margin-top: 15px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    /* Global Text Rules & Readability Fixes */
    .stApp p, .stApp span, .stApp label, .stApp div[data-testid="stMarkdownContainer"] p,
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp strong, .stApp b, .stApp em {{
        color: {current_theme['text_main']} !important;
    }}

    .stApp ol, .stApp ul, .stApp li,
    div[data-testid="stMarkdownContainer"] ol, 
    div[data-testid="stMarkdownContainer"] ul, 
    div[data-testid="stMarkdownContainer"] li,
    ::marker,
    ol > li::marker,
    ul > li::marker {{
        color: {current_theme['text_main']} !important;
        font-weight: 600 !important;
    }}

    /* Sidebar Base */
    [data-testid="stSidebar"] {{
        background-color: {current_theme['sidebar_bg']} !important;
        backdrop-filter: blur(16px);
        border-right: 1px solid {current_theme['card_border']} !important;
    }}

    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {{
        color: {current_theme['text_main']} !important;
    }}

    /* Universal Input Overrides */
    div[data-baseweb="input"] > div, 
    .stTextInput input, 
    div[data-baseweb="select"] > div {{
        background-color: {current_theme['input_bg']} !important;
        color: {current_theme['text_main']} !important;
        -webkit-text-fill-color: {current_theme['text_main']} !important;
        border: 1px solid {current_theme['card_border']} !important;
        border-radius: 12px !important;
    }}

    /* Placeholder High-Contrast */
    ::placeholder,
    ::-webkit-input-placeholder,
    .stTextInput input::placeholder,
    div[data-testid="stChatInput"] textarea::placeholder,
    div[data-baseweb="input"] input::placeholder {{
        color: {current_theme['placeholder']} !important;
        opacity: 0.95 !important;
        -webkit-text-fill-color: {current_theme['placeholder']} !important;
    }}

    /* Dropdown Menus */
    ul[role="listbox"], div[data-baseweb="popover"], div[data-baseweb="menu"] {{
        background-color: {current_theme['status_bg']} !important;
        border: 1px solid {current_theme['card_border']} !important;
    }}

    li[role="option"] {{
        background-color: {current_theme['status_bg']} !important;
        color: {current_theme['text_main']} !important;
    }}

    li[role="option"]:hover {{
        background-color: {current_theme['card_border']} !important;
    }}

    /* Standard Buttons Overrides */
    .stButton > button {{
        background-color: {current_theme['input_bg']} !important;
        color: {current_theme['text_main']} !important;
        border: 1px solid {current_theme['card_border']} !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
    }}

    .stButton > button:hover {{
        border-color: #ec4899 !important;
        color: #ffffff !important;
    }}

    /* Action Buttons & Form Submit Buttons */
    div[data-testid="stFormSubmitButton"] > button, .sidebar-gradient-btn > button {{
        background: {current_theme['btn_grad']} !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        border: none !important;
        height: 48px !important;
        font-size: 15px !important;
        box-shadow: 0 4px 15px {current_theme['shadow']} !important;
        width: 100% !important;
    }}

    /* Prompt Glass Card Wrapper */
    .prompt-container .stButton > button {{
        background: {current_theme['card_bg']} !important;
        border: 1px solid {current_theme['card_border']} !important;
        border-radius: 24px !important;
        height: 125px !important;
        padding: 20px !important;
        box-shadow: 0 10px 30px {current_theme['shadow']} !important;
        backdrop-filter: blur(14px) !important;
        transition: all 0.35s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
        color: {current_theme['text_main']} !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        white-space: pre-wrap !important;
        width: 100% !important;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    .prompt-container .stButton > button:hover {{
        transform: translateY(-6px) scale(1.02) !important;
        box-shadow: 0 18px 40px {current_theme['shadow']} !important;
        border-color: #ec4899 !important;
    }}

    /* Bottom Chat Area Override */
    footer,
    [data-testid="stBottom"],
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
    }}

    div[data-testid="stChatInput"] {{
        background-color: {current_theme['input_bg']} !important;
        border: 1px solid {current_theme['card_border']} !important;
        border-radius: 18px !important;
        box-shadow: 0 10px 30px {current_theme['shadow']} !important;
    }}

    div[data-testid="stChatInput"] > div,
    div[data-testid="stChatInput"] div[data-baseweb="base-input"] {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
    }}

    div[data-testid="stChatInput"] textarea {{
        color: {current_theme['text_main']} !important;
        -webkit-text-fill-color: {current_theme['text_main']} !important;
        background-color: transparent !important;
    }}

    @keyframes float3D {{
        0%, 100% {{
            transform: translateY(0px) rotateX(0deg) scale(1);
        }}
        50% {{
            transform: translateY(-14px) rotateX(10deg) scale(1.12);
        }}
    }}

    .flying-3d-robot-top {{
        display: flex;
        justify-content: center;
        margin-bottom: 15px;
        animation: float3D 3.5s ease-in-out infinite;
        filter: drop-shadow(0px 14px 22px {current_theme['shadow']});
    }}

    .main-title {{
        text-align: center;
        font-size: 52px;
        font-weight: 800;
        color: {current_theme['text_main']} !important;
        margin-top: 5px;
        margin-bottom: 35px;
        letter-spacing: -1px;
    }}

    .title-pink {{
        color: #ec4899 !important;
        font-style: italic;
        font-weight: 500;
    }}

    .top-right-nav {{
        position: absolute;
        top: -40px;
        right: 10px;
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 14px;
        font-weight: 500;
        color: {current_theme['text_sub']};
    }}

    .status-box {{
        background: {current_theme['status_bg']} !important;
        border-radius: 16px;
        padding: 12px 16px;
        border: 1px solid {current_theme['status_border']} !important;
        margin-top: 15px;
        color: {current_theme['text_main']} !important;
    }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)


# ==========================================
# SCREEN 1: LANDING & API KEY PAGE
# ==========================================
if not st.session_state.api_key_valid:
    st.markdown("<style>[data-testid='stSidebar'] { display: none; }</style>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.8, 1])

    with col2:
        with st.form("auth_form", border=False):
            st.markdown(
                """
                <div class="flying-3d-robot-top">
                    <svg width="75" height="75" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="20" y="25" width="60" height="50" rx="16" fill="url(#bot_body)" />
                        <rect x="28" y="35" width="44" height="28" rx="8" fill="#1E1E2E" />
                        <circle cx="40" cy="49" r="5" fill="#00F0FF" />
                        <circle cx="60" cy="49" r="5" fill="#00F0FF" />
                        <path d="M42 57 Q50 62 58 57" stroke="#00F0FF" stroke-width="3" stroke-linecap="round" fill="none" />
                        <rect x="45" y="10" width="10" height="15" rx="3" fill="url(#bot_body)" />
                        <circle cx="50" cy="9" r="6" fill="#EC4899" />
                        <rect x="10" y="40" width="10" height="20" rx="5" fill="url(#bot_body)" />
                        <rect x="80" y="40" width="10" height="20" rx="5" fill="url(#bot_body)" />
                        <defs>
                            <linearGradient id="bot_body" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
                                <stop stop-color="#8B5CF6"/>
                                <stop offset="1" stop-color="#EC4899"/>
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <h2 style="font-size: 28px; font-weight: 800; margin: 0 0 8px 0; line-height: 1.2; text-align: center;">
                    Welcome to<br>your <span class="sliding-color-text">Custom ChatGPT</span>
                </h2>
                <p style="font-size: 13px; margin-bottom: 20px; opacity: 0.85; text-align: center;">
                    Plug in your OpenAI API key to unlock your personal AI studio.
                </p>
                <div style="display: flex; flex-direction: column; align-items: center; gap: 6px; margin-bottom: 15px;">
                    <span class="badge-pill-pink">⚡ Streaming replies</span>
                    <span class="badge-pill-pink">📁 Saved chats</span>
                    <span class="badge-pill-pink">🎭 Custom persona</span>
                </div>
                <div class="card-input-label">
                    <span>🔑</span> OpenAI API key
                </div>
                """,
                unsafe_allow_html=True
            )

            entered_key = st.text_input(
                "API Key Input",
                type="password",
                placeholder="sk-...",
                label_visibility="collapsed"
            )

            submitted = st.form_submit_button("🚀 Unlock the magic", use_container_width=True)

            st.markdown(
                """
                <div style="text-align: center; margin-top: 15px;" class="security-note">
                    🔒 Your key lives only in this browser session and is never written to disk.<br>
                    Need one? <a href="https://platform.openai.com/api-keys" target="_blank">Get an API key ↗</a>
                </div>
                """,
                unsafe_allow_html=True
            )

            if submitted:
                if entered_key.strip():
                    with st.spinner("Verifying API Key..."):
                        if verify_api_key(entered_key.strip()):
                            key_clean = entered_key.strip()
                            st.session_state.user_api_key = key_clean
                            st.session_state.api_key_valid = True
                            st.query_params["key"] = key_clean
                            st.rerun()
                        else:
                            st.error("❌ Invalid API Key! Please check and try again.")
                else:
                    st.warning("Please enter your OpenAI API key.")


# ==========================================
# SCREEN 2: MAIN PROMPT INTERFACE
# ==========================================
else:
    # Top Right Links
    st.markdown(
        """
        <div class="top-right-nav">
            <span>Fork</span>
            <a href="https://github.com" target="_blank" style="color: inherit;">
                <svg height="20" width="20" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.28.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            </a>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
                <div style="background: linear-gradient(135deg, #f472b6, #e11d48); padding: 10px; border-radius: 14px; color: white;">✨</div>
                <div>
                    <div style="font-weight: 700; font-size: 16px; color: {current_theme['text_main']};">Custom ChatGPT</div>
                    <div style="font-size: 12px; color: {current_theme['text_sub']};">your personal AI studio</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown('<div class="sidebar-gradient-btn">', unsafe_allow_html=True)
        if st.button("✏️ New chat", use_container_width=True):
            new_chat_num = len(st.session_state.all_chats) + 1
            new_chat_id = f"Chat {new_chat_num}"
            st.session_state.all_chats[new_chat_id] = []
            st.session_state.chat_titles[new_chat_id] = "New Chat"
            st.session_state.current_chat_id = new_chat_id
            save_history()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        selected_t = st.selectbox(
            "🎨 Theme",
            options=list(themes_config.keys()),
            index=list(themes_config.keys()).index(st.session_state.selected_theme)
        )
        if selected_t != st.session_state.selected_theme:
            st.session_state.selected_theme = selected_t
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        search_query = st.text_input("Search", placeholder="🔎 Search chats...", label_visibility="collapsed")

        all_chat_ids = list(st.session_state.all_chats.keys())

        # Filter chat IDs by prompt titles or message content
        if search_query.strip():
            q = search_query.strip().lower()
            filtered_chat_ids = []
            for cid in all_chat_ids:
                title = get_chat_display_title(cid).lower()
                msgs = st.session_state.all_chats.get(cid, [])
                content_match = any(q in getattr(m, 'content', '').lower() for m in msgs)
                if q in title or content_match:
                    filtered_chat_ids.append(cid)
        else:
            filtered_chat_ids = all_chat_ids

        if not filtered_chat_ids:
            st.markdown(
                f"""
                <div style="background: rgba(255, 255, 255, 0.08); border: 1px dashed rgba(150, 150, 150, 0.4); border-radius: 16px; padding: 12px; text-align: center; font-size: 13px; margin-top: 10px; color: {current_theme['text_sub']};">
                    🔍 No matching prompts found
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            selected_idx = (
                filtered_chat_ids.index(st.session_state.current_chat_id)
                if st.session_state.current_chat_id in filtered_chat_ids
                else 0
            )

            selected_chat = st.radio(
                "Chats:",
                options=filtered_chat_ids,
                format_func=get_chat_display_title,
                index=selected_idx
            )
            if selected_chat != st.session_state.current_chat_id:
                st.session_state.current_chat_id = selected_chat
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("⚙️ Settings"):
            st.session_state.system_role = st.text_input("System Role", value=st.session_state.system_role)

        masked_key = st.session_state.user_api_key[:5] + "..." + st.session_state.user_api_key[-4:] if len(st.session_state.user_api_key) > 9 else st.session_state.user_api_key
        st.markdown(
            f"""
            <div class="status-box">
                <div style="font-size: 13px; font-weight: 600;">
                    <span style="color: #22c55e;">●</span> Connected to OpenAI
                </div>
                <div style="font-size: 11px; opacity: 0.8; margin-top: 2px;">{masked_key}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Key", use_container_width=True):
                st.session_state.api_key_valid = False
                st.session_state.user_api_key = ""
                st.query_params.clear()
                st.rerun()
        with c2:
            if st.button("🧹 Clear", use_container_width=True):
                st.session_state.all_chats[st.session_state.current_chat_id] = []
                st.session_state.chat_titles[st.session_state.current_chat_id] = "New Chat"
                save_history()
                st.rerun()

    # Main Content
    if st.session_state.current_chat_id not in st.session_state.all_chats:
        st.session_state.all_chats[st.session_state.current_chat_id] = []

    current_messages = st.session_state.all_chats[st.session_state.current_chat_id]

    if st.session_state.system_role:
        if not any(isinstance(x, SystemMessage) for x in current_messages):
            current_messages.insert(0, SystemMessage(content=st.session_state.system_role))
        else:
            current_messages[0] = SystemMessage(content=st.session_state.system_role)

    if len(current_messages) <= 1:
        st.markdown(
            """
            <div class="flying-3d-robot-top">
                <svg width="85" height="85" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="20" y="25" width="60" height="50" rx="16" fill="url(#bot_body_2)" />
                    <rect x="28" y="35" width="44" height="28" rx="8" fill="#1E1E2E" />
                    <circle cx="40" cy="49" r="5" fill="#00F0FF" />
                    <circle cx="60" cy="49" r="5" fill="#00F0FF" />
                    <path d="M42 57 Q50 62 58 57" stroke="#00F0FF" stroke-width="3" stroke-linecap="round" fill="none" />
                    <rect x="45" y="10" width="10" height="15" rx="3" fill="url(#bot_body_2)" />
                    <circle cx="50" cy="9" r="6" fill="#EC4899" />
                    <rect x="10" y="40" width="10" height="20" rx="5" fill="url(#bot_body_2)" />
                    <rect x="80" y="40" width="10" height="20" rx="5" fill="url(#bot_body_2)" />
                    <defs>
                        <linearGradient id="bot_body_2" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#8B5CF6"/>
                            <stop offset="1" stop-color="#EC4899"/>
                        </linearGradient>
                    </defs>
                </svg>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            '<h1 class="main-title">How can I <span class="title-pink">help</span> you today?</h1>',
            unsafe_allow_html=True
        )

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="prompt-container">', unsafe_allow_html=True)
            if st.button("🧠\n\nExplain like I'm five", use_container_width=True, key="p1"):
                st.session_state.pending_prompt = "Explain quantum computing like I'm five."
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="prompt-container">', unsafe_allow_html=True)
            if st.button("🧳\n\nPlan a trip", use_container_width=True, key="p2"):
                st.session_state.pending_prompt = "Plan a 5-day trip to Tokyo."
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="prompt-container">', unsafe_allow_html=True)
            if st.button("✍️\n\nWrite a poem", use_container_width=True, key="p3"):
                st.session_state.pending_prompt = "Write a short inspirational poem about AI."
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown('<div class="prompt-container">', unsafe_allow_html=True)
            if st.button("🐍\n\nLevel up my Python", use_container_width=True, key="p4"):
                st.session_state.pending_prompt = "Give me 3 advanced Python tips for data science."
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div style="text-align: center; font-size: 13px; margin-top: 35px; color: {current_theme['text_sub']};">
                ✨ Custom ChatGPT can make mistakes. Check important info.
            </div>
            """,
            unsafe_allow_html=True
        )

    else:
        for msg in current_messages[1:]:
            if isinstance(msg, HumanMessage):
                with st.chat_message("user"):
                    st.write(msg.content)
            elif isinstance(msg, AIMessage):
                with st.chat_message("assistant"):
                    st.write(msg.content)

    user_prompt = st.chat_input("Message Custom ChatGPT... ✨")

    active_prompt = user_prompt or st.session_state.pending_prompt

    if active_prompt:
        st.session_state.pending_prompt = None

        human_msgs = [m for m in current_messages if isinstance(m, HumanMessage)]
        if len(human_msgs) > 0 and st.session_state.chat_titles.get(st.session_state.current_chat_id) != "New Chat":
            new_chat_num = len(st.session_state.all_chats) + 1
            new_chat_id = f"Chat {new_chat_num}"
            st.session_state.all_chats[new_chat_id] = []
            st.session_state.chat_titles[new_chat_id] = "New Chat"
            st.session_state.current_chat_id = new_chat_id
            current_messages = st.session_state.all_chats[new_chat_id]
            if st.session_state.system_role:
                current_messages.append(SystemMessage(content=st.session_state.system_role))

        clean_prompt = active_prompt.strip().replace("\n", " ")
        title_summary = clean_prompt[:26] + "..." if len(clean_prompt) > 26 else clean_prompt
        st.session_state.chat_titles[st.session_state.current_chat_id] = title_summary

        current_messages.append(HumanMessage(content=active_prompt))

        with st.chat_message("user"):
            st.write(active_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Working..."):
                try:
                    chat = ChatOpenAI(
                        model_name="gpt-4o-mini",
                        temperature=0.5,
                        openai_api_key=st.session_state.user_api_key
                    )
                    response = chat.invoke(current_messages)
                    st.write(response.content)
                    current_messages.append(AIMessage(content=response.content))
                    
                    save_history()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
