import fitz  # PyMuPDF
import json
import os
import sys

def extract_text_details_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if block["type"] != 0:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    text = span["text"].strip()
                    font_size = span["size"]
                    font = span["font"].lower()

                    if not text:
                        continue

                    # Simple heuristic to detect title and headings
                    pages.append({
                        "text": text,
                        "font_size": font_size,
                        "font_name": font,
                        "page": page_num  # 0-indexed
                    })

    doc.close()
    return pages

def classify_headings(blocks):
    # Get the largest font size to assume it's the title
    if not blocks:
        return None, []

    # Sort by font size descending
    sorted_blocks = sorted(blocks, key=lambda b: -b["font_size"])
    title = sorted_blocks[0]["text"]

    # Decide thresholds for H1, H2, H3 based on top few font sizes
    font_sizes = sorted(set(b["font_size"] for b in blocks), reverse=True)
    h1, h2, h3 = (font_sizes + [0, 0, 0])[:3]

    outline = []
    for block in blocks:
        level = None
        if block["font_size"] == h1:
            level = "H1"
        elif block["font_size"] == h2:
            level = "H2"
        elif block["font_size"] == h3:
            level = "H3"

        if level:
            outline.append({
                "level": level,
                "text": block["text"],
                "page": block["page"]
            })

    return title, outline

def save_to_json(data, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def main():
    input_dir = "input"
    output_dir = "output"

    if not os.path.exists(input_dir):
        print(f"❌ Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    processed = False
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename.replace(".pdf", ".json"))

            try:
                print(f"🔍 Processing: {filename}")
                blocks = extract_text_details_from_pdf(pdf_path)
                title, outline = classify_headings(blocks)
                result = {
                    "title": title,
                    "outline": outline
                }
                save_to_json(result, output_path)
                print(f"✅ Processed: {filename} → {output_path}")
                processed = True
            except Exception as e:
                print(f"❌ Failed: {filename} | Error: {e}", file=sys.stderr)

    if not processed:
        print("⚠️ No PDF files processed", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
