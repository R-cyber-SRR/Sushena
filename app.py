import os
import json
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from src.workflow import create_mediagent_workflow

import firebase_admin
from firebase_admin import credentials, auth, firestore

# Initialize Firebase Admin SDK (guard against double-init during reload)
SERVICE_ACCOUNT_PATH = os.path.join(
    os.path.dirname(__file__),
    "ethackathon-c2eeb-firebase-adminsdk-fbsvc-13b4e3ad98.json"
)
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

app = FastAPI(title="Sushena API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Firebase Auth Dependency ---
async def get_current_user(request: Request) -> dict:
    """Verify Firebase ID token from Authorization header."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    id_token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid Firebase token: {str(e)}")


class NoteRequest(BaseModel):
    clinical_note: str

# Create workflow instance globally for reuse
workflow_app = create_mediagent_workflow()

@app.post("/api/process")
async def process_note(
    request: NoteRequest,
    user: dict = Depends(get_current_user)
):
    initial_state = {
        "clinical_note": request.clinical_note,
        "extracted_codes": [],
        "validation_issues": [],
        "prior_auth_status": "Not Checked",
        "guardrail_flags": [],
        "audit_trail": [],
        "overall_status": "Processing"
    }

    # Run langgraph workflow execution
    try:
        result = workflow_app.invoke(initial_state)

        # Save to Firestore under user's UID
        doc_ref = db.collection("clinical_notes").document()
        doc_ref.set({
            "user_id": user["uid"],
            "user_email": user.get("email", "unknown"),
            "raw_note": request.clinical_note,
            "extracted_codes": result.get("extracted_codes"),
            "guardrail_flags": result.get("guardrail_flags"),
            "prior_auth_status": result.get("prior_auth_status"),
            "overall_status": result.get("overall_status"),
            "audit_trail": result.get("audit_trail"),
        })

        return {
            "status": "success",
            "data": result,
            "record_id": doc_ref.id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- User History Endpoint ---
@app.get("/api/history")
async def get_history(user: dict = Depends(get_current_user)):
    """Get clinical note history for the current user."""
    try:
        docs = db.collection("clinical_notes").where("user_id", "==", user["uid"]).stream()
        history = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            history.append(d)
        return {"status": "success", "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Connect Frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")
os.makedirs(FRONTEND_DIR, exist_ok=True)

# Important rule for static generation, index.html is expected here
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)
