## AI Resume Analyzer + Job Matcher (Local LLM + RAG)

End-to-end local, privacy-friendly resume analyzer and job matcher using FastAPI, Streamlit, FAISS, sentence-transformers, spaCy, scikit-learn, and Ollama (llama3:8b).

### Features

- **Resume upload** (PDF or text), parsing and storage
- **Job description input** and skill extraction
- **Semantic job matching** with FAISS + sentence-transformers
- **ATS-style scoring** (keywords, similarity, sections)
- **Skill gap analysis** and **learning roadmap** (30/60/90 days) via local LLM
- **Explainability**: matched/missing skills and keywords, score breakdown

### Project Structure

- **backend/**
  - `main.py` – FastAPI app entrypoint
  - `routes/` – API route modules
  - `services/` – parsing, embeddings, vector store, ATS, skills, LLM
  - `models/schemas.py` – Pydantic request/response models
- **frontend/**
  - `streamlit_app.py` – Streamlit UI
- **data/**
  - `resumes/` – stored resumes and extracted text
  - `faiss_index/` – FAISS index + metadata files
  - `samples/` – sample resume and job description

### Prerequisites

- **Python** 3.10+
- **Ollama** installed locally
- **Model**: `llama3:8b` pulled in Ollama

Install Ollama and model (from a terminal):

```bash
ollama pull llama3:8b
ollama serve
```

Ollama will listen on `http://localhost:11434`.

### Setup

From the project root:

```bash
python -m venv .venv
.venv\Scripts\activate  # on Windows

pip install --upgrade pip
pip install -r requirements.txt
```

Download the spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

### Running the Backend (FastAPI)

From the project root:

```bash
uvicorn backend.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

Key endpoints:

- `POST /upload-resume` – upload a resume (PDF or text)
- `POST /analyze` – analyze a resume vs job description
- `GET /results/{id}` – fetch previously computed analysis

### Running the Frontend (Streamlit)

From the project root:

```bash
streamlit run frontend/streamlit_app.py
```

The UI will open at `http://localhost:8501`.

### Using the App

1. **Upload resume**
   - Upload a PDF or text resume.
   - The backend extracts text, chunks it, and builds a FAISS index.
2. **Paste job description**
   - Paste the full job description text into the text area.
3. **Click "Analyze"**
   - The app will:
     - Extract skills from resume and job description.
     - Compute semantic similarity and ATS-style score.
     - Query the local LLM (via Ollama) for:
       - Skill gap analysis and strengths.
       - 30/60/90-day learning roadmap.
       - ATS improvement suggestions.
4. **Review results**
   - Tabs:
     - **Match Score** – overall match %, similarity and scores.
     - **Skills Analysis** – matched vs missing skills/tools.
     - **ATS Feedback** – score breakdown, keyword coverage.
     - **Learning Roadmap** – 30/60/90-day plan and LLM reasoning.

### Sample Data

Sample files live under `data/samples/`:

- `sample_resume.txt` – example resume text.
- `sample_job_description.txt` – example job description.

You can:

- Upload `sample_resume.txt` directly (or convert it to a PDF in your editor and upload that).
- Paste `sample_job_description.txt` contents into the job description text area.

### Notes on Local LLM Integration

- The backend integrates with Ollama via HTTP:
  - `POST http://localhost:11434/api/chat`
- The helper in `backend/services/llm_service.py` exposes:
  - `chat(messages)` – low-level chat interface.
  - `complete(prompt)` – convenience wrapper.
- If Ollama is not running or the model is not available, LLM-dependent features will return informative error messages instead of crashing.

### Troubleshooting

- **Ollama not running**
  - Ensure `ollama serve` is running and the `llama3:8b` model is pulled.
- **spaCy model error**
  - If you see an error about `en_core_web_sm`, run:
    ```bash
    python -m spacy download en_core_web_sm
    ```
- **Slow first inference**
  - The first call to the embedding model and LLM can be slow due to model loading; subsequent calls should be faster.

### License

This project is intended as a local, educational reference for AI-powered resume analysis and job matching. Adapt for your own use as needed.

