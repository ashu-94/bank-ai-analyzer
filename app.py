from fastapi import FastAPI, UploadFile, File, HTTPException
from openai import AzureOpenAI
from pypdf import PdfReader
from dotenv import load_dotenv
from pathlib import Path
import os
import tempfile
import json

# ✅ Load ENV first
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

app = FastAPI()

# ✅ MODEL SECTION (KEEP THEM TOGETHER)

from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None


class AccountDetails(BaseModel):
    account_holder: str | None = None
    address: Address | None = None
    account_number: str | None = None
    account_type: str | None = None
    currency: str | None = None


class Transaction(BaseModel):
    date: str | None = None
    description: str | None = None
    debit: float | None = None
    credit: float | None = None
    balance: float | None = None


class BankStatementResponse(BaseModel):
    account_details: AccountDetails | None = None
    transactions: List[Transaction] = []   # ⭐ better than None

# ==========================================
# ✅ Validate ENV (FAIL FAST — Production Style)
# ==========================================

AZURE_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
API_VERSION = os.getenv("OPENAI_API_VERSION")
DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")

print("✅ DEPLOYMENT:", DEPLOYMENT)
print("✅ VERSION:", API_VERSION)
print("✅ ENDPOINT:", AZURE_ENDPOINT)

if not AZURE_KEY:
    raise ValueError("❌ AZURE_OPENAI_KEY is missing in .env")

if not AZURE_ENDPOINT:
    raise ValueError("❌ AZURE_OPENAI_ENDPOINT is missing in .env")

if not API_VERSION:
    raise ValueError("❌ OPENAI_API_VERSION is missing in .env")

if not DEPLOYMENT:
    raise ValueError("❌ AZURE_DEPLOYMENT is missing in .env")


# ==========================================
# ✅ Azure Client (Use validated vars — Senior practice)
# ==========================================

client = AzureOpenAI(
    api_key=AZURE_KEY,
    azure_endpoint=AZURE_ENDPOINT,
    api_version=API_VERSION
)


# ==========================================
# ✅ Utility Function — Extract PDF Text
# (NO recursion, NO duplication)
# ==========================================

def extract_pdf_text(file_path: str) -> str:
    try:
        reader = PdfReader(file_path)

        text = []

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text.append(extracted)

        final_text = "\n".join(text)

        if not final_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from PDF."
            )

        return final_text

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PDF extraction failed: {str(e)}"
        )


# ==========================================
# ✅ API Endpoint
# ==========================================

@app.post("/analyze-bank-statement", response_model=BankStatementResponse)
async def analyze_pdf(file: UploadFile = File(...)):

    tmp_path = None

    try:
        # ✅ Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # ✅ Extract PDF text
        pdf_text = extract_pdf_text(tmp_path)

        prompt = f"""
Extract structured data from this bank statement.

Return ONLY valid JSON.

Bank Statement:
{pdf_text}
"""

        # ✅ Azure OpenAI Call
        response = client.chat.completions.create(
            model=os.getenv("AZURE_DEPLOYMENT")
,  # MUST match Azure deployment name
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

        # ✅ Remove markdown safely
        if content.startswith("```"):
            content = content.replace("```json", "").replace("```", "").strip()

        # ✅ Validate JSON
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=500,
                detail=f"Model returned invalid JSON:\n{content}"
            )

        return result


    except HTTPException as http_err:
        raise http_err

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Azure/OpenAI Error: {str(e)}"
        )

    finally:
        # ✅ Always cleanup temp file
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
