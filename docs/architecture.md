# MediAgent Architecture

## Overview
MediAgent utilizes **LangGraph** to strictly manage state transitions and conditional logic, enabling a highly transparent, fully auditable multi-agent pipeline for healthcare claims processing. 

### Why LangGraph?
Unlike autonomous reflection loops (e.g. standard ReAct agents), healthcare claims require deterministic guardrails. LangGraph guarantees that if a condition is violated (e.g., Unbundling Risk), the workflow execution deterministically hits an `Escalate` state, completely bypassing `PriorAuth` and cleanly invoking an `AuditLog` shutdown sequence.

## Agent Design

1. **CodeExtractorAgent**: 
   - **Role**: Free-text NLP extraction.
   - **Mechanism**: LLM with strict Structured Output mapping clinical terms to exact ICD-10 and CPT schemas using prompt templates designed for high-precision recall.

2. **ComplianceValidatorAgent**: 
   - **Role**: Medical coding rules engine.
   - **Mechanism**: Loads deterministic constraints (mocked as `mock_rules.json`) mimicking CMS LCD/NCD overlaps (procedure-diagnosis linkage) and NCCI Edit Tables (bundling conflicts, e.g., upper GI biopsy with diagnostic upper GI). If an edit check fails, it raises a `High` severity alert and injects `BUNDLING_VIOLATION_DETECTED` into the `guardrail_flags`.

3. **PriorAuthAgent**: 
   - **Role**: Adjudication checking.
   - **Mechanism**: Re-evaluates CPT codes against prior-authorization checklists and flags if precertification was not obtained.

4. **AuditLoggerAgent**:
   - **Role**: Transparency endpoint.
   - **Mechanism**: A terminal node in the LangGraph that persists the `audit_trail` (an array of events pushed to state during execution) into `audit_log.json`. Every event strictly requires `action`, `rule`, `reason`, and `fallback` keys.
