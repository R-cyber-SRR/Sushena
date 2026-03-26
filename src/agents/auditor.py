import json
import os
import datetime
from typing import Dict, Any
from src.state import AgentState

def write_audit_log(state: AgentState) -> Dict[str, Any]:
    """ Dedicated node at the end to dump logging to a file """
    trail = state.get("audit_trail", [])
    
    # Usually we might persist into a DB, here we'll write to a file
    # Ensure it doesn't just overwrite without history, though for demo
    # we can append or just overwrite per run. Let's do a timestamped file or a single file append.
    # To keep the demo clean, we'll write to `audit_log.json` by overwriting for each run.
    path = os.path.join(os.path.dirname(__file__), "../../audit_log.json")
    
    summary = {
        "timestamp": datetime.datetime.now().isoformat(),
        "overall_status": state.get("overall_status", "Processing"),
        "guardrail_flags": state.get("guardrail_flags", []),
        "validation_issues": state.get("validation_issues", []),
        "prior_auth_status": state.get("prior_auth_status", ""),
        "audit_trail": trail
    }
    
    with open(path, "w") as f:
        json.dump(summary, f, indent=2)
        
    return {} # No changes to state.
