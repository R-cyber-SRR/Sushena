import os
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from pydantic import BaseModel
from src.state import AgentState, ExtractedEntity

# Auto-detect: use GitHub Models, Groq, or Ollama
if os.environ.get("GITHUB_TOKEN"):
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(
        model="Meta-Llama-3.1-8B-Instruct",
        api_key=os.environ.get("GITHUB_TOKEN"),
        base_url="https://models.inference.ai.azure.com/v1",
        temperature=0,
        extra_body={"max_tokens": 4096}
    )
elif os.environ.get("GROQ_API_KEY"):
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
else:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="qwen2.5:1.5b", temperature=0)

from langchain_core.output_parsers import PydanticOutputParser

class ExtractionOutput(BaseModel):
    codes: List[ExtractedEntity]

parser = PydanticOutputParser(pydantic_object=ExtractionOutput)

EXTRACTOR_PROMPT = """You are an elite Medical Coding Specialist. 
Analyze the clinical note and extract ONLY the most relevant ICD-10 diagnosis codes and CPT procedure codes.

RULES:
1. PRECISION: Only pick the SINGLE most specific code for each diagnosis or procedure.
2. NO SHOTGUNNING: Do NOT provide a list of similar codes for the same item. If multiple codes seem applicable, choose the one with the highest specificity based on the note.
3. ADHERENCE: Only extract what is explicitly stated or strongly implied. Do NOT hallucinate codes.

{format_instructions}

Clinical Note:
{clinical_note}
"""

def extract_codes_node(state: AgentState) -> Dict[str, Any]:
    note = state.get("clinical_note", "")
    prompt = ChatPromptTemplate.from_template(EXTRACTOR_PROMPT)
    
    # Use the parser to get format instructions
    format_instructions = parser.get_format_instructions()
    
    # Ensure llm has enough tokens
    chain = prompt | llm | parser
    
    audit_evt = {
        "agent": "CodeExtractorAgent",
        "action": "Attempting code extraction",
        "rule_applied": "ICD-10/CPT precision extraction",
        "reason": "Processing raw clinical text via LLM with strict specificity constraints.",
        "fallback": "Manual review if extraction fails or error occurs."
    }

    try:
        # Get raw response first
        # Use bind to ensure max_tokens is sent
        runnable = prompt | llm.bind(max_tokens=4096)
        raw_res = runnable.invoke({
            "clinical_note": note,
            "format_instructions": format_instructions
        })
        
        extracted = parser.parse(raw_res.content)
        extracted_data = [c.model_dump() for c in extracted.codes]
        audit_evt["action"] = f"Extracted {len(extracted_data)} codes from clinical note"
        audit_evt["reason"] = f"LLM matched and identified {len(extracted_data)} distinct items using high-precision logic."
    except Exception as e:
        print(f"Extraction Error (LLM/Parser Failure): {e}")
        extracted_data = []
        audit_evt["action"] = "Extraction Failed (LLM Error)"
        audit_evt["reason"] = f"The LLM failed to generate a valid response: {str(e)[:150]}"
        audit_evt["fallback"] = "CRITICAL: System encountered an LLM error. Human intervention required."

    return {
        "extracted_codes": extracted_data,
        "audit_trail": [audit_evt],
        "overall_status": state.get("overall_status", "Processing")
    }
