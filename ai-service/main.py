from fastapi import FastAPI, UploadFile, File, HTTPException
import os, uuid, asyncio
from parsers.resume_parser import parse_resume
from parsers.JD_parser import parse_jd
from vector_store.chunking import chunk_text
from vector_store.chroma_store import index_chunks
import uuid
from vector_store.chroma_store import query_similar

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
        # Call your existing parser (Ollama → JSON)
        result = await asyncio.to_thread(parse_resume, file_path)

        # Store the full extracted text into Chroma
        from parsers.text_extractor import extract_text_from_pdf
        raw_text = extract_text_from_pdf(file_path)
        chunks = chunk_text(raw_text)
        doc_id = f"resume-{uuid.uuid4().hex}"

        num_chunks = index_chunks(
            collection_name="resumes",
            doc_id=doc_id,
            chunks=chunks,
            base_metadata={"source": file.filename, "type": "resume"}
        )

        # Return both structured JSON and indexing info
        return {
            "parsed_data": result,
            "doc_id": doc_id,
            "chunks_indexed": num_chunks
        }

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

        from parsers.text_extractor import extract_text_from_pdf
        raw_text = extract_text_from_pdf(file_path)
        chunks = chunk_text(raw_text)
        doc_id = f"jd-{uuid.uuid4().hex}"

        num_chunks = index_chunks(
            collection_name="job_descriptions",
            doc_id=doc_id,
            chunks=chunks,
            base_metadata={"source": file.filename, "type": "jd"}
        )

        return {
            "parsed_data": result,
            "doc_id": doc_id,
            "chunks_indexed": num_chunks
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        os.remove(file_path)

@app.get("/match")
async def match_candidates(jd_id: str, top_k: int = 5):
    """
    Given a JD (by doc_id), return top-K matching resumes from Chroma.
    """
    jd_collection = "job_descriptions"
    resume_collection = "resumes"

    # Fetch JD chunks from Chroma
    col = query_similar.__globals__["get_collection"](jd_collection)
    jd_docs = col.get(where={"doc_id": jd_id})

    if not jd_docs["documents"]:
        raise HTTPException(status_code=404, detail=f"No JD found for id {jd_id}")

    # Use the *first chunk* of JD text as query
    jd_text = jd_docs["documents"][0]

    results = query_similar(
        collection_name=resume_collection,
        query_text=jd_text,
        top_k=top_k
    )

    matches = []
    for doc, meta, score in zip(results["documents"][0],
                                results["metadatas"][0],
                                results["distances"][0]):
        matches.append({
            "resume_doc_id": meta["doc_id"],
            "chunk": doc,
            "similarity": 1 - score  # convert cosine distance → similarity
        })

    return {"jd_id": jd_id, "matches": matches}
