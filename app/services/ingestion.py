import fitz  # PyMuPDF
import os
import shutil
from fastapi import UploadFile
from app.services.rag import ContextObject

# Ensure upload directory exists
UPLOAD_DIR = "data/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def process_uploaded_file(file: UploadFile) -> ContextObject:
    """Saves the file locally and extracts its text."""
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    extracted_text = ""
    
    # Handle PDF Extraction
    if file.filename.endswith(".pdf"):
        with fitz.open(file_path) as doc:
            for page in doc:
                extracted_text += page.get_text("text") + "\n"
    else:
        # Fallback for plain text files
        with open(file_path, "r", encoding="utf-8") as f:
            extracted_text = f.read()
            
    return ContextObject(
        raw_text=extracted_text, 
        metadata={"source": file.filename, "type": file.content_type}
    )

import whisper
import yt_dlp
import uuid

def process_youtube_url(url: str) -> ContextObject:
    """Downloads YouTube audio and transcribes it using local Whisper."""
    # Create a unique temporary filename
    temp_id = str(uuid.uuid4())
    audio_path = os.path.join(UPLOAD_DIR, f"{temp_id}.mp3")
    
    # yt-dlp settings to extract audio
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(UPLOAD_DIR, f'{temp_id}.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True
    }
    
    # Download the audio
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_title = info.get('title', 'YouTube Video')
    
    # Load Whisper (using the "base" model for speed on your M2)
    model = whisper.load_model("base") 
    result = model.transcribe(audio_path)
    
    # Clean up the audio file after transcription to save space
    if os.path.exists(audio_path):
        os.remove(audio_path)
        
    return ContextObject(
        raw_text=result["text"], 
        metadata={"source": video_title, "type": "youtube_video"}
    )