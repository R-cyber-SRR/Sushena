import os
import json
from dotenv import load_dotenv

# Ensure API key is loaded before importing modules that need it
load_dotenv()

from src.workflow import create_mediagent_workflow

# We will run 3 distinct clinical notes to demonstrate the system
clinical_notes = [
    {
        "name": "Standard Clear Case",
        "note": "Patient presents for routine screening. Performed comprehensive metabolic panel. Diagnoses: Essential Hypertension (I10)."
    },
    {
        "name": "Edge Case - Unbundling Attempt",
        "note": "Performed diagnostic upper GI endoscopy. Also performed upper GI endoscopy with biopsy. No modifier 59 applied. Diagnoses: Gastro-esophageal reflux disease without esophagitis (K21.9)."
    },
    {
        "name": "Edge Case - Missing Medical Necessity",
        "note": "Patient presents with headache. Ordered MRI Brain without contrast. Diagnoses: Headache (R51.9)."
    }
]

def run_demo():
    app = create_mediagent_workflow()
    
    print("====================================")
    print("MediAgent Healthcare Operations Demo")
    print("====================================\n")
    
    for i, case in enumerate(clinical_notes):
        print(f"--- Running Case {i+1}: {case['name']} ---")
        print(f"Clinical Note: {case['note']}")
        
        initial_state = {
            "clinical_note": case["note"],
            "extracted_codes": [],
            "validation_issues": [],
            "prior_auth_status": "Not Checked",
            "guardrail_flags": [],
            "audit_trail": [],
            "overall_status": "Processing"
        }
        
        # Execute the LangGraph workflow
        result = app.invoke(initial_state)
        
        print(f"\nExtracted Codes: {json.dumps(result.get('extracted_codes'), indent=2)}")
        print(f"Guardrail Flags: {result.get('guardrail_flags')}")
        print(f"Prior Auth Status: {result.get('prior_auth_status')}")
        print(f"Final Status: {result.get('overall_status')}")
        print("\nAudit log updated in audit_log.json")
        print("---------------------------------------------------\n")

if __name__ == "__main__":
    run_demo()
