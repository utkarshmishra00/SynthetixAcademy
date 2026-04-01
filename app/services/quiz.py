from langchain_core.prompts import PromptTemplate  # <-- FIXED IMPORT
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List
from app.core.llm import llm

# Define the exact structure we want Gemini to output
class MCQ(BaseModel):
    question: str = Field(description="The multiple choice question")
    options: List[str] = Field(description="Exactly 4 answer options")
    correct_answer: str = Field(description="The exact string of the correct option")

class Quiz(BaseModel):
    questions: List[MCQ]

def generate_quiz(text_context: str) -> dict:
    """Generates 5 MCQs based strictly on the provided text."""
    parser = JsonOutputParser(pydantic_object=Quiz)
    
    prompt = PromptTemplate(
        template="""You are a strict academic evaluator. Based ONLY on the provided text, create 5 multiple-choice questions. 
        Do not use outside knowledge.
        
        Text: {text}
        
        {format_instructions}""",
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    
    chain = prompt | llm | parser
    return chain.invoke({"text": text_context[:10000]})