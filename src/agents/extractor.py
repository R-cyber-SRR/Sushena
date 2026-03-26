import os
from langchain_core.prompts import ChatPromptTemplate
from typing import Dict, Any, List
from pydantic import BaseModel
from src.state import AgentState, ExtractedEntity

# Auto-detect: use Groq in the cloud, Ollama locally
if os.environ.get("GROQ_API_KEY"):
    from langchain_groq import ChatGroq
    llm = ChatGroq(model="llama3-8b-8192", temperature=0)
else:
    from langchain_ollama import ChatOllama
    llm = ChatOllama(model="qwen2.5:1.5b", temperature=0)

class ExtractionOutput(BaseModel):
    codes: List[ExtractedEntity]

EXTRACTOR_PROMPT = """You are a medical coding expert. Extract all ICD-10 diagnosis codes and CPT procedure codes from the following clinical note.

Return a structured output with the list of extracted codes.
If no modifier is found or applies for CPT codes, leave it null.
If you are unsure, extract the most highly probable codes and do not guess non-existent codes.

Clinical Note:
{clinical_note}
"""

def extract_codes_node(state: AgentState) -> Dict[str, Any]:
    note = state.get("clinical_note", "")
    prompt = ChatPromptTemplate.from_template(EXTRACTOR_PROMPT)
    chain = prompt | llm.with_structured_output(ExtractionOutput)
    
    extracted = chain.invoke({"clinical_note": note})
    extracted_data = [c.model_dump() for c in extracted.codes]
    
    audit_evt = {
        "agent": "CodeExtractorAgent",
        "action": f"Extracted {len(extracted_data)} codes from clinical note",
        "rule_applied": "ICD-10/CPT guidelines NLP extraction",
        "reason": f"LLM matched and identified {len(extracted_data)} distinct items in free text.",
        "fallback": "Manual medical coding review if zero codes extracted."
    }
    
    return {
        "extracted_codes": extracted_data,
        "audit_trail": [audit_evt],
        "overall_status": state.get("overall_status", "Processing")
    }
