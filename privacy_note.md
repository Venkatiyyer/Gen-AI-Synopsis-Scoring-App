# Scoring Methodology & Privacy Protection Strategy

## Scoring Methodology

Our scoring pipeline combines **semantic embeddings** with **readability metrics** to yield an interpretable 0–100 score:

1. **Coverage (0–50 points)**  
   - Compute cosine similarity between document and synopsis embeddings using a mini‑LM model.  
   - Scaled to 0–50 for direct interpretability.

2. **Coherence (0–25 points)**  
   - Split synopsis into sentences, compute pairwise embedding similarities, and average off‑diagonal values.  
   - Reflects logical flow across sentences.

3. **Clarity (0–25 points)**  
   - Use Flesch Reading Ease score to approximate readability, normalized to 0–25.  
   - Higher scores correspond to clearer, simpler phrasing.

Final score is the sum of these three components (max 100). Qualitative feedback is generated either via rule‑based thresholds or optionally via an LLM prompt for more nuanced comments.

## Privacy Protection Strategy

We follow rigorous privacy‑by‑design and data minimization principles:

- **Anonymization & De‑identification**  
  - All PII (names, titles, dates, locations, emails, phone numbers, SSNs, credit cards, URLs, IPs, pronouns) is stripped using Microsoft Presidio before any processing or storage.  
  - Custom pattern recognizers capture honorifics (e.g., “Mr.”, “Dr.”) and pronouns to prevent residual identifiers.

- **No Raw Data Persistence**  
  - Only anonymized text is stored in memory or FAISS indices; raw uploads are immediately discarded.  
  - Global in‑memory variables or ephemeral session storage prevent disk persistence of user content.

- **Secure External Calls**  
  - Any LLM API invocation (OpenAI, Groq) receives only anonymized inputs.  
  - Environment variables and secrets are managed via `.env`, ensuring no keys or raw text are logged.

