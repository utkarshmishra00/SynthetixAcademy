from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import re
from dotenv import load_dotenv

# Import all our services
from app.services.ingestion import process_uploaded_file, process_youtube_url
from app.services.rag import index_and_summarize, get_youtube_search_queries, chat_with_document
from app.services.quiz import generate_quiz as create_quiz

load_dotenv()

app = FastAPI(title="Synthetix Academy API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

document_store = {}

# Pydantic models for JSON requests
class URLRequest(BaseModel):
    url: str

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "Synthetix Academy Engine is running online."}

@app.post("/api/v1/ingest/file")
async def ingest_file(file: UploadFile = File(...)):
    try:
        context_obj = await process_uploaded_file(file)
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', file.filename.split('.')[0])
        doc_id = f"doc_{clean_name}"
        document_store[doc_id] = context_obj
        return {"message": "Success", "document_id": doc_id, "title": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/ingest/url")
async def ingest_url(payload: URLRequest):
    try:
        context_obj = process_youtube_url(payload.url)
        # Create a safe ID from the video title
        clean_name = re.sub(r'[^a-zA-Z0-9]', '', context_obj.metadata["source"])[:20]
        doc_id = f"yt_{clean_name}"
        document_store[doc_id] = context_obj
        return {"message": "Success", "document_id": doc_id, "title": context_obj.metadata["source"]}
    except Exception as e:
        print(f"YouTube Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/summarize/{document_id}")
async def summarize_document(document_id: str):
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        summary = index_and_summarize(document_store[document_id], document_id)
        return {"result": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/recommend/{document_id}")
async def recommend_resources(document_id: str):
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        links = get_youtube_search_queries(document_store[document_id].raw_text)
        return {"recommendations": links}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/quiz/generate/{document_id}")
async def generate_quiz(document_id: str):
    if document_id not in document_store:
        raise HTTPException(status_code=404, detail="Document not found.")
    try:
        quiz_json = create_quiz(document_store[document_id].raw_text)
        return {"quiz": quiz_json}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat/{document_id}")
async def chat_endpoint(document_id: str, payload: ChatRequest):
    try:
        # Grab the raw text from memory to use as a backup
        raw_text = document_store[document_id].raw_text if document_id in document_store else ""
        
        answer = chat_with_document(document_id, payload.message, raw_text)
        return {"reply": answer}
    except Exception as e:
        print(f"Chat Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))