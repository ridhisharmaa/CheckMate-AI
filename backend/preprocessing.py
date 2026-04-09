"""
STAGE 1 — Computer Vision Preprocessing
Converts PDF pages into clean, OCR-ready images using OpenCV.

Techniques applied:
- PDF → PIL images via pdf2image
- Grayscale conversion
- Adaptive thresholding (binarization)
- Denoising (fastNlMeansDenoising)
- Deskewing (Hough line transform)
- Contrast enhancement (CLAHE)
- Border removal
"""

import cv2
import numpy as np
import os
from PIL import Image
import pdf2image


def preprocess_pdf(pdf_path: str, output_dir: str, prefix: str = "page") -> list[str]:
    """
    Convert PDF to preprocessed images ready for OCR.
    Returns list of image file paths.
    """
    # Convert PDF pages to PIL images at high DPI for accuracy
    pages = pdf2image.convert_from_path(pdf_path, dpi=300, fmt="PNG")
    processed_paths = []

    for i, page in enumerate(pages):
        img = np.array(page)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        processed = _preprocess_image(img)

        out_path = os.path.join(output_dir, f"{prefix}_page_{i+1}.png")
        cv2.imwrite(out_path, processed)
        processed_paths.append(out_path)
        print(f"  Preprocessed page {i+1}/{len(pages)}")

    return processed_paths


def _preprocess_image(img: np.ndarray) -> np.ndarray:
    """Apply full preprocessing pipeline to a single image."""

    # 1. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 2. Deskew the image (fix rotation from scanner/photo angle)
    gray = _deskew(gray)

    # 3. Remove noise while preserving edges
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

    # 4. CLAHE — Contrast Limited Adaptive Histogram Equalization
    #    Enhances local contrast, great for uneven lighting in photos
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # 5. Adaptive thresholding — better than global for handwriting
    #    Handles varying illumination across the page
    binary = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        blockSize=31,
        C=10
    )

    # 6. Morphological opening to remove tiny noise dots
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

    # 7. Remove black borders (common in scanned docs)
    cleaned = _remove_borders(cleaned)

    # Convert back to 3-channel for Gemini Vision (expects color image)
    final = cv2.cvtColor(cleaned, cv2.COLOR_GRAY2BGR)
    return final


def _deskew(gray: np.ndarray) -> np.ndarray:
    """
    Detect and correct skew angle using Hough Transform on edges.
    Handles up to ±45 degree rotation.
    """
    try:
        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)

        # Hough line detection
        lines = cv2.HoughLinesP(
            edges, 1, np.pi / 180,
            threshold=100,
            minLineLength=100,
            maxLineGap=10
        )

        if lines is None or len(lines) < 5:
            return gray  # Not enough lines to estimate skew

        # Calculate angles of all detected lines
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 != 0:
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                # Only consider near-horizontal lines (text lines)
                if -45 < angle < 45:
                    angles.append(angle)

        if not angles:
            return gray

        # Use median angle to avoid outlier influence
        median_angle = np.median(angles)

        # Only deskew if angle is significant (>0.5 degrees)
        if abs(median_angle) < 0.5:
            return gray

        # Rotate image to correct skew
        h, w = gray.shape
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        deskewed = cv2.warpAffine(
            gray, rotation_matrix, (w, h),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_REPLICATE
        )
        return deskewed

    except Exception:
        return gray  # Fallback: return original if deskew fails


def _remove_borders(img: np.ndarray, border_size: int = 15) -> np.ndarray:
    """Remove black borders that appear in scanned documents."""
    h, w = img.shape[:2]
    # Fill border region with white
    img[:border_size, :] = 255
    img[h-border_size:, :] = 255
    img[:, :border_size] = 255
    img[:, w-border_size:] = 255
    return img
