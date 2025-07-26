# Adobe Hackathon 1A - PDF Heading Extractor 🧠

This solution extracts headings and outlines from PDF files and outputs them in structured JSON format.

## ✅ Features

- Parses all PDFs inside `/app/input`
- Extracts heading levels (H1, H2, H3) based on font size
- Outputs JSON files to `/app/output`
- Fully offline — no network required
- Docker-compatible (amd64)

---

## 🚀 How to Build & Run

### 1. Build the Docker Image

```bash
docker build --platform linux/amd64 -t hackathon-solution:final .



