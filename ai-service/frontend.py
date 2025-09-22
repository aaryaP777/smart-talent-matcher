# ai-service/frontend.py

import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Talent Matcher", layout="wide")

st.title("📄 Smart Talent Matcher")

def upload_and_parse(file, endpoint):
    """Uploads a file and calls the FastAPI parsing endpoint."""
    files = {"file": (file.name, file.getvalue(), file.type)}
    try:
        response = requests.post(f"{API_URL}{endpoint}", files=files)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def display_parsed_results(result):
    """Renders the parsed data and explanations in a structured format."""
    if not result:
        return

    st.success("Document Parsed Successfully!")
    
    # Display the main parsed data
    st.subheader("📋 Extracted Information")
    st.json(result.get("parsed_data", {}))

    # Display the explanations in a collapsible section
    if "explanation" in result:
        with st.expander("💡 View AI Explanations (XAI)"):
            explanations = result.get("explanation", {})
            for key, desc in explanations.items():
                st.markdown(f"**{key.replace('_', ' ').title()}:** *{desc}*")

    st.info(f"**Document ID:** `{result.get('doc_id')}` | **Chunks Indexed:** `{result.get('chunks_indexed')}`")

# --- Sidebar and Page Logic ---

page = st.sidebar.radio("Choose an option", ["Parse Resume", "Parse Job Description"])

if page == "Parse Resume":
    st.header("📌 Parse a Resume")
    uploaded_file = st.file_uploader("Upload a resume (PDF)", type=["pdf"])
    if uploaded_file:
        if st.button("Parse Resume"):
            with st.spinner("Analyzing resume and generating explanations..."):
                result = upload_and_parse(uploaded_file, "/parse-resume")
                display_parsed_results(result)

elif page == "Parse Job Description":
    st.header("📌 Parse a Job Description")
    uploaded_file = st.file_uploader("Upload a job description (PDF)", type=["pdf"])
    if uploaded_file:
        if st.button("Parse JD"):
            with st.spinner("Analyzing JD and generating explanations..."):
                result = upload_and_parse(uploaded_file, "/parse-jd")
                display_parsed_results(result)
                if result and "doc_id" in result:
                    st.session_state["jd_id"] = result["doc_id"]

    if "jd_id" in st.session_state:
        st.markdown("---")
        st.header("🔎 Find Matching Resumes")
        top_k = st.number_input("Number of top resumes to fetch", 1, 10, 3)
        if st.button("Match Resumes"):
            with st.spinner("Searching for the best candidates..."):
                params = {"jd_id": st.session_state['jd_id'], "top_k": top_k}
                try:
                    response = requests.get(f"{API_URL}/match", params=params)
                    response.raise_for_status()
                    matches_result = response.json()
                    st.success("Found potential matches!")
                    
                    matches = matches_result.get("matches", [])
                    for i, match in enumerate(matches, 1):
                        with st.expander(f"**Match {i}** | Similarity: **{match['similarity']:.2%}** | Resume ID: `{match['resume_doc_id']}`"):
                            st.write("**Matching Snippet from Resume:**")
                            st.info(f"_{match['chunk']}_")
                except requests.exceptions.RequestException as e:
                    st.error(f"Matching Error: {e}")

