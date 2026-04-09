"""
STAGE 2 — OCR via Gemini 1.5 Flash Vision
Uses Google's multimodal LLM instead of traditional OCR (TrOCR, EasyOCR)
for dramatically better accuracy on handwriting, especially:
- Cursive and messy handwriting
- Mixed content (text + diagrams + code + tables)
- Context-aware word inference
"""

import os
import base64
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-flash-latest")


STUDENT_OCR_PROMPT = """
You are an expert OCR system specialized in reading handwritten student answer sheets.

Your task: Extract ALL text from this handwritten answer sheet with MAXIMUM accuracy.

CRITICAL RULES:
1. Preserve every question number the student wrote (e.g., "Q1", "1.", "Ans 3", "Question 2", etc.)
2. Transcribe handwriting EXACTLY — use context to infer unclear words intelligently
3. For DIAGRAMS/FLOWCHARTS/TREES: describe them in detail inside [DIAGRAM: ...] tags
4. For TABLES: convert to markdown table format inside [TABLE: ...] tags  
5. For CODE: preserve inside [CODE: ...] tags with correct indentation
6. Do NOT skip any content — even small side notes matter
7. If a word is truly illegible, write [ILLEGIBLE] — never guess randomly
8. Preserve line breaks where they indicate structure (lists, steps, etc.)

Output the full transcript below:
"""

TEACHER_OCR_PROMPT = """
You are an expert document parser for printed/typed academic content.

Your task: Extract the complete question paper AND model answers with perfect accuracy.

EXTRACT AND STRUCTURE AS:
- Each question: clearly labeled with its number
- Model answer for each question: complete and detailed
- Marks for each question if mentioned (e.g., "(5 marks)", "[2]", etc.)
- For diagrams in model answers: describe them in [DIAGRAM: ...] tags
- For tables: use markdown table format in [TABLE: ...] tags
- For code: use [CODE: ...] tags

Preserve all mathematical formulas, technical terms, and subject-specific notation exactly.

Output the structured content below:
"""


def run_ocr(image_paths: list[str], mode: str = "student") -> str:
    """
    Run Gemini Vision OCR on a list of preprocessed page images.
    mode: "student" or "teacher"
    Returns concatenated text of all pages.
    """
    prompt = STUDENT_OCR_PROMPT if mode == "student" else TEACHER_OCR_PROMPT
    all_pages_text = []

    for i, img_path in enumerate(image_paths):
        print(f"  OCR page {i+1}/{len(image_paths)} ({mode})...")
        page_text = _ocr_single_page(img_path, prompt, page_num=i+1)
        all_pages_text.append(f"--- PAGE {i+1} ---\n{page_text}")

    return "\n\n".join(all_pages_text)


def _ocr_single_page(img_path: str, prompt: str, page_num: int) -> str:
    """Run OCR on a single page image using Gemini Vision."""
    try:
        img = Image.open(img_path)

        # Gemini Vision: pass image directly as PIL Image
        response = model.generate_content(
            [prompt, img],
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,      # Low temp = more deterministic OCR
                max_output_tokens=4096,
            )
        )
        return response.text.strip()

    except Exception as e:
        print(f"  ⚠️ OCR failed for page {page_num}: {e}")
        return f"[OCR ERROR on page {page_num}: {str(e)}]"
