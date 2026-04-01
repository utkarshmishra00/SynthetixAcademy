SYNTHETIX ACADEMY
=================

PROJECT DESCRIPTION

Synthetix Academy is an intelligent, full-stack AI learning assistant that transforms static documents and multimedia into interactive educational experiences.

By leveraging local vector databases, local audio transcription, and Google's Gemini 2.5 AI models, the platform automatically ingests study materials, extracts core concepts, recommends dynamic multimedia resources, and generates self-assessment quizzes to test comprehension.

FEATURES
Multimodal Ingestion Layer: Upload PDFs or paste YouTube URLs. The system automatically extracts text via PyMuPDF or downloads and transcribes video audio locally using OpenAI's Whisper model.

AI Summarization: Powered by gemini-2.5-flash, the application chunks, vectorizes, and generates concise, structured summaries of the material.

Dynamic Knowledge Expansion: Bypasses traditional API limits by autonomously generating highly specific YouTube search links based on extracted core concepts.

Interactive Self-Assessment: Features a strict, context-grounded Quiz Engine that generates multiple-choice questions and provides instant grading and feedback.

Persistent Study Assistant: A RAG-powered chatbot interface allows users to ask follow-up questions directly against the uploaded material.

TECH STACK
Frontend: Streamlit

Backend: Python, FastAPI, Uvicorn

AI & Orchestration: LangChain, Google Gemini API (gemini-2.5-flash, gemini-embedding-001)

Vector Database: ChromaDB (Local)

Audio & Document Parsing: OpenAI Whisper, yt-dlp, PyMuPDF (fitz)

PREREQUISITES
Python 3.10 or higher

System packages: ffmpeg and node (Required for YouTube audio extraction).
Mac users can install these via Homebrew: brew install ffmpeg node

Google Gemini API Key (Available at aistudio.google.com)

INSTALLATION INSTRUCTIONS
Clone the Repository
git clone https://github.com/utkarshmishra00/SynthetixAcademy
cd synthetix-academy

Set Up the Environment
Create and activate a virtual environment:
python3 -m venv venv
source venv/bin/activate

Install Dependencies
pip install fastapi uvicorn streamlit langchain langchain-community langchain-core langchain-text-splitters chromadb pymupdf yt-dlp openai-whisper python-dotenv requests pydantic python-multipart langchain-google-genai

CONFIGURATION
Create a .env file in the root directory of the project and add your Gemini API key:

GOOGLE_API_KEY="your_gemini_api_key_here"

RUNNING THE APPLICATION
You will need two separate terminal windows to run the frontend and backend simultaneously. Ensure your virtual environment is activated in both terminals.

Terminal 1: Start the FastAPI Backend
uvicorn app.main:app --reload
(The API documentation will be available at http://127.0.0.1:8000/docs)

Terminal 2: Start the Streamlit Frontend
streamlit run app/ui.py
(The user interface will open automatically in your browser at http://localhost:8501)

AUTHOR
Utkarsh Mishra
GitHub: https://github.com/utkarshmishra00