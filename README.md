# Nonprofit Narrative Researcher: Agentic AI for Strategic Storytelling

[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-blue)](https://langchain-ai.github.io/langgraph/)
[![Gemini 3.1 Pro](https://img.shields.io/badge/AI-Gemini%203.1%20Pro-orange)](https://deepmind.google/technologies/gemini/)
[![React](https://img.shields.io/badge/Frontend-React%2019-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![Digital Public Infrastructure](https://img.shields.io/badge/Category-Digital%20Public%20Infrastructure-green)](#)

**Nonprofit Narrative Researcher** is an autonomous, agentic research engine designed to help mission-driven organizations synthesize their impact and identify strategic narrative gaps. By leveraging **LangGraph** for multi-agent orchestration and **Google Gemini 3.1 Pro**, it performs deep, iterative research across the web to build a verifiable, cited narrative of an organization's work and its place in the broader ecosystem.
...
- **AI Models:** Google Gemini 3.1 Pro & 3.1 Flash-Lite.

This project serves as a **Reference Architecture** for how nonprofits can utilize Agentic AI to bridge the "data-narrative gap." In a landscape where mission-driven work is often buried in unstructured reports and disparate web pages, this tool acts as a piece of **Digital Public Infrastructure (DPI)**—a reusable, verifiable research layer that ensures organizational storytelling is grounded in high-fidelity data.

## ✨ Key Features

- **🧠 Autonomous Agentic Orchestration:** Built on LangGraph to manage complex, non-deterministic research workflows with stateful memory.
- **🤔 Self-Correcting Reflection Loops:** Features a specialized "Knowledge Gap Analysis" node that programmatically evaluates research sufficiency, triggering iterative refinements until a high-confidence answer is achieved.
- **🔍 Parallelized Discovery:** Utilizes fan-out/fan-in patterns to simultaneously triage multiple internal and external URLs, significantly accelerating the research lifecycle.
- **📄 Verifiable Synthesis:** Generates comprehensive narrative reports with inline citations, ensuring every claim is backed by a primary web source.
- **🛡️ Enterprise-Ready Backend:** A FastAPI-powered backend designed for scalability, including Docker support for seamless deployment.

## 🏗 Architecture

The core logic resides in a state-machine graph (`backend/src/agent/graph.py`):

1. **URL Extraction:** Identifies the primary target domain and research intent.
2. **Discovery & Triage:** Scrapes the site tree and triages "Critical Pages" (Impact reports, About pages, Partner lists).
3. **Parallel Scrape:** Concurrently ingests content from multiple prioritized pages.
4. **Evaluation:** An LLM-based reflection step identifies knowledge gaps or contradictions.
5. **Iterative Refinement:** If research is insufficient, the agent dynamically generates new search terms and returns to the discovery phase.
6. **Narrative Synthesis:** Final synthesis of the gathered data into a structured report.

## 🛠 Tech Stack

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Shadcn UI.
- **Backend:** Python 3.11+, LangGraph, FastAPI, LangChain.
- **AI Models:** Google Gemini 3.1 Pro & 3.1 Flash-Lite.
- **Infrastructure:** Docker, Makefile for rapid development.

## 🚦 Getting Started

### Prerequisites
- Python 3.11+
- Node.js (v18+)
- [Google Gemini API Key](https://aistudio.google.com/)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
pip install .
# Create a .env file with your GEMINI_API_KEY
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 3. Rapid Dev
```bash
# From the root directory
make dev
```

## 📜 License

Distributed under the Apache License 2.0. See `LICENSE` for more information.

---
*Built to explore the intersection of Agentic AI and Social Impact.*
