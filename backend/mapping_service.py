"""
STAGE 3 — Answer Mapping via LLM
The hardest problem: students answer in ANY order, may write question numbers
in many formats or omit them entirely.

Strategy: Send full OCR text + list of question numbers to Gemini.
Let the LLM figure out which text block corresponds to which question.
This is far more robust than regex/keyword matching.
"""

import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-flash-latest")


def map_answers_to_questions(
    ocr_text: str,
    question_numbers: list[str],
    is_teacher: bool = False
) -> dict[str, str]:
    """
    Map extracted OCR text to specific question numbers.
    Returns: {"Q1": "answer text...", "Q2": "answer text...", ...}
    """
    q_list = ", ".join(question_numbers)
    role = "model answer sheet" if is_teacher else "student answer sheet"

    prompt = f"""
You are analyzing a {role} OCR transcript.

The question paper has these questions: {q_list}

Here is the full OCR text of the answer sheet:
---
{ocr_text}
---

Your task: Extract the answer written for EACH question listed above.

IMPORTANT RULES:
1. Students may write question numbers as: "Q1", "1.", "1)", "Ans 1", "Question 1", "Que. 1", etc.
2. Students may answer in ANY order — don't assume sequential order
3. Extract the COMPLETE answer for each question (including any sub-parts a, b, c)
4. If a question is not answered at all, set its value to null
5. Include any [DIAGRAM: ...], [TABLE: ...], or [CODE: ...] blocks that belong to that answer
6. Do NOT cut off answers — include everything the student wrote for that question

Return ONLY a valid JSON object in this exact format:
{{
  "Q1": "complete answer text here including diagrams tables etc",
  "Q2": "complete answer text here",
  "Q3": null
}}

No explanation, no markdown, just the JSON object.
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.0,
                max_output_tokens=4096,
            )
        )
        raw = response.text.strip()

        # Clean up any accidental markdown wrapping
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        answers = json.loads(raw)

        # Normalize keys to match our question_numbers format
        normalized = {}
        for qnum in question_numbers:
            # Try exact match first, then case-insensitive
            if qnum in answers:
                normalized[qnum] = answers[qnum]
            else:
                # Try to find a close match
                for key in answers:
                    if key.upper().replace(" ", "") == qnum.upper().replace(" ", ""):
                        normalized[qnum] = answers[key]
                        break
                else:
                    normalized[qnum] = None

        return normalized

    except json.JSONDecodeError:
        print(f"  ⚠️ Mapping JSON parse failed, attempting recovery...")
        return _fallback_mapping(ocr_text, question_numbers)

    except Exception as e:
        print(f"  ⚠️ Mapping failed: {e}")
        return {q: None for q in question_numbers}


def _fallback_mapping(ocr_text: str, question_numbers: list[str]) -> dict[str, str]:
    """
    Fallback: simple regex-based mapping when LLM fails.
    Less accurate but never crashes.
    """
    result = {}
    patterns = []

    for qnum in question_numbers:
        # Extract the number part (e.g., "Q1" → "1", "Q10" → "10")
        num = re.sub(r"[^0-9]", "", qnum)
        patterns.append((qnum, num))

    # Sort patterns by question number (descending) to avoid "1" matching "10"
    patterns.sort(key=lambda x: -int(x[1]) if x[1] else 0)

    for i, (qnum, num) in enumerate(patterns):
        if not num:
            result[qnum] = None
            continue

        # Build regex to find where this question starts
        start_pattern = rf"(?:Q\.?\s*{num}|Ans\.?\s*{num}|Question\.?\s*{num}|{num}[.)\s])"
        start_match = re.search(start_pattern, ocr_text, re.IGNORECASE)

        if not start_match:
            result[qnum] = None
            continue

        start = start_match.end()

        # Find where the next question starts
        if i + 1 < len(patterns):
            next_num = patterns[i + 1][1]
            end_pattern = rf"(?:Q\.?\s*{next_num}|Ans\.?\s*{next_num}|{next_num}[.)\s])"
            end_match = re.search(end_pattern, ocr_text[start:], re.IGNORECASE)
            end = start + end_match.start() if end_match else len(ocr_text)
        else:
            end = len(ocr_text)

        result[qnum] = ocr_text[start:end].strip()

    return result
