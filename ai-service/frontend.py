import streamlit as st
import requests
import json

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Resume & JD Parser", layout="wide")

st.title("Resume & JD Parser")

page = st.sidebar.radio("Choose an option", ["Parse Resume", "Parse Job Description"])

def upload_and_parse(file, endpoint):
    """Helper to upload file and call FastAPI"""
    files = {"file": file}
    response = requests.post(f"{API_URL}{endpoint}", files=files)
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error {response.status_code}: {response.json().get('detail')}")
        return None

if page == "Parse Resume":
    st.header("📌 Parse Resume")
    uploaded_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Parse Resume"):
            with st.spinner("Parsing resume..."):
                result = upload_and_parse(uploaded_file, "/parse-resume")
                if result:
                    st.success("Resume Parsed Successfully")
                    st.json(result)

elif page == "Parse Job Description":
    st.header("📌 Parse Job Description")
    uploaded_file = st.file_uploader("Upload Job Description (PDF)", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Parse JD"):
            with st.spinner("Parsing job description..."):
                result = upload_and_parse(uploaded_file, "/parse-jd")
                if result:
                    st.success("JD Parsed Successfully")
                    st.json(result)

                    # Store JD ID in session state so it survives refresh
                    st.session_state["jd_id"] = result.get("doc_id")

    # Show matching section only if JD is already parsed
    if "jd_id" in st.session_state:
        st.markdown("---")
        st.subheader("🔎 Find Matching Resumes")

        top_k = st.number_input("Number of top resumes to fetch", min_value=1, max_value=10, value=3, step=1)

        if st.button("Match Resumes"):
            with st.spinner("Finding best matching resumes..."):
                try:
                    response = requests.get(f"{API_URL}/match", params={"jd_id": st.session_state['jd_id'], "top_k": top_k})
                    if response.status_code == 200:
                        matches_result = response.json()
                        st.success("Matches Found")

                        matches = matches_result.get("matches", [])
                        for i, match in enumerate(matches, start=1):
                            with st.expander(f"Match {i}: Resume ID {match['resume_doc_id']}"):
                                st.write(f"**Similarity Score:** {match['similarity']:.4f}")
                                st.write("**Matching Text Chunk:**")
                                st.write(match['chunk'])
                    else:
                        st.error(f"Error {response.status_code}: {response.text}")
                except Exception as e:
                    st.error(f"Request failed: {e}")
