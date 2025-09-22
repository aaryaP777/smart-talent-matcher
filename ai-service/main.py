# ai-service/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
import os, uuid, asyncio
from parsers.resume_parser import parse_resume
from parsers.JD_parser import parse_jd
from vector_store.chunking import chunk_text
from vector_store.chroma_store import index_chunks, query_similar
# Import the new explainer function
from explanation.explainer import generate_explanations

app = FastAPI(title="Resume & JD Parser API")

@app.get("/")
async def root():
    return {"message": "API is running"}

async def process_and_explain(parser_func, file_path, file, collection_name, doc_type):
    """Helper function to parse, explain, and index a document."""
    try:
        # 1. Parse the document to get structured data
        parsed_result = await asyncio.to_thread(parser_func, file_path)

        # 2. Generate explanations for the parsed data
        explanations = generate_explanations(parsed_result)

        # 3. Index the raw text for semantic search
        from parsers.text_extractor import extract_text_from_pdf
        raw_text = extract_text_from_pdf(file_path)
        chunks = chunk_text(raw_text)
        doc_id = f"{doc_type}-{uuid.uuid4().hex}"

        num_chunks = index_chunks(
            collection_name=collection_name,
            doc_id=doc_id,
            chunks=chunks,
            base_metadata={"source": file.filename, "type": doc_type}
        )

        # 4. Return the combined result
        return {
            "parsed_data": parsed_result,
            "explanation": explanations,  # Explanations are now part of the response
            "doc_id": doc_id,
            "chunks_indexed": num_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/parse-resume")
async def parse_resume_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = f"temp_{uuid.uuid4().hex}.pdf"
    with open(file_path, "wb") as f:
        f.write(await file.read())
        
    return await process_and_explain(parse_resume, file_path, file, "resumes", "resume")

@app.post("/parse-jd")
async def parse_jd_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    file_path = f"temp_{uuid.uuid4().hex}.pdf"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    return await process_and_explain(parse_jd, file_path, file, "job_descriptions", "jd")

@app.get("/match")
async def match_candidates(jd_id: str, top_k: int = 5):
    jd_collection = "job_descriptions"
    resume_collection = "resumes"

    col = query_similar.__globals__["get_collection"](jd_collection)
    jd_docs = col.get(where={"doc_id": jd_id})

    if not jd_docs["documents"]:
        raise HTTPException(status_code=404, detail=f"No JD found for id {jd_id}")

    jd_text = jd_docs["documents"][0]
    results = query_similar(collection_name=resume_collection, query_text=jd_text, top_k=top_k)

    matches = [
        {
            "resume_doc_id": meta["doc_id"],
            "chunk": doc,
            "similarity": 1 - score
        }
        for doc, meta, score in zip(results["documents"][0], results["metadatas"][0], results["distances"][0])
    ]

    return {"jd_id": jd_id, "matches": matches}
