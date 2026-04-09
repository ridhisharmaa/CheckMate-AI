# ✓ CheckMate — AI Answer Sheet Grader
## Complete Setup & Run Guide

---

## 📁 Project Structure

```
checkmate/
├── backend/
│   ├── main.py              ← FastAPI app (entry point)
│   ├── preprocessing.py     ← CV: deskew, denoise, binarize
│   ├── ocr_service.py       ← Gemini Vision OCR
│   ├── mapping_service.py   ← LLM answer-to-question mapping
│   ├── scoring_service.py   ← Semantic + LLM scoring
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── App.jsx          ← Main UI component
    │   ├── main.jsx
    │   └── index.css
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## 🔑 STEP 1: Get Your FREE Gemini API Key

1. Go to: https://aistudio.google.com/app/apikey
2. Sign in with Google (free — no credit card needed)
3. Click "Create API Key"
4. Copy the key

**Free tier limits:**
- 15 requests per minute
- 1,500 requests per day
- This is MORE than enough for a full exam set

---

## 🐍 STEP 2: Set Up the Backend

### 2a. Install system dependencies

**Ubuntu/Debian (Linux):**
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv poppler-utils
```

**macOS:**
```bash
brew install python3 poppler
```

**Windows:**
- Install Python 3.11 from https://python.org
- Install Poppler for Windows: https://github.com/oschwartz10612/poppler-windows/releases
- Add poppler's `bin/` folder to your system PATH

### 2b. Create a Python virtual environment

```bash
cd checkmate/backend
python3 -m venv venv

# Activate it:
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### 2c. Install Python packages

```bash
# Install CPU-only PyTorch first (avoids downloading huge GPU version)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Then install everything else
pip install -r requirements.txt
```

> ⚠️ First install takes 5-10 minutes (downloads ~500MB including sentence-transformers model)

### 2d. Set your Gemini API key

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and paste your Gemini API key:
# GEMINI_API_KEY=AIzaSy...your_key_here
```

### 2e. Start the backend server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
Loading sentence-transformers model...
Sentence-transformers ready ✅
INFO:     Uvicorn running on http://0.0.0.0:8000
```

Test it's working: open http://localhost:8000 → should show `{"status":"CheckMate API running ✅"}`

---

## 💻 STEP 3: Set Up the Frontend

Open a NEW terminal window:

```bash
cd checkmate/frontend

# Install Node.js if you don't have it:
# https://nodejs.org (LTS version)

npm install
npm run dev
```

You should see:
```
  VITE v5.x  ready in 500ms
  ➜  Local:   http://localhost:3000/
```

---

## 🚀 STEP 4: Use CheckMate

1. Open http://localhost:3000 in your browser
2. Upload student's handwritten answer sheet PDF
3. Upload teacher's model Q&A PDF
4. Set question labels (Q1, Q2...) and max marks
5. Click "Grade Answer Sheet"
6. Wait ~1-3 minutes (OCR + AI takes time)
7. See results: per-question scores, similarity %, feedback, total marks

---

## 📋 How to Prepare Your PDFs

### Student Answer Sheet PDF
- Scan OR photograph each page
- Use a scanning app (Adobe Scan, Microsoft Lens, CamScanner) for best quality
- Export as PDF
- Good lighting = better OCR accuracy

### Teacher Q&A PDF
Format your teacher answer PDF like this:
```
Q1. What is RAM?
Answer: RAM (Random Access Memory) is volatile memory used for temporary storage...

Q2. Explain the OSI model.
Answer: The OSI model has 7 layers...
(2 marks)

Q3. Draw and explain a binary search tree.
Answer: [DIAGRAM: A binary tree with root 50, left child 30, right child 70...]
(5 marks)
```

---

## 🔧 Troubleshooting

**"poppler not found" error:**
- Make sure poppler is installed and in PATH
- Test: `pdftoppm -v` in terminal

**"Module not found" errors:**
- Make sure your virtualenv is activated: `source venv/bin/activate`

**"GEMINI_API_KEY not set" error:**
- Check your `.env` file has the key with no spaces around `=`

**Slow grading:**
- Normal! OCR + LLM takes 30s-3min depending on PDF size
- Free Gemini tier: if you hit rate limits, wait 1 minute and retry

**Port already in use:**
```bash
# Change backend port:
uvicorn main:app --reload --port 8001
# Then update frontend/vite.config.js proxy target to :8001
```

---

## 🌐 Free Deployment (Optional — Share Online)

### Backend → Render.com (Free)
1. Push backend folder to GitHub
2. Go to render.com → New Web Service
3. Connect your repo, set:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variable: `GEMINI_API_KEY=your_key`
5. Deploy → get a URL like `https://checkmate-api.onrender.com`

### Frontend → Vercel (Free)
1. Update `API_BASE` in `frontend/src/App.jsx` to your Render URL
2. Push frontend folder to GitHub
3. Go to vercel.com → Import project
4. Deploy → get a URL like `https://checkmate.vercel.app`

---

## 💡 Tips for Best Results

1. **High-res scans**: 300 DPI minimum. Blurry photos = worse OCR
2. **Good lighting**: No shadows on the answer sheet
3. **Clean teacher PDF**: Clearly label each Q&A — "Q1. [question] Answer: [answer]"
4. **Question labels must match**: If teacher PDF says "Q1", your marks scheme must also say "Q1"
5. **Diagrams**: Gemini describes them in text — include diagram descriptions in teacher answer for scoring

---

## 🧠 ML Pipeline Summary

```
Student PDF → CV Preprocessing → Gemini Vision OCR → Answer Mapping → Scoring → Results
              (OpenCV)           (Free API)           (Gemini LLM)    (Similarity
               deskew                                  maps answers    + LLM rubric)
               denoise                                 to Q numbers    proportional marks
               binarize
               enhance
```

**No GPU required.** Everything runs on CPU + Gemini's free cloud inference.
