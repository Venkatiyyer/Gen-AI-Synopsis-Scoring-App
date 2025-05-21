import streamlit as st
import os
import shutil
from backend import (
    extract_text_from_file,
    extract_and_store_in_faiss,
    evaluate_synopsis,
    ARTICLE_PATH,
    SYNOPSIS_PATH
)

# ─── Data Reset Uploads────────────────────────────────────────────────────────────────

if st.sidebar.button("🗑️ Delete All Upload Files"):
    # Remove stored FAISS indices
    for path in ('temp'):
        if os.path.isdir(path):
            shutil.rmtree(path)
    # # Clear session state
    # for key in ["article_text", "synopsis_text"]:
    #     if key in st.session_state:
    #         del st.session_state[key]
    st.sidebar.success("✅ All stored files has been cleared.")
    # st.experimental_rerun()

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Eval-RAG by Venkat Iyer", layout="wide", initial_sidebar_state="expanded")


# ─── Access Control ─────────────────────────────────────────────────────────────
# Replace 'your_token_here' with a secure token or load from environment
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "token")

    
# ─── Data Reset FAISS────────────────────────────────────────────────────────────────
# if st.sidebar.button("🗑️ Clear All Data"):
#     # Remove stored FAISS indices
#     for path in (ARTICLE_PATH, SYNOPSIS_PATH):
#         if os.path.isdir(path):
#             shutil.rmtree(path)
#     # Clear session state
#     for key in ["article_text", "synopsis_text"]:
#         if key in st.session_state:
#             del st.session_state[key]
#     st.sidebar.success("✅ All stored data has been cleared.")
#     # st.experimental_rerun()

# ─── Data Reset Uploads────────────────────────────────────────────────────────────────

if st.sidebar.button("🗑️ Delete All Upload Files"):
    # Remove stored FAISS indices
    for path in ('temp'):
        if os.path.isdir(path):
            shutil.rmtree(path)
    # # Clear session state
    # for key in ["article_text", "synopsis_text"]:
    #     if key in st.session_state:
    #         del st.session_state[key]
    st.sidebar.success("✅ All stored files has been cleared.")
    # st.experimental_rerun()

# ─── Custom CSS Styling ───────────────────────────────────────────────────────
st.markdown("""
    <style>
        [data-testid="stSidebar"] { background-color: #2c3e50; color: #ecf0f1; }
        [data-testid="stSidebar"] .css-1d391kg { color: #ecf0f1; }
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        h1, h2, h3 { color: #2c3e50; }
        .stButton > button {
            background-color: #4CAF50; color: white; padding: 0.5rem 1.2rem;
            border: none; border-radius: 8px; font-size: 16px;
        }
        .stButton > button:hover { background-color: #388e3c; }
        textarea, input[type="file"] { border-radius: 8px !important; }
        label[data-testid="stRadioLabel"] > div {
            font-size: 1.1rem; font-weight: 500; color: #ecf0f1;
        }
        div[role="radiogroup"] > label:hover { background-color: #34495e; border-radius: 0.5rem; }
        input[type="radio"]:checked + div {
            background-color: #364e41 !important; color: white !important;
            border-radius: 0.5rem;
        }
        .sidebar-nav-item { display: flex; align-items: center;
            padding: 8px 16px; border-radius: 8px; margin-bottom: 8px; cursor: pointer;
        }
        .sidebar-nav-item img { width: 24px; height: 24px; margin-right: 8px; }
        .sidebar-nav-item:hover { background-color: #34495e; }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
    .sidebar-title {
        font-size: 28px; font-weight: bold; margin-bottom: 15px;
        background: linear-gradient(120deg, #9400D3, #5da6b0, #134f5c);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .sidebar-step { font-size: 18px; color: #999999; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.sidebar.markdown('<div class="sidebar-title">RAG Evaluation Made Effortless!</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-step">1. Upload Article & Example</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-step">2. Enter Synopsis</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-step">3. View Score</div>', unsafe_allow_html=True)

# ─── Sidebar Navigation ───────────────────────────────────────────────────────
page = st.sidebar.radio("*Go to*", ["Upload", "Synopsis Evaluation"])

# Header with icon and title
col_icon, col_title = st.columns([0.075, 1], gap="small")
with col_icon:
    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
    st.image("static/recognition.png", width=50)
with col_title:
    st.markdown("## Eval-RAG")

# Greeting
st.markdown("""
<h2 style="margin-top:14px; font-weight:bold;">
  <span style="background: linear-gradient(90deg, #0021F3, #9400D3, #EE82EE);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
    Welcome!</span>
  <span style="background: linear-gradient(90deg, #8A2BE2, #FF69B4);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
    Let's evaluate your synopsis.</span>
</h2>
""", unsafe_allow_html=True)


# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# If not yet authenticated, show a small centered form
if not st.session_state.authenticated:
    # Create three columns; middle one is where our small form lives
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("access_form", clear_on_submit=False):
            st.write("🔐 **Access Token**")
            token_input = st.text_input("", type="password", placeholder="Enter token")
            submitted = st.form_submit_button("Enter")
            if submitted:
                if token_input == ACCESS_TOKEN:
                    st.session_state.authenticated = True
                    st.success("✅ Access granted")
                else:
                    st.error("⚠️ Invalid token")

    # Block the rest of the app until authenticated
    if not st.session_state.authenticated:
        st.stop()
        
# Initialize session-state flags to clear uploads and FAISS indexes on browser refresh
if "clear_uploads_and_indexes" not in st.session_state:
    st.session_state.clear_uploads_and_indexes = True

# Clear any previous upload and FAISS-related state once per fresh session
if st.session_state.clear_uploads_and_indexes:
    for key in list(st.session_state.keys()):
        if key.startswith("article_uploader") \
           or key.startswith("synopsis_uploader") \
           or key.startswith("faiss_"):
            del st.session_state[key]
    st.session_state.clear_uploads_and_indexes = False

# ─── Page: Upload ─────────────────────────────────────────────────────────────
if page == "Upload":
    st.image("static/upload.png", width=50)
    with st.expander("📁 Upload Article and Gold Synopsis", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            article_file = st.file_uploader("Upload Article (PDF/TXT)", type=["pdf", "txt"], key="article_uploader")
        with col2:
            synopsis_file = st.file_uploader("Upload Gold Synopsis (PDF/TXT, optional)", type=["pdf", "txt"], key="synopsis_uploader")

        if st.button("⬆️ Upload Files", key="upload_button"):
            if not article_file:
                st.warning("⚠️ Please upload the article file.")
            else:
                try:
                    with st.spinner("📤 Processing and Saving to FAISS..."):
                        result = extract_and_store_in_faiss(article_file, synopsis_file)
                        st.session_state["article_text"] = result.get("article_anon", "")
                        st.session_state["synopsis_text"] = result.get("synopsis_anon", "")

                    if result["status"] == "success":
                        if synopsis_file:
                            st.success("✅ Article and gold synopsis uploaded successfully!")
                        else:
                            st.success("✅ Article uploaded successfully! (No gold synopsis provided)")
                    else:
                        st.error(f"❌ Upload failed: {result.get('message', 'Unknown error')}")
                except Exception as e:
                    st.error(f"❌ Error during upload: {str(e)}")

# # ─── Page: Synopsis Evaluation ────────────────────────────────────────────────
# elif page == "Synopsis Evaluation":
#     st.image("static/transcript.png", width=50)
#     st.subheader("📝 Enter and Evaluate Your Synopsis")
#     # synopsis_input = st.text_area("Enter Your Synopsis Text Here")

#     if st.button("🔍 Evaluate Synopsis", key="evaluate_button"):
#         # if not synopsis_input.strip():
#         #     st.warning("⚠️ Please enter a synopsis to evaluate.")
#         try:
            
#             evaluation = evaluate_synopsis()
#             with st.expander("📊 Evaluation Results", expanded=True):
#                 st.subheader("📝 Your Article")
#                 st.markdown(evaluation["article"], unsafe_allow_html=True)
#                 st.subheader("📝 Your Synopsis")
#                 st.markdown(evaluation["synopsis"], unsafe_allow_html=True)
#                 st.subheader("📝 Your Result")
#                 st.markdown(evaluation["result"], unsafe_allow_html=True)
#         except Exception as e:
#             st.error(f"❌ Evaluation error: {str(e)}")


# ─── Page: Synopsis Evaluation ────────────────────────────────────────────────
elif page == "Synopsis Evaluation":
    st.image("static/transcript.png", width=50)
    st.subheader("🧾 Evaluate Your Synopsis")
    # synopsis_input = st.text_area("Enter Your Synopsis Text Here")

    if st.button("🔍 Evaluate Synopsis", key="evaluate_button"):
        
        try:
            evaluation = evaluate_synopsis()

            # Show result outside expander
            st.subheader("📊 Result")
            st.markdown(evaluation.get("result", ""), unsafe_allow_html=True)

            # Expander for Article
            with st.expander("📄 Retrieved Article Context", expanded=False):
                st.markdown(evaluation.get("article", ""), unsafe_allow_html=True)

            # Expander for User Synopsis
            with st.expander("✍️ Your Synopsis", expanded=False):
                st.markdown(evaluation.get("synopsis", ""), unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Evaluation error: {str(e)}")

