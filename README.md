# CheckMate

CheckMate is an early-stage AI answer sheet grading system. It is designed to take a student's handwritten answer sheet PDF, compare it against a teacher's reference answer PDF, and return question-wise marks, feedback, and an overall grade.

This project is not deployed yet. It is a very early local version intended for experimentation, testing, and further development.

## What It Does

CheckMate helps automate the first pass of answer sheet evaluation:

- Accepts a scanned or photographed handwritten student answer sheet as a PDF.
- Accepts a teacher reference PDF containing questions and model answers.
- Lets the user define question labels and maximum marks.
- Extracts text from the student answer sheet using vision-based OCR.
- Maps student answers to the matching teacher questions.
- Scores each answer using semantic similarity and LLM-based rubric evaluation.
- Shows question-wise scores, feedback, detected visual content, and the final grade.

The goal is not to replace a teacher's judgment. It is meant to assist with grading by producing a structured, reviewable evaluation.

## How It Works

The grading flow is:

```text
Student PDF
  -> CV preprocessing
  -> Gemini Vision OCR
  -> answer-to-question mapping
  -> semantic + LLM scoring
  -> question-wise results
```

The backend preprocesses uploaded PDFs, extracts readable text from handwritten pages, maps extracted answers to the expected questions, and scores them against teacher-provided answers. The frontend provides the upload flow, marks scheme editor, progress states, and results view.

## Project Structure

```text
checkmate/
  backend/
    main.py              FastAPI app entry point
    preprocessing.py     PDF/image preprocessing helpers
    ocr_service.py       Gemini Vision OCR integration
    mapping_service.py   LLM-based answer mapping
    scoring_service.py   Semantic and LLM scoring logic
    check_models.py      Model/environment checks
    requirements.txt     Python dependencies

  frontend/
    index.html           Vite HTML entry point
    package.json         Frontend scripts and dependencies
    vite.config.js       Vite configuration
    src/
      main.jsx           React entry point
      App.jsx            Main CheckMate UI
      index.css          Global styles
      App.css            App styles
      assets/            Frontend image assets

  setup.txt              Full local setup and run guide
  README.md              Project overview
```

## Tech Stack

- Backend: FastAPI, Python
- OCR/LLM: Google Gemini API
- Computer vision: OpenCV-style preprocessing pipeline
- Semantic scoring: sentence-transformers
- PDF processing: Python PDF/image tooling
- Frontend: React, Vite
- Runtime: Local development only for now

## Current Status

CheckMate is not production-ready yet. The current version is focused on proving the pipeline works locally:

- No hosted deployment is available.
- API keys and environment setup are handled locally.
- The grading flow may need more validation with real answer sheets.
- OCR quality depends heavily on scan quality.
- Human review is still expected before using results in a real academic setting.

## Local Setup

Because the project is not deployed yet, anyone who wants to use it must run both the backend and frontend locally.

### 1. Create A Gemini API Key

Create an API key from Google AI Studio:

```text
https://aistudio.google.com/app/apikey
```

### 2. Set Up The Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file inside `backend/` and add:

```text
GEMINI_API_KEY=your_api_key_here
```

Start the backend:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API should be available at:

```text
http://localhost:8000
```

### 3. Set Up The Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The frontend should be available at the local URL printed by Vite, usually:

```text
http://localhost:5173
```

If the backend port changes, update the frontend API base URL in `frontend/src/App.jsx`.

## Usage

Once both servers are running:

1. Upload the student handwritten answer sheet PDF.
2. Upload the teacher's reference Q&A PDF.
3. Add or edit question labels and maximum marks.
4. Click the grading button.
5. Review the generated marks, feedback, and final score.

## Notes For Contributors

This is an early version, so the most useful next improvements are likely:

- Better handling for messy scans and low-quality handwriting.
- More transparent scoring explanations.
- Stronger validation for teacher reference PDF formatting.
- Exportable grading reports.
- Authentication, storage, and deployment support.
- Test coverage for backend grading and mapping behavior.
