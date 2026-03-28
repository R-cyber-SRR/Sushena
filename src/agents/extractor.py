import os
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from pydantic import BaseModel
from src.state import AgentState, ExtractedEntity

# Auto-detect: use Groq in the cloud, Ollama locally
if os.environ.get("GROQ_API_KEY"):
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0)
else:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="qwen2.5:1.5b", temperature=0)

class ExtractionOutput(BaseModel):
    codes: List[ExtractedEntity]

EXTRACTOR_PROMPT = """You are an elite Medical Coding Specialist. 
Analyze the clinical note and extract ONLY the most relevant ICD-10 diagnosis codes and CPT procedure codes.

RULES:
1. PRECISION: Only pick the SINGLE most specific code for each diagnosis or procedure.
2. NO SHOTGUNNING: Do NOT provide a list of similar codes for the same item. If multiple codes seem applicable, choose the one with the highest specificity based on the note.
3. ADHERENCE: Only extract what is explicitly stated or strongly implied. Do NOT hallucinate codes.
4. FORMAT: Return a structured list. If no modifier applies, leave it null.

Clinical Note:
{clinical_note}
"""

def extract_codes_node(state: AgentState) -> Dict[str, Any]:
    note = state.get("clinical_note", "")
    prompt = ChatPromptTemplate.from_template(EXTRACTOR_PROMPT)
    chain = prompt | llm.with_structured_output(ExtractionOutput)
    
    audit_evt = {
        "agent": "CodeExtractorAgent",
        "action": "Attempting code extraction",
        "rule_applied": "ICD-10/CPT precision extraction",
        "reason": "Processing raw clinical text via LLM with strict specificity constraints.",
        "fallback": "Manual review if extraction fails or error occurs."
    }

    try:
        extracted = chain.invoke({"clinical_note": note})
        extracted_data = [c.model_dump() for c in extracted.codes]
        audit_evt["action"] = f"Extracted {len(extracted_data)} codes from clinical note"
        audit_evt["reason"] = f"LLM matched and identified {len(extracted_data)} distinct items using high-precision logic."
    except Exception as e:
        print(f"Extraction Error (400/Tool Failure): {e}")
        extracted_data = []
        audit_evt["action"] = "Extraction Failed (LLM Error)"
        audit_evt["reason"] = f"The LLM failed to generate a valid structured response: {str(e)[:100]}"
        audit_evt["fallback"] = "CRITICAL: System encountered an LLM error. Human intervention required for this note."

    return {
        "extracted_codes": extracted_data,
        "audit_trail": [audit_evt],
        "overall_status": state.get("overall_status", "Processing")
    }
