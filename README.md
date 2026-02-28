# 🚀 AI Resume Analyzer + Job Matcher

An intelligent AI-powered recruitment assistant that analyzes resumes, extracts skills, performs ATS scoring, and matches candidates with the most relevant job roles using NLP, semantic search, and LLM-based insights.

📌 Features

📄 Resume parsing (PDF/DOCX)

🧠 AI-based skill extraction

🎯 ATS resume scoring

🤖 LLM-powered analysis

🔍 Semantic job–resume matching

📊 Skill gap identification

⚡ FastAPI backend with modular architecture

🗂️ Vector store for similarity search

🏗️ Project Architecture
backend
 ┣ models          → Data schemas
 ┣ routes          → API endpoints
 ┣ services        → Core AI logic
 ┃ ┣ ats_score.py
 ┃ ┣ embeddings.py
 ┃ ┣ llm_service.py
 ┃ ┣ parser.py
 ┃ ┣ skill_extractor.py
 ┃ ┗ vector_store.py
 ┣ main.py         → FastAPI app entry point
data               → Sample datasets (ignored in prod)
requirements.txt   → Dependencies
⚙️ Tech Stack

Backend: FastAPI, Python
AI/NLP:

Sentence Transformers / Embeddings

LLM integration

TF-IDF / Semantic similarity

Vector Database: FAISS / Chroma (based on your setup)
Other: Uvicorn, Pydantic

🔄 System Flow

Upload resume

Resume parsing

Skill extraction

Generate embeddings

ATS score calculation

Job matching via vector similarity

LLM-powered feedback & recommendations

📡 API Endpoints
🔹 Health Check
GET /health
🔹 Resume Analysis
POST /analyze
🔹 Job Matching
POST /match-job
🔹 ATS Score
POST /ats-score

👉 Interactive API docs available at:

http://127.0.0.1:8000/docs
🧪 Running Locally
1️⃣ Clone the repo
git clone https://github.com/your-username/AI-Resume-Analyzer-Job-Matcher.git
cd AI-Resume-Analyzer-Job-Matcher
2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate
3️⃣ Install dependencies
pip install -r requirements.txt
4️⃣ Start the server
uvicorn backend.main:app --reload
📊 Example Use Cases

Job seekers optimizing resumes for ATS

HR automated resume screening

Career recommendation systems

University placement platforms

🔐 Environment Variables

Create a .env file:

OPENAI_API_KEY=your_key_here
📸 Future Enhancements

🌐 Frontend dashboard

📂 Multiple resume comparison

🧾 Resume improvement suggestions

☁️ Cloud deployment (Docker + CI/CD)

🔎 Real-time job scraping

🤝 Contributing

Pull requests are welcome.
For major changes, please open an issue first.

📜 License

MIT License

⭐ Author

Mummadi Ranjith Kumar
🔗 GitHub: https://github.com/mummadiranjithkumar
