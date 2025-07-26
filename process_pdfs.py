import os
import json
import fitz  # PyMuPDF
from pathlib import Path

def extract_title(doc):
    """Extracts a title from the first page based on font size and position."""
    page = doc[0]
    blocks = page.get_text("dict")["blocks"]
    text_elements = []

    for block in blocks:
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text_elements.append(span)

    if not text_elements:
        return "Untitled Document"

    # Sort by font size (desc) then by y (asc)
    text_elements.sort(key=lambda x: (-x["size"], x["bbox"][1]))
    title = text_elements[0]["text"].strip()
    return title

def classify_heading(font_size, font_size_thresholds):
    """Classify heading levels by font size."""
    if font_size >= font_size_thresholds["H1"]:
        return "H1"
    elif font_size >= font_size_thresholds["H2"]:
        return "H2"
    else:
        return "H3"

def process_pdfs():
    # Try default Docker paths
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")

    # ✅ Fall back to local folders if running outside Docker
    if not input_dir.exists():
        input_dir = Path("input")
        output_dir = Path("output")

    # Ensure output folder exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each PDF in input_dir
    for pdf_file in input_dir.glob("*.pdf"):
        print(f"🔍 Processing: {pdf_file.name}")
        doc = fitz.open(pdf_file)

        title = extract_title(doc)

        font_sizes = []
        outlines = []

        # Gather font sizes to determine thresholds
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        font_sizes.append(span["size"])

        # Get font size thresholds (top 3 unique sizes)
        unique_sizes = sorted(set(font_sizes), reverse=True)
        font_size_thresholds = {
            "H1": unique_sizes[0] if len(unique_sizes) > 0 else 12,
            "H2": unique_sizes[1] if len(unique_sizes) > 1 else 11,
        }

        # Extract outline
        for page_num, page in enumerate(doc):
            blocks = page.get_text("dict")["blocks"]
            for block in blocks:
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        if not text or len(text) < 3:
                            continue
                        heading_level = classify_heading(span["size"], font_size_thresholds)
                        outlines.append({
                            "level": heading_level,
                            "text": text,
                            "page": page_num
                        })

        # Save output
        output_data = {
            "title": title,
            "outline": outlines
        }

        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Processed: {pdf_file.name} → {output_file.name}")

if __name__ == "__main__":
    print("🚀 Starting PDF processing...")
    process_pdfs()
    print("✅ All PDFs processed.")
