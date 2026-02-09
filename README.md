README.md

# 🏦 Bank AI Analyzer

Production-ready FastAPI AI system that analyzes bank statements using Azure OpenAI.

## 🏗️ Architecture

User uploads bank statement → FastAPI processes the file →  
PyPDF extracts text → Azure OpenAI analyzes transactions →  
Structured insights returned via API.

##Badge

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green)
![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-purple)
![Status](https://img.shields.io/badge/Status-Active-success)



## 🚀 Features
- AI-powered transaction analysis
- PDF bank statement parsing
- Secure API key management with environment variables
- FastAPI-based scalable backend
- Cloud deployment ready

## 🛠 Tech Stack
- FastAPI
- Azure OpenAI
- Python
- PyPDF
- Uvicorn

## 📡 API Docs
Once deployed:

👉 /docs provides interactive Swagger UI.

## 🔐 Security
API keys are stored securely using environment variables and are never pushed to GitHub.

## 🚀 How to Run Locally

```bash
git clone https://github.com/ashu-94/bank-ai-analyzer.git
cd bank-ai-analyzer
pip install -r requirements.txt
uvicorn app:app --reload


---
Built by Ashutosh Kumar 🚀



