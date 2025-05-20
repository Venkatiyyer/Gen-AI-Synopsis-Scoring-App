import os
import io
import fitz  # PyMuPDF
import faiss
import numpy as np

from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional, IO

from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from anonymize import anonymizer  # Presidio-based anonymizer

# Paths to store FAISS indices
ARTICLE_PATH = "db/article_docs_faiss"
SYNOPSIS_PATH = "db/synopsis_faiss"
SYNOPSIS_FILE = os.path.join(SYNOPSIS_PATH, "synopsis_anon.txt")

# In-memory storage for anonymized synopsis text
global_synopsis_anon: str = ""

# ─── Init ─────────────────────────────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# # Storing Synopsis
# synopsis_anon = None

# Setup the LLM
llm = ChatGroq(
    model_name="llama-3.3-70b-versatile",
    temperature=0.2,
    groq_api_key=GROQ_API_KEY
)

# # Prompt template for synopsis evaluation
# prompt_template = PromptTemplate(
#     input_variables=["article", "synopsis"],
#     template="""
# You are an expert evaluator. Given the ANONYMIZED article and its ANONYMIZED user-written synopsis, score the synopsis on three dimensions and provide feedback.

# Article:
# {article}

# Synopsis:
# {synopsis}

# Return:
# - Overall Score (0-100)
# - Qualitative feedback (2-3 lines)
# """
# )

# Prompt template for synopsis evaluation
prompt_template = PromptTemplate(
    input_variables=["article", "synopsis"],
      template="""
      
      
You are a privacy‐conscious GenAI evaluator. You will compare the ANONYMIZED article and its ANONYMIZED user‐submitted synopsis and produce:


1. Overall Score out of 100, allocated as:
   - Relevance: 0–25
   - Content Coverage: 0–35
   - Coherence: 0–20
   - Clarity: 0–20
   
2. Visual breakdown, for example:
Relevance: 20/25
Content Coverage: 30/35
Coherence: 18/20
Clarity: 17/20

3. Brief qualitative feedback (2–3 lines) on the synopsis quality.

Article (anonymized):
{article}

Synopsis (anonymized):
{synopsis}

Return your response strictly in the following format:

Overall Score: XX/100

Breakdown:

- Relevance: __/25
- Content Coverage: __/35
- Coherence: __/20
- Clarity: __/20


Feedback:
- …
- …
- (optional) …

— End of response —

"""
)


# Embeddings for FAISS
embeddings = HuggingFaceEmbeddings(model_name="paraphrase-MiniLM-L6-v2")

# ─── Utils ────────────────────────────────────────────────────────────────────
def chunk_text(text: str) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return [Document(page_content=chunk) for chunk in splitter.split_text(text)]


def extract_text_from_file(uploaded_file) -> str:
    content = uploaded_file.read()
    if uploaded_file.name.lower().endswith(".pdf"):
        pdf = fitz.open(stream=content, filetype="pdf")
        return "".join(page.get_text() for page in pdf)
    elif uploaded_file.name.lower().endswith(".txt"):
        return content.decode("utf-8")
    else:
        raise ValueError("Unsupported file format. Only PDF or TXT allowed.")


# ─── Ingestion ───────────────────────────────────────────────────────────────
def extract_and_store_in_faiss(article_file, synopsis_file: Optional[IO] = None) -> dict:
    global global_synopsis_anon     # ← declare here!

    try:
        # Read and anonymize article
        raw_article = extract_text_from_file(article_file)
        article_anon = anonymizer(raw_article)
        article_chunks = chunk_text(article_anon)
        article_store = FAISS.from_documents(article_chunks, embeddings)
        os.makedirs(ARTICLE_PATH, exist_ok=True)
        article_store.save_local(ARTICLE_PATH)

        # synopsis_anon = None
        if synopsis_file:
            # Read and anonymize synopsis
            raw_synopsis = extract_text_from_file(synopsis_file)
            synopsis_anon = anonymizer(raw_synopsis)
            global_synopsis_anon = synopsis_anon
            synopsis_chunks = chunk_text(synopsis_anon)
            synopsis_store = FAISS.from_documents(synopsis_chunks, embeddings)
            os.makedirs(SYNOPSIS_PATH, exist_ok=True)
            synopsis_store.save_local(SYNOPSIS_PATH)
            
            # # Save raw anonymized synopsis for later evaluation
            
            # with open(SYNOPSIS_FILE, "w", encoding="utf-8") as f:
            #     f.write(synopsis_anon)

        return {"status": "success", "article_anon": article_anon, "synopsis_anon": synopsis_anon}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ─── Evaluate Synopsis ─────────────────────────────────────────────────────────
@staticmethod
def evaluate_synopsis() -> str:
    # # # Anonymize user synopsis
    # syn_anon = anonymizer(synopsis)

    # Load article index
    if not os.path.isdir(ARTICLE_PATH) or not os.listdir(ARTICLE_PATH):
        raise RuntimeError(f"Article FAISS index missing at '{ARTICLE_PATH}'. Upload article first.")
    article_store = FAISS.load_local(ARTICLE_PATH, embeddings, allow_dangerous_deserialization=True)
    
    #  # Load anonymized synopsis text
    # if not os.path.exists(SYNOPSIS_FILE):
    #     raise RuntimeError(f"Anonymized synopsis file missing at '{SYNOPSIS_FILE}'. Upload synopsis first.")
    # with open(SYNOPSIS_FILE, "r", encoding="utf-8") as f:
    #     synopsis_anon = f.read()
    
    # Storing var global_synopsis_anon
    synopsis_anon = global_synopsis_anon

    # Retrieve relevant article chunks for context
    examples = article_store.similarity_search(synopsis_anon, k=3)
    article_ctx = "\n".join(doc.page_content for doc in examples)

    # Build prompt
    prompt = prompt_template.format(article=article_ctx, synopsis=synopsis_anon)

    # Invoke LLM
    response = llm.invoke([{"role": "user", "content": prompt}]).content
    return{"result":response, "article": article_ctx, "synopsis":synopsis_anon}
