from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.agents.extractor import extract_codes_node
from src.agents.validator import validate_codes_node
from src.agents.prior_auth import prior_auth_node
from src.agents.auditor import write_audit_log

def create_mediagent_workflow():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("extractor", extract_codes_node)
    workflow.add_node("validator", validate_codes_node)
    workflow.add_node("prior_auth", prior_auth_node)
    workflow.add_node("auditor", write_audit_log)
    
    # Define edges and conditional routing
    workflow.add_edge(START, "extractor")
    workflow.add_edge("extractor", "validator")
    
    # Guardrail router
    def route_after_validation(state: AgentState):
        if state.get("overall_status") == "Escalated to Human":
            return "auditor"  # Skip straight to audit if hard failure
        return "prior_auth"
        
    workflow.add_conditional_edges("validator", route_after_validation)
    
    # After prior auth, always audit
    workflow.add_edge("prior_auth", "auditor")
    workflow.add_edge("auditor", END)
    
    # Compile
    app = workflow.compile()
    return app
