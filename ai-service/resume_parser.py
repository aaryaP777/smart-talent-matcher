import os
import json
import re
from PyPDF2 import PdfReader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama.llms import OllamaLLM

def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


pdf_path = "./data/resume.pdf"

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"Resume file not found at {pdf_path}")

resume_text = extract_text_from_pdf(pdf_path)

prompt = PromptTemplate(
    input_variables=["resume_text"],
    template = """
    You are an information extraction system.  
    Analyze the provided resume text and extract the following details into a structured JSON format.

    **Extraction Requirements:**
    1. **Full Name** — Candidate’s complete name as mentioned in the resume.
    2. **Email** — Candidate’s primary email address.
    3. **Phone Number** — Candidate’s primary contact number (include country code if available).
    4. **Skills** — List of technical and non-technical skills mentioned in the resume.
    5. **Education** — List containing:
        - Degree / Qualification
        - Field of Study
        - Institution Name
        - Start Year and End Year (if available)
    6. **Experience** — List containing:
        - Job Title
        - Company Name
        - Start Date and End Date (or "Present" if ongoing)
        - Key Responsibilities / Achievements (bullet points)
    7. **Certifications** — List containing:
        - Certification Name
        - Issuing Organization
        - Year (if available)
    8. **Projects** — List containing:
        - Project Title
        - Description
        - Technologies Used (if mentioned)
        - Role in the Project

    **Output Rules:**
    - Return ONLY a valid JSON object.
    - **Important:** If any field is missing, **make sure** to use `null` for single values or an empty list `[]` for lists.
    - **Important:** Do not include any extra text, explanations, or formatting after the JSON.
    - Keep the JSON keys exactly as specified below.

    **Final JSON Structure:**
    {{
    "full_name": "",
    "email": "",
    "phone_number": "",
    "skills": [],
    "education": [
        {{
        "degree": "",
        "field_of_study": "",
        "institution": "",
        "start_year": "",
        "end_year": ""
        }}
    ],
    "experience": [
        {{
        "job_title": "",
        "company_name": "",
        "start_date": "",
        "end_date": "",
        "responsibilities": []
        }}
    ],
    "certifications": [
        {{
        "name": "",
        "organization": "",
        "year": ""
        }}
    ],
    "projects": [
        {{
        "title": "",
        "description": "",
        "technologies_used": [],
        "role": ""
        }}
    ]
    }}

    Resume Text: {resume_text}
    """
)

llm = OllamaLLM(model="llama3")
chain = prompt | llm

structured_response = chain.invoke({"resume_text": resume_text})
structured_response = structured_response.replace("```", '').strip()

structured_response = re.sub(r"^.*?(\{)", r"\1", structured_response, flags=re.S)

try:
    parsed_data = json.loads(structured_response)
    print("Parsed Resume Data:")
    print(json.dumps(parsed_data, indent=2))
except json.JSONDecodeError:
    print("Model output is not valid JSON. Raw output:")
    print(structured_response)