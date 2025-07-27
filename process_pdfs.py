import os
import fitz  # PyMuPDF
import json
import unicodedata

INPUT_DIR = "input"
OUTPUT_DIR = "output"
LEVELS = ["H1", "H2", "H3"]  # Only include up to H3

def is_probable_table_block(block):
    lines = block.get("lines", [])
    if len(lines) > 4:
        avg_len = sum(len(" ".join(span["text"] for span in line.get("spans", []))) for line in lines) / len(lines)
        if avg_len < 40:
            return True
    return False

def map_font_sizes_to_levels(font_sizes):
    sorted_fonts = sorted(font_sizes.items(), key=lambda x: (-x[0], -x[1]))
    try:
        body_threshold = max(size for size, count in font_sizes.items() if count > 30)
    except ValueError:
        body_threshold = min(font_sizes.keys())
    heading_fonts = [fs for fs, _ in sorted_fonts if fs > body_threshold]
    size_to_level = {}
    for i, fs in enumerate(heading_fonts[:3]):  # Only map top 3 heading sizes
        size_to_level[fs] = LEVELS[i]

    return size_to_level

def extract_title(doc):
    font_counter = {}
    page = doc.load_page(0)
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line.get("spans", []):
                size = round(span["size"], 1)
                font_counter[size] = font_counter.get(size, 0) + 1

    if not font_counter:
        return "", set(), {}

    largest_font = max(font_counter.items(), key=lambda x: x[0])[0]
    title_lines = []
    title_segments = set()
    title_sizes = {}

    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            spans = line.get("spans", [])
            if not spans:
                continue
            if all(round(span["size"], 1) == largest_font for span in spans):
                text = " ".join(span["text"].strip() for span in spans).strip()
                if text:
                    normalized = text.replace(" ", "").lower()
                    title_segments.add(normalized)
                    title_lines.append(text)
                    title_sizes[largest_font] = title_sizes.get(largest_font, 0) + 1

    title = "  ".join(title_lines).strip()
    if len(title.split()) < 3:
        return "", set(), font_counter
    return title, title_segments, font_counter

def extract_outline(doc):
    num_pages = len(doc)
    title, title_segments, title_font_sizes = extract_title(doc)

    font_sizes = title_font_sizes.copy()
    start_page = 0 if num_pages == 1 else 1

    for page_num in range(start_page, num_pages):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block or is_probable_table_block(block):
                continue
            for line in block["lines"]:
                for span in line.get("spans", []):
                    size = round(span["size"], 1)
                    font_sizes[size] = font_sizes.get(size, 0) + 1

    size_to_level = map_font_sizes_to_levels(font_sizes)
    seen_headings = set()
    outline = []

    for page_num in range(start_page, num_pages):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block or is_probable_table_block(block):
                continue
            for line in block["lines"]:
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = " ".join(span["text"].strip() for span in spans).strip()
                if len(text) < 2:
                    continue
                text = unicodedata.normalize("NFKC", text)
                size = round(max(span["size"] for span in spans), 1)
                level = size_to_level.get(size)

                normalized_text = text.replace(" ", "").lower()
                if normalized_text in title_segments or normalized_text in seen_headings:
                    continue

                if level:
                    seen_headings.add(normalized_text)
                    outline.append({
                        "level": level,
                        "text": text,
                        "page": page_num
                    })

    return outline, title

def process_pdf(file_path):
    doc = fitz.open(file_path)
    outline, title = extract_outline(doc)
    return {
        "title": title,
        "outline": outline
    }

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    pdfs = [f for f in os.listdir(INPUT_DIR) if f.lower().endswith(".pdf")]
    if not pdfs:
        print("⚠️  No PDF files found in", INPUT_DIR)
        return

    for filename in pdfs:
        pdf_path = os.path.join(INPUT_DIR, filename)
        print(f"📄 Processing: {filename}")
        result = process_pdf(pdf_path)
        json_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    print("✅ All PDFs processed successfully.")

if __name__ == "__main__":
    main()
