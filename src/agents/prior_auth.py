import os
import json
from typing import Dict, Any
from src.state import AgentState

RULES_FILE = os.path.join(os.path.dirname(__file__), "../../data/mock_rules.json")
with open(RULES_FILE, "r") as f:
    MOCK_RULES = json.load(f)

def prior_auth_node(state: AgentState) -> Dict[str, Any]:
    if state.get("overall_status") == "Escalated to Human":
        return {
            "prior_auth_status": "Escalated",
            "audit_trail": [{
                "agent": "PriorAuthAgent",
                "action": "Skipped checking prior auth requirements",
                "rule_applied": "Guardrail Halt",
                "reason": "Previous agent triggered hard guardrail escalation.",
                "fallback": "None"
            }]
        }

    extracted = state.get("extracted_codes", [])
    cpt_codes = [c["code"] for c in extracted if c.get("type", "") == "CPT"]
            
    needs_auth = False
    reasons = []
    
    for rule in MOCK_RULES["cms_lcd_ncd"]:
        if rule.get("requires_prior_auth") and rule["procedure_code"] in cpt_codes:
            needs_auth = True
            reasons.append(f"Procedure {rule['procedure_code']} requires prior auth based on NCD.")
            
    audit_ev = {
        "agent": "PriorAuthAgent",
        "action": "Checked prior authorization requirements.",
        "rule_applied": "Payer Policy Decision Tree",
        "reason": " | ".join(reasons) if needs_auth else "No codes requiring PA found.",
        "fallback": "Pend claim and escalate."
    }
    
    status = "Approved"
    if needs_auth:
        status = "Escalated"
        
    overall_status = state.get("overall_status", "Processing")
    if status == "Escalated":
        overall_status = "Escalated to Human"
        
    return {
        "prior_auth_status": status,
        "overall_status": overall_status,
        "audit_trail": [audit_ev]
    }
