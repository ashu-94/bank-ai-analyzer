README.md

# 🏦 Bank AI Analyzer

 ## 🏷️ Badges

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Production-green)
![Azure OpenAI](https://img.shields.io/badge/Azure-OpenAI-purple)
![Status](https://img.shields.io/badge/Status-Active-success)
![API](https://img.shields.io/badge/API-Live-success)

## 🚀 Live Demo
👉 https://bank-ai-analyzer-1.onrender.com/docs

## 📘 Description

An enterprise-grade AI-powered financial analysis system that automatically extracts, categorizes, and generates 
insights from bank statements using FastAPI and Azure OpenAI.
Designed with production best practices including modular architecture, environment-based secrets management, and scalable API design.



## 🏗️ Architecture

User uploads bank statement → FastAPI processes the file →  
PyPDF extracts text → Azure OpenAI analyzes transactions →  
Structured insights returned via API.

## 🚀 Live Capabilities
- Upload bank statements (PDF)
- Extract transactions automatically
- AI-powered financial insights
- Detect spending patterns
- Production-ready API

---

## 🚀 Features
- AI-powered transaction analysis
- PDF bank statement parsing
- Secure API key management with environment variables
- FastAPI-based scalable backend
- Cloud deployment ready

- ## 🧠 AI Capabilities

- Intelligent transaction classification  
- Spending behavior detection  
- Financial pattern recognition  
- Automated insight generation using LLM  


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



