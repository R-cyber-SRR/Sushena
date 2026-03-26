# MediAgent

MediAgent is an AI agent system for healthcare operations that handles medical coding, claims adjudication, and prior authorization workflows. The system navigates ICD-10/CPT code sets, evaluates payer-specific policies, and enforces strict regulatory guardrails with fully auditable reasoning via LangGraph.

## Architecture

See `docs/architecture.md` and `docs/impact_model.md` for in-depth details.

- **CodeExtractorAgent**: Extracts ICD-10 and CPT codes from free-text clinical notes.
- **ComplianceValidatorAgent**: Cross-references against static rules for NCCI (bundling) and CMS NCD/LCD policies.
- **PriorAuthAgent**: Decision tree integration for prior auth checks.
- **AuditLoggerAgent**: Appends structured JSON footprints of all rule evaluations and escalations.

## Setup Instructions

1. **Virtual Environment & Dependencies**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file at the root or correctly export `OPENAI_API_KEY`.
   ```bash
   export OPENAI_API_KEY="sk-proj-..."
   ```

3. **Run the Demo Workflow**:
   ```bash
   python demo.py
   ```
   
   Running this script processes 3 sample cases:
   - Standard clear medical case
   - Unbundling risk attempt 
   - Non-covered diagnosis (Missing medical necessity)

4. **View Audits**:
   Inspect `audit_log.json` to see the exact rules applied, rationale, and status changes for each execution block.

## Local AI Integration (Ollama)

MediAgent has been updated to use local open-source models (Qwen2.5 1.5B) via Ollama, removing the need for a paid ChatGPT plan.

1. **Install Ollama**: Download from [ollama.com](https://ollama.com)
2. **Start Ollama Server**: 
   ```bash
   ollama serve
   ```
3. **Pull the Model**:
   ```bash
   ollama run qwen2.5:1.5b
;   ```
Ensure Ollama is running in the background before processing a clinical note through the app!

## Deployment

To host this project online (e.g. Render, AWS, Railway), we have provided a standard `Dockerfile`.

1. **Build the container**:
   ```bash
   docker build -t mediagent .
   ```
2. **Run the container**:
   ```bash
   docker run -d -p 8000:8000 mediagent
   ```
   
*Note: Depending on your host setup, you may need to point your deployed container to an external Ollama URL if your host machine does not have a GPU.*
