from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate  # <-- FIXED IMPORT
from app.core.llm import llm, embeddings

# Temporary mock for the ContextObject
class ContextObject:
    def __init__(self, raw_text: str, metadata: dict):
        self.raw_text = raw_text
        self.metadata = metadata

def index_and_summarize(context: ContextObject, document_id: str):
    """Chunks text, saves to vector DB, and generates a summary."""
    
    # 1. Chunk the document
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(context.raw_text)
    metadatas = [context.metadata for _ in chunks]
    
    # 2. Store in ChromaDB locally
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory="./data/vectorstore",
        collection_name=document_id
    )
    
    # 3. Generate Summary & Recommendations using Gemini
    prompt = PromptTemplate.from_template("""
    You are an expert learning assistant. Read the following text and provide:
    1. A concise, structured summary (3-4 bullet points).
    2. 'Core Concepts': A list of 3 key topics discussed.
    3. 'Further Exploration': 3 highly specific search queries the user could type into YouTube or Google to learn more about this.
    
    Format your response clearly.
    
    Text: {text}
    """)
    
    chain = prompt | llm
    result = chain.invoke({"text": context.raw_text[:8000]})
    
    return result.content


from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
import urllib.parse

# Define the exact JSON structure we want
class TopicList(BaseModel):
    topics: list[str] = Field(description="A list of 3 highly specific YouTube search queries")

def get_youtube_search_queries(text_context: str) -> list[dict]:
    """Generates direct YouTube search links based on document concepts."""
    parser = JsonOutputParser(pydantic_object=TopicList)
    
    prompt = PromptTemplate(
        template="""You are a learning assistant. Based on the following text, generate 3 highly specific search queries that a student could type into YouTube to find educational videos about the core concepts. 
        Return ONLY the JSON.
        
        Text: {text}
        
        {format_instructions}""",
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    # Use the first 5000 characters to figure out the topics
    result = chain.invoke({"text": text_context[:5000]})
    
    # Convert those text topics into clickable YouTube URLs
    recommendations = []
    for topic in result["topics"]:
        # This turns "Machine Learning" into "Machine+Learning" for the URL
        safe_query = urllib.parse.quote_plus(topic + " tutorial") 
        recommendations.append({
            "title": f"Watch videos about: {topic}",
            "url": f"https://www.youtube.com/results?search_query={safe_query}"
        })
        
    return recommendations


def chat_with_document(document_id: str, query: str, raw_text: str = "") -> str:
    """Searches the vector DB. If empty, uses the raw text fallback."""
    vectorstore = Chroma(
        persist_directory="./data/vectorstore",
        embedding_function=embeddings,
        collection_name=document_id
    )
    
    docs = vectorstore.similarity_search(query, k=4)
    
    # FIX: If the database is empty, fallback to the raw text in memory!
    if not docs and raw_text:
        # Pass a massive chunk of the transcript directly to Gemini 2.5
        context_text = raw_text[:20000] 
    else:
        context_text = "\n\n".join([doc.page_content for doc in docs])
    
    prompt = PromptTemplate.from_template("""
    You are a helpful study assistant. Answer the user's question based ONLY on the provided context. 
    If the answer is not in the context, say "I cannot find the answer to that in the provided material."
    
    Context:
    {context}
    
    Question: {question}
    """)
    
    chain = prompt | llm
    result = chain.invoke({"context": context_text, "question": query})
    
    return result.content