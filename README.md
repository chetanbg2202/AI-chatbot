# 🎓 FAQ Chatbot — Online Course Platform Support

An AI-powered FAQ chatbot built with **Python**, **NLTK**, **scikit-learn**, and **Streamlit**.  
It answers user questions by finding the most semantically similar question in a pre-built FAQ dataset using **TF-IDF vectorization** and **cosine similarity**.

---

## ✨ Features

| Feature | Detail |
|---|---|
| **NLP Preprocessing** | Lowercase → Punctuation removal → Tokenization → Stopword removal → Lemmatization |
| **Similarity Matching** | TF-IDF (unigrams + bigrams) + cosine similarity |
| **Confidence Threshold** | Rejects low-confidence matches (< 0.30) with a fallback response |
| **Intent Detection** | Handles greetings, thanks, farewells, and help requests separately |
| **Efficiency** | TF-IDF matrix built **once** at startup, reused for every query |
| **Transparency** | Displays matched FAQ question + confidence score in the UI |
| **Logging** | Unmatched queries logged to `logs/unanswered.log` for dataset improvement |
| **Debug Mode** | Toggle in the sidebar to view top-3 candidate matches with scores |

---

## 📁 Project Structure

```
faq_chatbot/
├── data/
│   └── faqs.json          # 30 FAQ entries (question + answer)
├── logs/
│   └── unanswered.log     # Auto-created; logs queries with no match
├── preprocess.py          # clean_text() — NLP preprocessing pipeline
├── matcher.py             # TF-IDF index builder + cosine similarity matcher
├── chatbot.py             # Core logic: load FAQs, get_response(), intent detection
├── app.py                 # Streamlit UI entry point
├── setup_nltk.py          # One-time NLTK resource downloader
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## 🚀 Quick Start

### 1. Clone / download the project

```bash
cd faq_chatbot
```

### 2. Create and activate a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download NLTK resources (one-time setup)

```bash
python setup_nltk.py
```

Expected output:
```
Downloading required NLTK resources...

  ✔  punkt_tab  — downloaded
  ✔  stopwords  — downloaded
  ✔  wordnet    — downloaded
  ✔  omw-1.4    — downloaded

All NLTK resources are ready. You can now run the chatbot.
```

### 5. Launch the Streamlit app

```bash
streamlit run app.py
```

The app will open in your browser at **http://localhost:8501**.

---

## 🧪 Testing the CLI Mode

You can also test the chatbot entirely in your terminal (no Streamlit needed):

```bash
python chatbot.py
```

Sample session:
```
🎓 FAQ Chatbot — Online Course Platform
Type 'bye' to exit.

You: Hello!
Bot: 👋 Hello! Welcome to the Online Course Platform Support chatbot...

You: How do I get my certificate?
Bot: Once you complete all lessons and pass the final quiz...
     📌 Matched FAQ : How do I get a certificate after completing a course?
     📊 Confidence  : 78%

You: bye
Bot: 👋 Goodbye! Have a great learning journey...
```

---

## 🔧 How It Works

### Preprocessing (`preprocess.py`)

The `clean_text(text)` function applies these steps **identically** to both FAQ questions (at index time) and user queries (at query time):

```
Raw text
  → lowercase
  → remove punctuation & digits
  → NLTK word_tokenize
  → remove stopwords (NLTK English)
  → WordNetLemmatizer (lemmatize, not just stem)
  → join back to string
```

### Similarity Matching (`matcher.py`)

1. **Index time** (`build_index`): All cleaned FAQ questions are vectorized with `TfidfVectorizer(ngram_range=(1,2))`. The fitted vectorizer and matrix are stored in memory.
2. **Query time** (`find_best_match`): The user query is cleaned with the same `clean_text()`, then transformed using the **already-fitted** vectorizer (no re-fitting). Cosine similarity is computed against all FAQ vectors.
3. The FAQ with the highest score is returned. If the score is below the **threshold (0.30)**, a fallback response is given instead.

### Chatbot Logic (`chatbot.py`)

```
User query
  → Intent detection (regex patterns)
      ↳ Greeting / Thanks / Farewell / Help  →  canned response
  → FAQ similarity matching
      ↳ score ≥ 0.30  →  matched FAQ answer + confidence
      ↳ score < 0.30  →  fallback response + log to unanswered.log
```

---

## ➕ How to Add New FAQs

Open `data/faqs.json` and add a new entry following this format:

```json
{
  "id": 31,
  "question": "Your new question here?",
  "answer": "Your detailed answer here."
}
```

**That's it.** The TF-IDF index is rebuilt automatically every time the app starts, so no additional steps are needed.

> **Tip:** Use the `logs/unanswered.log` file to discover what questions users are asking that aren't covered — these are great candidates for new FAQ entries.

---

## 🎛️ Configuration

Key parameters you can tweak in the source code:

| Parameter | Location | Default | Effect |
|---|---|---|---|
| `threshold` | `chatbot.py` → `get_response()` | `0.30` | Min. cosine similarity to accept a match |
| `top_n` | `chatbot.py` → `get_response()` | `3` | How many candidates to log/display |
| `ngram_range` | `matcher.py` → `build_index()` | `(1, 2)` | Unigrams + bigrams for TF-IDF |
| `sublinear_tf` | `matcher.py` → `build_index()` | `True` | Log-normalize TF scores |
| Intent patterns | `chatbot.py` → `INTENT_PATTERNS` | see code | Regex patterns for small talk |

---

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────┐
│                    app.py (Streamlit UI)             │
│  ┌──────────────┐  ┌─────────────────────────────┐  │
│  │  Sidebar     │  │  Chat history (session state)│  │
│  │  Quick Qs    │  │  User bubble + Bot bubble    │  │
│  │  Settings    │  │  Confidence bar + FAQ pill   │  │
│  └──────────────┘  └─────────────────────────────┘  │
└──────────────────────────┬──────────────────────────┘
                           │ get_response(query)
┌──────────────────────────▼──────────────────────────┐
│                  chatbot.py                         │
│   ┌──────────────────┐   ┌──────────────────────┐   │
│   │ Intent Detection │   │  FAQ Similarity Match │   │
│   │  (regex)         │   │  (find_best_match)    │   │
│   └──────────────────┘   └──────────┬───────────┘   │
│                                     │               │
└─────────────────────────────────────┼───────────────┘
                                      │
┌─────────────────────────────────────▼───────────────┐
│                   matcher.py                        │
│   TfidfVectorizer.transform(clean_text(query))      │
│   cosine_similarity(query_vec, tfidf_matrix)        │
└─────────────────────────────────────┬───────────────┘
                                      │
┌─────────────────────────────────────▼───────────────┐
│                  preprocess.py                      │
│   lower → remove punct → tokenize → lemmatize       │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Dependencies

| Package | Version | Purpose |
|---|---|---|
| `nltk` | 3.9.1 | Tokenization, stopwords, lemmatization |
| `scikit-learn` | 1.5.2 | TF-IDF vectorizer, cosine similarity |
| `numpy` | 1.26.4 | Array operations for similarity scores |
| `streamlit` | 1.40.2 | Web UI framework |
| `pandas` | 2.2.3 | Optional data manipulation |

---

## 🐛 Troubleshooting

**`LookupError: Resource punkt_tab not found`**  
→ Run `python setup_nltk.py` to download all required NLTK data.

**`ModuleNotFoundError: No module named 'streamlit'`**  
→ Make sure your virtual environment is activated and run `pip install -r requirements.txt`.

**App shows no matches for valid questions**  
→ Lower the `threshold` in `chatbot.py` from `0.30` to `0.20`. If questions still don't match, add more FAQ entries or paraphrase the existing ones.

**Port 8501 already in use**  
→ Run `streamlit run app.py --server.port 8502` to use a different port.

---

## 📄 License

MIT License — free to use, modify, and distribute.
