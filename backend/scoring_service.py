"""
STAGE 4 — Scoring Engine
Two-layer scoring for maximum fairness:

Layer 1: Semantic Similarity (sentence-transformers, runs on CPU, free)
  - Captures meaning even when phrased differently
  - Good for factual/conceptual answers

Layer 2: LLM Rubric Evaluation (Gemini, free tier)
  - Evaluates correctness, completeness, diagram quality
  - Gives nuanced marks for partially correct answers
  - Handles subject-specific technical content

Final score = weighted combination of both layers
"""

import os
import json
import re
import google.generativeai as genai
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini = genai.GenerativeModel("models/gemini-flash-latest")

# Load once at startup — small model, runs on CPU
print("Loading sentence-transformers model...")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Sentence-transformers ready ✅")


def score_all_questions(
    student_answers: dict[str, str | None],
    teacher_answers: dict[str, str | None],
    marks_scheme: dict[str, int | float],
) -> dict:
    """
    Score every question and compile final results.
    Returns structured result dict for frontend.
    """
    question_results = []
    total_scored = 0.0
    total_possible = 0.0

    for qnum, max_marks in marks_scheme.items():
        student_ans = student_answers.get(qnum)
        teacher_ans = teacher_answers.get(qnum)
        max_marks = float(max_marks)
        total_possible += max_marks

        result = _score_single_question(qnum, student_ans, teacher_ans, max_marks)
        question_results.append(result)
        total_scored += result["marks_awarded"]

    return {
        "questions": question_results,
        "total_scored": round(total_scored, 2),
        "total_possible": total_possible,
        "percentage": round((total_scored / total_possible * 100) if total_possible > 0 else 0, 1),
        "grade": _compute_grade(total_scored, total_possible),
    }


def _score_single_question(
    qnum: str,
    student_ans: str | None,
    teacher_ans: str | None,
    max_marks: float,
) -> dict:
    """Score a single question using both similarity and LLM rubric."""

    # Case: student didn't attempt this question
    if not student_ans or student_ans.strip() == "":
        return {
            "question": qnum,
            "max_marks": max_marks,
            "marks_awarded": 0.0,
            "similarity_score": 0.0,
            "llm_score": 0.0,
            "feedback": "Not attempted.",
            "has_diagram": False,
            "has_table": False,
            "has_code": False,
            "student_answer_preview": "",
        }

    # Case: teacher answer missing (shouldn't happen normally)
    if not teacher_ans or teacher_ans.strip() == "":
        return {
            "question": qnum,
            "max_marks": max_marks,
            "marks_awarded": max_marks * 0.5,  # Benefit of doubt
            "similarity_score": 50.0,
            "llm_score": 50.0,
            "feedback": "Model answer unavailable. Partial marks awarded.",
            "has_diagram": _has_content_type(student_ans, "DIAGRAM"),
            "has_table": _has_content_type(student_ans, "TABLE"),
            "has_code": _has_content_type(student_ans, "CODE"),
            "student_answer_preview": student_ans[:300],
        }

    # Layer 1: Semantic similarity (cosine similarity of embeddings)
    similarity_pct = _compute_semantic_similarity(student_ans, teacher_ans)

    # Layer 2: LLM rubric evaluation
    llm_score_pct, feedback = _llm_rubric_evaluation(
        qnum, student_ans, teacher_ans, max_marks, similarity_pct
    )

    # Weighted combination: 35% similarity + 65% LLM rubric
    # LLM gets more weight because it understands subject context
    combined_pct = (0.35 * similarity_pct) + (0.65 * llm_score_pct)

    # Diagram/table/code bonus: +5% if student included these where expected
    has_diagram = _has_content_type(student_ans, "DIAGRAM")
    has_table = _has_content_type(student_ans, "TABLE")
    has_code = _has_content_type(student_ans, "CODE")
    teacher_has_diagram = _has_content_type(teacher_ans, "DIAGRAM")
    teacher_has_table = _has_content_type(teacher_ans, "TABLE")
    teacher_has_code = _has_content_type(teacher_ans, "CODE")

    bonus = 0.0
    if has_diagram and teacher_has_diagram:
        bonus += 5.0
    if has_diagram and not teacher_has_diagram:
        bonus += 3.0   # Student added diagram even when not required = creativity bonus
    if has_table and teacher_has_table:
        bonus += 3.0
    if has_code and teacher_has_code:
        bonus += 3.0

    final_pct = min(100.0, combined_pct + bonus)
    marks_awarded = round((final_pct / 100.0) * max_marks, 2)

    return {
        "question": qnum,
        "max_marks": max_marks,
        "marks_awarded": marks_awarded,
        "similarity_score": round(similarity_pct, 1),
        "llm_score": round(llm_score_pct, 1),
        "combined_score_pct": round(final_pct, 1),
        "feedback": feedback,
        "has_diagram": has_diagram,
        "has_table": has_table,
        "has_code": has_code,
        "student_answer_preview": student_ans[:300],
    }


def _compute_semantic_similarity(student_ans: str, teacher_ans: str) -> float:
    """
    Compute cosine similarity between student and teacher answer embeddings.
    Returns percentage (0-100).
    """
    # Strip special content blocks for text similarity
    clean_student = _strip_special_blocks(student_ans)
    clean_teacher = _strip_special_blocks(teacher_ans)

    if not clean_student.strip() or not clean_teacher.strip():
        return 0.0

    try:
        emb1 = embedder.encode(clean_student, convert_to_tensor=True)
        emb2 = embedder.encode(clean_teacher, convert_to_tensor=True)
        similarity = float(util.cos_sim(emb1, emb2)[0][0])
        # Cosine similarity is -1 to 1, normalize to 0-100
        return max(0.0, min(100.0, (similarity + 1) / 2 * 100))
    except Exception as e:
        print(f"  Similarity error: {e}")
        return 50.0


def _llm_rubric_evaluation(
    qnum: str,
    student_ans: str,
    teacher_ans: str,
    max_marks: float,
    similarity_hint: float,
) -> tuple[float, str]:
    """
    Ask Gemini to evaluate the student's answer against the model answer.
    Returns (score_percentage, feedback_string).
    """
    prompt = f"""
You are a strict but fair academic examiner evaluating a student's answer.

Question: {qnum} (Maximum marks: {max_marks})

MODEL ANSWER (teacher's reference):
{teacher_ans}

STUDENT'S ANSWER:
{student_ans}

Note: A semantic similarity tool has already scored this at {similarity_hint:.1f}% similarity.

Your task: Evaluate the student's answer holistically on:
1. Conceptual correctness (most important)
2. Completeness — are all key points covered?
3. Technical accuracy — correct terminology/formulas/algorithms?
4. Quality of diagrams/tables/code if present
5. Clarity of explanation

SCORING GUIDE:
- 90-100%: Perfect or near-perfect, all key points, accurate
- 70-89%: Good, most points covered, minor gaps
- 50-69%: Partial, core concept correct but incomplete
- 30-49%: Some relevant content, significant gaps
- 10-29%: Minimal correct content
- 0-9%: Incorrect or not relevant

Return ONLY valid JSON (no markdown, no explanation):
{{
  "score_percentage": <number 0-100>,
  "feedback": "<2-3 sentence constructive feedback mentioning what was right, what was missing>"
}}
"""
    try:
        response = gemini.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=512,
            )
        )
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        data = json.loads(raw)
        score_pct = float(data.get("score_percentage", 50.0))
        feedback = data.get("feedback", "Evaluation complete.")
        return max(0.0, min(100.0, score_pct)), feedback

    except Exception as e:
        print(f"  LLM rubric error: {e}")
        # Fallback to similarity-based score
        return similarity_hint, "Automated evaluation. Review manually for accuracy."


def _has_content_type(text: str, tag: str) -> bool:
    """Check if OCR output contains a specific content type tag."""
    if not text:
        return False
    return f"[{tag}:" in text.upper()


def _strip_special_blocks(text: str) -> str:
    """Remove [DIAGRAM:...], [TABLE:...], [CODE:...] blocks for text similarity."""
    return re.sub(r"\[(DIAGRAM|TABLE|CODE|ILLEGIBLE):.*?\]", "", text, flags=re.DOTALL | re.IGNORECASE).strip()


def _compute_grade(scored: float, possible: float) -> str:
    """Compute letter grade from score."""
    if possible == 0:
        return "N/A"
    pct = (scored / possible) * 100
    if pct >= 90: return "A+"
    if pct >= 80: return "A"
    if pct >= 70: return "B"
    if pct >= 60: return "C"
    if pct >= 50: return "D"
    return "F"
