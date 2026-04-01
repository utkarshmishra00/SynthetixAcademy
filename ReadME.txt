SYNTHETIX ACADEMY
=================

PROJECT OVERVIEW
----------------
Synthetix Academy is an intelligent, full-stack AI learning assistant designed to transform static documents and multimedia into interactive educational experiences.

The platform leverages local vector databases, on-device audio transcription, and advanced AI models (Google Gemini 2.5) to automatically process study materials. It extracts key concepts, generates structured summaries, recommends relevant multimedia resources, and creates quizzes for self-assessment.


CORE FEATURES
-------------

1. Multimodal Ingestion
   - Upload PDF documents or provide YouTube links
   - Extract text using PyMuPDF
   - Download and transcribe video audio locally using Whisper

2. AI-Powered Summarization
   - Uses gemini-2.5-flash for fast, high-quality summaries
   - Splits and processes content into structured chunks
   - Generates concise and easy-to-understand learning material

3. Dynamic Knowledge Expansion
   - Automatically identifies core concepts
   - Generates targeted YouTube search links
   - Helps users explore topics beyond the original material

4. Interactive Quiz Engine
   - Creates multiple-choice questions from content
   - Ensures questions are context-grounded
   - Provides instant grading and feedback

5. Persistent Study Assistant
   - RAG (Retrieval-Augmented Generation) based chatbot
   - Allows users to ask follow-up questions
   - Answers are grounded in uploaded material


TECH STACK
----------

Frontend:
  - Streamlit

Backend:
  - Python
  - FastAPI
  - Uvicorn

AI & Orchestration:
  - LangChain
  - Google Gemini API (gemini-2.5-flash, gemini-embedding-001)

Vector Database:
  - ChromaDB (Local)

Audio & Document Processing:
  - OpenAI Whisper
  - yt-dlp
  - PyMuPDF (fitz)


PREREQUISITES
-------------

- Python 3.10 or higher
- System packages:
    ffmpeg
    node
  (Required for YouTube audio extraction)

Mac installation:
  brew install ffmpeg node

- Google Gemini API Key:
  https://aistudio.google.com


INSTALLATION
------------

1. Clone the repository
   git clone https://github.com/utkarshmishra00/SynthetixAcademy
   cd synthetix-academy

2. Create and activate virtual environment
   python3 -m venv venv
   source venv/bin/activate

3. Install dependencies
   pip install fastapi uvicorn streamlit langchain langchain-community langchain-core langchain-text-splitters chromadb pymupdf yt-dlp openai-whisper python-dotenv requests pydantic python-multipart langchain-google-genai


CONFIGURATION
-------------

Create a .env file in the root directory:

   GOOGLE_API_KEY="your_gemini_api_key_here"


RUNNING THE APPLICATION
-----------------------

Use two terminals simultaneously (activate venv in both)

Terminal 1 - Backend:
   uvicorn app.main:app --reload

   API Docs:
   http://127.0.0.1:8000/docs

Terminal 2 - Frontend:
   streamlit run app/ui.py

   App UI:
   http://localhost:8501


AUTHOR
------

Utkarsh Mishra
GitHub: https://github.com/utkarshmishra00