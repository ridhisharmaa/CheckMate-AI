from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import tempfile, os, json, traceback
from pathlib import Path

from preprocessing import preprocess_pdf
from ocr_service import run_ocr
from mapping_service import map_answers_to_questions
from scoring_service import score_all_questions

app = FastAPI(title="CheckMate API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "CheckMate API running ✅"}

@app.post("/grade")
async def grade_paper(
    student_pdf: UploadFile = File(...),
    teacher_pdf: UploadFile = File(...),
    marks_scheme: str = Form(...),   # JSON string: {"Q1": 2, "Q2": 5, ...}
):
    """
    Main grading endpoint.
    - student_pdf: scanned handwritten answer sheet
    - teacher_pdf: printed Q&A reference from teacher
    - marks_scheme: JSON mapping question numbers to max marks
    """
    try:
        marks = json.loads(marks_scheme)
    except Exception:
        raise HTTPException(400, "marks_scheme must be valid JSON like {\"Q1\": 2, \"Q2\": 5}")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploads
        student_path = os.path.join(tmpdir, "student.pdf")
        teacher_path = os.path.join(tmpdir, "teacher.pdf")

        with open(student_path, "wb") as f:
            f.write(await student_pdf.read())
        with open(teacher_path, "wb") as f:
            f.write(await teacher_pdf.read())

        try:
            # STAGE 1: CV Preprocessing → images
            print("📸 Stage 1: Preprocessing PDFs...")
            student_images = preprocess_pdf(student_path, tmpdir, prefix="student")
            teacher_images = preprocess_pdf(teacher_path, tmpdir, prefix="teacher")

            

            # STAGE 2: OCR via Gemini Vision
            print("🔍 Stage 2: Running OCR...")
            student_text = run_ocr(student_images, mode="student")
            teacher_text = run_ocr(teacher_images, mode="teacher")

            print("\n================ OCR OUTPUT (STUDENT) ================\n")
            print(student_text)

            print("\n================ OCR OUTPUT (TEACHER) ================\n")
            print(teacher_text)

            # STAGE 3: Map student answers to question numbers
            print("🗺️  Stage 3: Mapping answers to questions...")
            question_numbers = list(marks.keys())
            student_answers = map_answers_to_questions(student_text, question_numbers)
            teacher_answers = map_answers_to_questions(teacher_text, question_numbers, is_teacher=True)
            print("\n================ MAPPED STUDENT ANSWERS ================\n")
            print(student_answers)

            print("\n================ MAPPED TEACHER ANSWERS ================\n")
            print(teacher_answers)

            # STAGE 4: Score each question
            print("📊 Stage 4: Scoring...")
            results = score_all_questions(student_answers, teacher_answers, marks)

            print("✅ Done!")
            return JSONResponse(content={"success": True, "results": results})

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(500, f"Pipeline error: {str(e)}")
