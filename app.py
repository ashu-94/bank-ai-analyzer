from fastapi import FastAPI, UploadFile, File
from openai import AzureOpenAI
from pypdf import PdfReader
import os
import tempfile
import json

app = FastAPI()

# ✅ Azure OpenAI Client
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-05-01-preview",   # safer version
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)


# ✅ Function to extract text from PDF
def extract_pdf_text(file_path):
    reader = PdfReader(file_path)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    return text


# ✅ API Endpoint
@app.post("/analyze-bank-statement")
async def analyze_pdf(file: UploadFile = File(...)):

    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        # Extract text
        reader = PdfReader(tmp_path)
        pdf_text = ""

        for page in reader.pages:
            pdf_text += page.extract_text()

        prompt = f"""
        Extract structured data from this bank statement and return ONLY JSON.

        Bank Statement:
        {pdf_text}
        """

        response = client.chat.completions.create(
            model="gpt-4o",  # your deployment name
            messages=[
                {"role": "system", "content": "You are a financial document parser."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        content = response.choices[0].message.content

        # Remove markdown if model wraps JSON
        content = content.replace("```json", "").replace("```", "").strip()

        result = json.loads(content)

        return result   # ✅ INSIDE function

    except Exception as e:
        return {"error": str(e)}



