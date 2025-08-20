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
                    st.success("✅ Resume Parsed Successfully")
                    st.json(result)

elif page == "Parse Job Description":
    st.header("📌 Parse Job Description")
    uploaded_file = st.file_uploader("Upload Job Description (PDF)", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Parse JD"):
            with st.spinner("Parsing job description..."):
                result = upload_and_parse(uploaded_file, "/parse-jd")
                if result:
                    st.success("✅ JD Parsed Successfully")
                    st.json(result)