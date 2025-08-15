from fastapi import FastAPI, UploadFile, File, HTTPException
import os, uuid, asyncio
from parsers.resume_parser import parse_resume
from parsers.JD_parser import parse_jd

app = FastAPI(title="Resume & JD Parser API")

@app.get("/")
async def root():
    return {"message": "API is running"}

@app.post("/parse-resume")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = f"temp_{uuid.uuid4().hex}.pdf"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        result = await asyncio.to_thread(parse_resume, file_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(file_path)

@app.post("/parse-jd")
async def parse_jd_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = f"temp_{uuid.uuid4().hex}.pdf"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        result = await asyncio.to_thread(parse_jd, file_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(file_path)