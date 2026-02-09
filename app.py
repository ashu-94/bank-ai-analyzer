from fastapi import FastAPI, UploadFile, File, HTTPException
from openai import AzureOpenAI
from pypdf import PdfReader
from dotenv import load_dotenv
from pathlib import Path
import os
import tempfile
import json
from pydantic import BaseModel
from typing import List, Optional

# ==========================================
# ✅ Load ENV FIRST
# ==========================================

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

# ==========================================
# ✅ FastAPI Metadata (Makes Docs Look Senior)
# ==========================================

app = FastAPI(
    title="AI Bank Statement Analyzer",
    description="Production-ready FastAPI service that extracts structured financial data from bank statements using Azure OpenAI.",
    version="1.0.0"
)

# ==========================================
# ✅ Response Models
# ==========================================

class Address(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None


class AccountDetails(BaseModel):
    account_holder: Optional[str] = None
    address: Optional[Address] = None
    account_number: Optional[str] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None


class Transaction(BaseModel):
    date: Optional[str] = None
    description: Optional[str] = None
    debit: Optional[float] = None
    credit: Optional[float] = None
    balance: Optional[float] = None


class BankStatementResponse(BaseModel):
    account_details: Optional[AccountDetails] = None
    transactions: List[Transaction] = []
    message: str


# ==========================================
# ✅ Validate ENV (Fail Fast — Senior Practice)
# ==========================================

AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_VERSION = os.getenv("OPENAI_API_VERSION")
DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")

missing = [k for k, v in {
    "AZURE_OPENAI_KEY": AZURE_KEY,
    "AZURE_OPENAI_ENDPOINT": AZURE_ENDPOINT,
    "OPENAI_API_VERSION": API_VERSION,
    "AZURE_DEPLOYMENT": DEPLOYMENT
}.items() if not v]

if missing:
    raise ValueError(f"Missing environment variables: {missing}")

# ==========================================
# ✅ Azure Client
# ==========================================

client = AzureOpenAI(
    api_key=AZURE_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    api_version=API_VERSION
)

# ==========================================
# ✅ Utility Function — Extract PDF Text
# ==========================================

def extract_pdf_text(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)

        text_pages = [
            page.extract_text()
            for page in reader.pages
            if page.extract_text()
        ]

        final_text = "\n".join(text_pages)

        if not final_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No readable text found in PDF."
            )

        return final_text

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF extraction failed: {str(e)}"
        )

# ==========================================
# ✅ Root Endpoint (Recruiter Trick)
# ==========================================

@app.get("/")
def root():
    return {
        "message": "AI Bank Statement Analyzer API is running.",
        "docs": "/docs",
        "health": "/health"
    }

# ==========================================
# ✅ Health Endpoint
# ==========================================

@app.get("/health")
def health():
    return {"status": "ok"}

# ==========================================
# ✅ MAIN ENDPOINT
# ==========================================

@app.post(
    "/analyze-bank-statement",
    response_model=BankStatementResponse,
    summary="Analyze Bank Statement",
    description="Upload a bank statement PDF and extract structured transaction data using Azure OpenAI."
)
async def analyze_bank_statement(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    tmp_path = None

    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        pdf_text = extract_pdf_text(tmp_path)

        prompt = f"""
Extract structured data from this bank statement.

Return ONLY valid JSON matching this schema:

{{
  "account_details": {{
    "account_holder": "",
    "account_number": "",
    "account_type": "",
    "currency": ""
  }},
  "transactions": [
    {{
      "date": "",
      "description": "",
      "debit": 0,
      "credit": 0,
      "balance": 0
    }}
  ]
}}

Bank Statement:
{pdf_text}
"""

        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=[
                {
                    "role": "system",
                    "content": "You are a financial document parser that outputs strictly valid JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content.strip()

        # Remove markdown if present
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        try:
            parsed_json = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail="Model returned invalid JSON."
            )

        return BankStatementResponse(
            account_details=parsed_json.get("account_details"),
            transactions=parsed_json.get("transactions", []),
            message="Bank statement processed successfully."
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Azure/OpenAI Error: {str(e)}"
        )

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
