import streamlit as st

st.set_page_config(page_title="Vidya Dashboard", layout="wide", page_icon="🎓")

st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        max-width: 1200px;
    }
    .tool-card {
        background: #ffffff;
        border: 1px solid #dfe3e8;
        border-radius: 12px;
        padding: 1.2rem 1.2rem 1rem 1.2rem;
        height: 100%;
        min-height: 200px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .tool-card h3 {
        margin: 0 0 0.55rem 0;
        font-size: 1.15rem;
        font-weight: 700;
        color: #1f2937;
    }
    .tool-card p {
        margin: 0 0 0.9rem 0;
        color: #4b5563;
        line-height: 1.5;
        font-size: 0.98rem;
    }
    .red-btn {
        display: inline-block;
        width: 100%;
        background-color: #ff4b4b;
        color: white !important;
        padding: 0.7rem 1rem;
        text-align: center;
        text-decoration: none;
        border-radius: 6px;
        font-weight: 700;
        margin-top: auto;
        box-sizing: border-box;
    }
    .red-btn:hover {
        background-color: #ff3333;
    }
    .small-btn {
        display: inline-block;
        width: 100%;
        background-color: #ff4b4b;
        color: white !important;
        padding: 0.6rem 0.8rem;
        text-align: center;
        text-decoration: none;
        border-radius: 6px;
        font-weight: 700;
        margin-top: 0.6rem;
        box-sizing: border-box;
    }
    .small-btn:hover {
        background-color: #ff3333;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎓 Vidya Platform")
st.markdown("Advanced Agentic Learning & Assessment Hub")
st.divider()

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown("""
    <div class="tool-card">
        <div>
            <h3>🎤 Speaking Assessment</h3>
            <p>Start the speaking checker and speak naturally with Sara for live feedback.</p>
        </div>
        <a href='http://localhost:8004' target='_self' class='red-btn'>Start Speaking Assessment</a>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="tool-card">
        <div>
            <h3>🎧 Listening Assessment</h3>
            <p>Start the listening test and answer AI-generated questions.</p>
        </div>
        <a href='http://localhost:8503' target='_self' class='red-btn'>Start Listening Assessment</a>
    </div>
    """, unsafe_allow_html=True)

st.markdown("### Advanced Tools")

col3, col4 = st.columns(2, gap="large")

with col3:
    st.markdown("""
    <div class="tool-card">
        <div>
            <h3>🤖 RAG Conversation</h3>
            <p>Start a guided science conversation with the RAG tutor.</p>
        </div>
        <a href='http://localhost:8506' target='_self' class='red-btn'>Start RAG Conversation</a>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="tool-card">
        <div>
            <h3>🕵️ Plagiarism Check</h3>
            <p>Run plagiarism detection for student work and teacher review from one place.</p>
        </div>
        <div style='display:flex; gap:0.7rem; margin-top:auto;'>
            <a href='http://localhost:8507' target='_self' class='small-btn' style='flex:1;'>Student Upload</a>
            <a href='http://localhost:8502' target='_self' class='small-btn' style='flex:1;'>Teacher Report</a>
        </div>
    </div>
    """, unsafe_allow_html=True)

