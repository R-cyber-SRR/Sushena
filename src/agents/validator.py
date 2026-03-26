import json
import os
from typing import Dict, Any
from src.state import AgentState

RULES_FILE = os.path.join(os.path.dirname(__file__), "../../data/mock_rules.json")
with open(RULES_FILE, "r") as f:
    MOCK_RULES = json.load(f)

def validate_codes_node(state: AgentState) -> Dict[str, Any]:
    extracted = state.get("extracted_codes", [])
    
    icd10_codes = [c["code"] for c in extracted if c.get("type", "") == "ICD-10"]
    cpt_codes = [c["code"] for c in extracted if c.get("type", "") == "CPT"]

    issues = []
    guardrail_flags = []
    
    # 1. Check CPT Bundling (NCCI Edits)
    for rule in MOCK_RULES["cpt_bundles"]:
        if rule["comprehensive_code"] in cpt_codes and rule["component_code"] in cpt_codes:
            component_has_59 = False
            for c in extracted:
                if c.get("code") == rule["component_code"] and c.get("modifier") == "59":
                    component_has_59 = True
                    break
            
            if not component_has_59:
                issues.append({
                    "issue_type": "Unbundling Risk",
                    "severity": "High",
                    "description": rule["rationale"] + " Missing modifier 59.",
                    "codes_involved": [rule["comprehensive_code"], rule["component_code"]]
                })
                guardrail_flags.append("BUNDLING_VIOLATION_DETECTED")
    
    # 2. Check CMS LCD/NCD
    for rule in MOCK_RULES["cms_lcd_ncd"]:
        if rule["procedure_code"] in cpt_codes:
            has_allowed_dx = False
            for dx in icd10_codes:
                if dx in rule["allowed_diagnoses"]:
                    has_allowed_dx = True
                    break
            
            if not has_allowed_dx:
                issues.append({
                    "issue_type": "Diagnosis Mismatch",
                    "severity": "High",
                    "description": rule["rationale"],
                    "codes_involved": [rule["procedure_code"]]
                })
                guardrail_flags.append("MEDICAL_NECESSITY_VIOLATION")

    audit_ev = {
        "agent": "ComplianceValidatorAgent",
        "action": f"Validated {len(cpt_codes)} CPT combinations and LCD/NCD overlaps.",
        "rule_applied": "CMS MUE / NCCI edits subset",
        "reason": f"Found {len(issues)} compliance issues.",
        "fallback": "Escalate to human if High severity rule violation occurs or rule is ambiguous."
    }

    overall_status = state.get("overall_status", "Processing")
    if guardrail_flags:
        overall_status = "Escalated to Human"

    return {
        "validation_issues": issues,
        "guardrail_flags": guardrail_flags,
        "overall_status": overall_status,
        "audit_trail": [audit_ev]
    }
