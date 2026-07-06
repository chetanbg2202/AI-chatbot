"""
app.py
------
Streamlit UI for the FAQ Chatbot.

Run with:
    streamlit run app.py

Features
--------
* Dark-themed, modern chat interface
* Persistent session-state chat history
* Confidence score badge alongside every bot reply
* Matched FAQ question displayed for transparency
* Debug expander showing top-3 candidate matches
* Intent responses (greetings, thanks, farewells)
* Sidebar with quick example questions
"""

import sys
from pathlib import Path

# Ensure the project root is on the Python path so imports work
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from chatbot import get_response

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="📚 Course Support Chatbot",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS — premium dark glassmorphism theme
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* ---- Google Font ---- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ---- Global reset ---- */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ---- App background ---- */
    .stApp {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        min-height: 100vh;
    }

    /* ---- Sidebar ---- */
    [data-testid="stSidebar"] {
        background: rgba(255,255,255,0.05);
        border-right: 1px solid rgba(255,255,255,0.1);
        backdrop-filter: blur(12px);
    }
    [data-testid="stSidebar"] * { color: #e2e8f0 !important; }

    /* ---- Chat message bubbles ---- */
    .user-bubble {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: #fff;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 6px 0 6px 60px;
        font-size: 0.95rem;
        line-height: 1.5;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
        word-wrap: break-word;
    }

    .bot-bubble {
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.15);
        color: #e2e8f0;
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 6px 60px 6px 0;
        font-size: 0.95rem;
        line-height: 1.6;
        backdrop-filter: blur(8px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        word-wrap: break-word;
    }

    /* ---- Avatars ---- */
    .avatar-user {
        float: right;
        margin: 6px 0 6px 8px;
        font-size: 1.6rem;
    }
    .avatar-bot {
        float: left;
        margin: 6px 8px 6px 0;
        font-size: 1.6rem;
    }

    /* ---- Meta info pill (matched FAQ / confidence) ---- */
    .meta-pill {
        display: inline-block;
        background: rgba(102,126,234,0.2);
        border: 1px solid rgba(102,126,234,0.4);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.78rem;
        color: #a5b4fc;
        margin: 4px 2px 0;
    }

    /* ---- Confidence bar ---- */
    .conf-bar-wrap {
        height: 6px;
        background: rgba(255,255,255,0.1);
        border-radius: 3px;
        margin: 6px 0;
        overflow: hidden;
    }
    .conf-bar-fill {
        height: 100%;
        border-radius: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }

    /* ---- Header ---- */
    .chat-header {
        text-align: center;
        padding: 20px 0 10px;
    }
    .chat-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea, #a78bfa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .chat-header p {
        color: #94a3b8;
        font-size: 0.92rem;
        margin: 4px 0 0;
    }

    /* ---- Divider ---- */
    hr.styled { border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 16px 0; }

    /* ---- Input box tweaks ---- */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        font-size: 0.95rem !important;
        padding: 12px 16px !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.3) !important;
    }

    /* ---- Send button ---- */
    .stButton > button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 10px 24px !important;
        transition: all 0.2s ease !important;
        width: 100%;
    }
    .stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(102,126,234,0.5) !important;
    }

    /* ---- Expander ---- */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.04) !important;
        border-radius: 8px !important;
        color: #94a3b8 !important;
        font-size: 0.82rem !important;
    }

    /* ---- Clear button ---- */
    .clear-btn button {
        background: rgba(239,68,68,0.15) !important;
        border: 1px solid rgba(239,68,68,0.3) !important;
        color: #fca5a5 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []          # list of dicts: {role, content, meta}
if "input_key" not in st.session_state:
    st.session_state.input_key = 0          # used to reset input box


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="chat-header">
        <h1>🎓 Course Support Bot</h1>
        <p>Ask me anything about our Online Learning Platform</p>
    </div>
    <hr class="styled"/>
    """,
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Sidebar — quick questions + info
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 💡 Example Questions")
    example_questions = [
        "How do I reset my password?",
        "Can I get a refund?",
        "How do I get my certificate?",
        "What payment methods do you accept?",
        "Can I download videos offline?",
        "How do I cancel my subscription?",
        "Is there a student discount?",
        "How do I contact an instructor?",
    ]
    for eq in example_questions:
        if st.button(eq, key=f"eq_{eq}", use_container_width=True):
            # Inject the example as a user message
            st.session_state.messages.append(
                {"role": "user", "content": eq, "meta": None}
            )
            response, match_result, matched_q = get_response(eq)
            meta = {
                "matched_question": matched_q,
                "score": match_result.best_score if match_result else None,
                "top_n": match_result.top_n if match_result else [],
            }
            st.session_state.messages.append(
                {"role": "bot", "content": response, "meta": meta}
            )

    st.markdown("<hr class='styled'/>", unsafe_allow_html=True)
    st.markdown("### ⚙️ Settings")
    show_debug = st.toggle("Show debug info", value=False)
    show_confidence = st.toggle("Show confidence score", value=True)

    st.markdown("<hr class='styled'/>", unsafe_allow_html=True)
    st.markdown(
        "<small style='color:#64748b'>Built with 🐍 Python • NLTK • scikit-learn • Streamlit</small>",
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Helper: render a single message
# ---------------------------------------------------------------------------
def render_message(msg: dict, show_debug: bool, show_confidence: bool) -> None:
    role = msg["role"]
    content = msg["content"]
    meta = msg.get("meta") or {}

    if role == "user":
        st.markdown(
            f'<div style="overflow:hidden">'
            f'  <span class="avatar-user">👤</span>'
            f'  <div class="user-bubble">{content}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    else:
        # Bot bubble
        bot_html = (
            f'<div style="overflow:hidden">'
            f'  <span class="avatar-bot">🤖</span>'
            f'  <div class="bot-bubble">{content}</div>'
            f'</div>'
        )
        st.markdown(bot_html, unsafe_allow_html=True)

        # Confidence badge + matched FAQ
        score = meta.get("score")
        matched_q = meta.get("matched_question")
        top_n = meta.get("top_n", [])

        pills_html = ""
        if matched_q and show_confidence:
            pct = int((score or 0) * 100)
            bar_color = (
                "#22c55e" if pct >= 70 else
                "#f59e0b" if pct >= 45 else
                "#ef4444"
            )
            pills_html += (
                f'<span class="meta-pill">📌 {matched_q}</span>'
                f'<span class="meta-pill">🎯 Confidence: {pct}%</span>'
            )
            st.markdown(
                f'<div style="margin-left:50px">'
                f'{pills_html}'
                f'<div class="conf-bar-wrap">'
                f'  <div class="conf-bar-fill" style="width:{pct}%;background:{bar_color}"></div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Debug: top-3 matches
        if show_debug and top_n:
            with st.expander("🔍 Debug: Top-3 candidate matches", expanded=False):
                for idx, s in top_n:
                    st.markdown(
                        f"**Score {s:.3f}** — _{st.session_state.get('faq_questions', ['?']* 50)[idx] if 'faq_questions' in st.session_state else f'FAQ #{idx}'}_"
                    )


# ---------------------------------------------------------------------------
# Chat history container
# ---------------------------------------------------------------------------
chat_container = st.container()

with chat_container:
    if not st.session_state.messages:
        st.markdown(
            """
            <div style="text-align:center;padding:40px 20px;color:#4a5568">
                <div style="font-size:3rem">💬</div>
                <p style="color:#64748b;font-size:0.95rem">
                    No messages yet. Ask a question below or pick one from the sidebar!
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        for msg in st.session_state.messages:
            render_message(msg, show_debug=show_debug, show_confidence=show_confidence)


# ---------------------------------------------------------------------------
# Input area
# ---------------------------------------------------------------------------
st.markdown("<hr class='styled'/>", unsafe_allow_html=True)

col_input, col_send, col_clear = st.columns([6, 1.2, 1.2])

with col_input:
    user_text = st.text_input(
        label="Your question",
        placeholder="Type your question here…",
        label_visibility="collapsed",
        key=f"chat_input_{st.session_state.input_key}",
    )

with col_send:
    send_clicked = st.button("Send ➤", use_container_width=True)

with col_clear:
    clear_clicked = st.button("🗑️ Clear", use_container_width=True)

# Handle send
if (send_clicked or (user_text and user_text.endswith("\n"))) and user_text.strip():
    query = user_text.strip()

    # Append user message
    st.session_state.messages.append({"role": "user", "content": query, "meta": None})

    # Get bot response
    with st.spinner("Thinking…"):
        response, match_result, matched_q = get_response(query)

    meta = {
        "matched_question": matched_q,
        "score": match_result.best_score if match_result else None,
        "top_n": match_result.top_n if match_result else [],
    }
    st.session_state.messages.append({"role": "bot", "content": response, "meta": meta})

    # Reset input box by incrementing key
    st.session_state.input_key += 1
    st.rerun()

# Handle clear
if clear_clicked:
    st.session_state.messages = []
    st.session_state.input_key += 1
    st.rerun()

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div style="text-align:center;margin-top:20px;">
        <small style="color:#334155">
            FAQ Chatbot • Powered by TF-IDF + Cosine Similarity • 
            <a href="mailto:support@learningplatform.com" style="color:#667eea">support@learningplatform.com</a>
        </small>
    </div>
    """,
    unsafe_allow_html=True,
)
