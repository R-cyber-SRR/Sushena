import operator
from typing import TypedDict, Annotated, List, Dict, Any, Optional
from pydantic import BaseModel, Field

class ExtractedEntity(BaseModel):
    code: str = Field(description="The formal code, e.g., ICD-10 or CPT code")
    description: str = Field(description="Text description of the diagnosis or procedure")
    type: str = Field(description="'ICD-10' or 'CPT'")
    modifier: Optional[str] = Field(default=None, description="Any CPT code modifiers, if applicable (e.g., '25', '59')")

class ValidationIssue(BaseModel):
    issue_type: str = Field(description="'Unbundling Risk', 'Diagnosis Mismatch', 'Missing Modifier', 'Expired Code', etc.")
    severity: str = Field(description="'High', 'Medium', 'Low'")
    description: str = Field(description="Detailed explanation of the issue rule that was violated")
    codes_involved: List[str] = Field(description="List of codes involved in this failure")

class AuditEvent(BaseModel):
    agent: str = Field(description="Name of the agent taking action (e.g., 'CodeExtractorAgent')")
    action: str = Field(description="Description of what was done")
    rule_applied: str = Field(description="The specific guardrail, policy, or logic rule used")
    reason: str = Field(description="Why this rule applied based on the data")
    fallback: str = Field(description="What should be done if this fails or edge case triggered")

class AgentState(TypedDict):
    clinical_note: str
    extracted_codes: List[Dict[str, Any]]
    validation_issues: List[Dict[str, Any]]
    prior_auth_status: str # 'Not Checked', 'Approved', 'Denied', 'Escalated'
    guardrail_flags: List[str]
    audit_trail: Annotated[List[Dict[str, Any]], operator.add]
    overall_status: str # 'Processing', 'Approved', 'Escalated to Human', 'Rejected'
