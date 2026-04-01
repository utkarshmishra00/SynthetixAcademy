import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()

# FIX: Updated to the current, active Gemini 2.5 Flash model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3, 
    max_tokens=2048
)

# FIX: Updated to the new active embedding pipeline
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")