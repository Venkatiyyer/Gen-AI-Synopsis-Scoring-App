## GenAI Synopsis Scoring App

A Streamlit application that lets users upload an article and its synopsis, then returns a 0–100 score plus qualitative feedback based on coverage, coherence, and clarity.

---

### 📋 Prerequisites

- Python 3.10+  
- Git (for cloning the repo)  
- An OpenAI or Groq API key (if using LLM for feedback)

### 🔧 Installation

1. **Clone the repository**  
   ```bash
   git clone [https://github.com/Venkatiyyer/Gen-AI-Synopsis-Scoring-App]
   cd genai-synopsis-scoring-app
   ```

2. **Create & activate a virtual environment**  
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_lg
   ```

4. **Configure environment variables**  
   ```bash
   cp .env.example .env
   # Then edit .env to add GROQ_API_KEY and/or OPENAI_API_KEY
   ```

### 🚀 Usage

```bash
streamlit run app.py
```

- Upload an **article** file (`.txt` or `.pdf`), then a **synopsis** (`.txt`).  
- View the **score** and **feedback** in the Streamlit UI.

### 📂 Project Structure

```
genai_synopsis_app/
├── backend.py
├── anonymize.py      # Presidio-based PII removal
├── frontend.py          # Scoring & optional LLM feedback
├── requirements.txt
├── privacy_note.md    # Detailed privacy strategy
└── README.md
```

### 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
