import os
import json
import re
from langchain_core.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from parsers.text_extractor import extract_text_from_pdf

def parse_jd(pdf_path: str) -> dict:
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"JD file not found at {pdf_path}")

    jd_text = extract_text_from_pdf(pdf_path)
    prompt = PromptTemplate(
        input_variables=["jd_text"],
        template="""
    You are an intelligent Job Description (JD) parsing system.  
    Analyze the provided job description text and extract the following details into a structured JSON format.

    **Extraction Requirements:**
    1. **Job Title** — The title of the position being hired.
    2. **Company Name** — Name of the organization offering the job.
    3. **Location** — City, State, and/or Country (if mentioned).
    4. **Employment Type** — Full-time, Part-time, Contract, Internship, etc.
    5. **Required Skills** — List of technical and non-technical skills required.
    6. **Preferred Skills** — Additional skills that are nice to have.
    7. **Experience Required** — Minimum experience needed (in years, if mentioned).
    8. **Education Requirements** — Minimum education level or specific qualifications.
    9. **Responsibilities** — Key responsibilities and duties of the role (bullet points).
    10. **Salary Range** — If mentioned in the JD.
    11. **Benefits** — Perks, benefits, or incentives offered.
    12. **Application Deadline** — Last date to apply (if mentioned).

    **Output Rules:**
    - Return ONLY a valid JSON object.
    - **Important** If any field is missing, **make sure** to use `null` for single values or an empty list `[]` for lists.
    - **Important** Do not include any extra text, explanations, or formatting before or after the JSON.
    - Keep the JSON keys exactly as specified below.

    **Final JSON Structure:**
    {{
      "job_title": "",
      "company_name": "",
      "location": "",
      "employment_type": "",
      "required_skills": [],
      "preferred_skills": [],
      "experience_required": "",
      "education_requirements": "",
      "responsibilities": [],
      "salary_range": "",
      "benefits": [],
      "application_deadline": ""
    }}

    Job Description Text: {jd_text}
    """
)

    llm = OllamaLLM(model="llama3")
    chain = prompt | llm

    structured_response = chain.invoke({"jd_text": jd_text})
    structured_response = structured_response.replace("```", "").strip()
    structured_response = re.sub(r"^.*?(\{)", r"\1", structured_response, flags=re.S)
    structured_response = re.sub(r"(\}).*$", r"\1", structured_response, flags=re.S)

    try:
        return json.loads(structured_response)
    except json.JSONDecodeError:
        return {"error": "Model output is not valid JSON", "raw_output": structured_response}