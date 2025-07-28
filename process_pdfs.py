import os
import json
import fitz  # PyMuPDF
import unicodedata
import re

INPUT_DIR = "input"
OUTPUT_DIR = "output"


def extract_title(doc):
    max_size = 0
    title = ""
    page = doc.load_page(0)  # First page only
    blocks = page.get_text("dict")["blocks"]
    for block in blocks:
        if "lines" not in block:
            continue
        for line in block["lines"]:
            for span in line.get("spans", []):
                text = span["text"].strip()
                if len(text.split()) < 3:
                    continue
                if span["size"] > max_size:
                    max_size = span["size"]
                    title = text
    return title.strip() if title else None


def extract_headings(doc):
    headings = []
    font_sizes = {}

    # Step 1: Collect all font sizes in the document
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line.get("spans", []):
                    size = round(span["size"], 1)
                    font_sizes[size] = font_sizes.get(size, 0) + 1

    # Step 2: Determine heading levels based on font size
    ranked_sizes = sorted(font_sizes.items(), key=lambda x: (-x[0], -x[1]))
    levels = ["H1", "H2", "H3"]
    size_to_level = {}
    for i, (size, _) in enumerate(ranked_sizes[:len(levels)]):
        size_to_level[size] = levels[i]

    # Step 3: Extract headings based on font size
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = " ".join(span["text"].strip() for span in spans).strip()
                if not text or len(text) < 2:
                    continue

                # Normalize multilingual text
                text = unicodedata.normalize("NFKC", text)
                size = round(max(span["size"] for span in spans), 1)
                level = size_to_level.get(size)
                if level:
                    headings.append({
                        "level": level,
                        "text": text,
                        "page": page_num
                    })

    return headings


def is_likely_form(outline):
    if not outline:
        return False
    pages = {item['page'] for item in outline}
    short_texts = [item['text'] for item in outline if len(item['text'].split()) <= 3]
    mostly_numbered = sum(1 for t in short_texts if re.match(r"^\d+[\.\)]?$", t)) > 5

    return (
        len(pages) == 1 and
        len(outline) > 15 and
        (len(short_texts) / len(outline) > 0.6 or mostly_numbered)
    )


def process_pdf(file_path, output_path):
    doc = fitz.open(file_path)

    title = extract_title(doc) or doc.metadata.get("title") or os.path.splitext(os.path.basename(file_path))[0]
    outline = extract_headings(doc)

    if is_likely_form(outline):
        outline = []

    result = {
        "title": title.strip(),
        "outline": outline
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.exists(INPUT_DIR):
        print(f"Input directory not found: {INPUT_DIR}")
        return

    for filename in os.listdir(INPUT_DIR):
        if filename.lower().endswith(".pdf"):
            input_path = os.path.join(INPUT_DIR, filename)
            output_path = os.path.join(OUTPUT_DIR, filename.replace(".pdf", ".json"))
            print(f"📄 Processing: {filename}")
            try:
                process_pdf(input_path, output_path)
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    print("All PDFs processed successfully.")


if __name__ == "__main__":
    main()
