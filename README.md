
# Multilingual PDF Outline Extractor

A robust solution for extracting structured outlines from PDF documents with support for multiple languages including English, Japanese, Hindi, and Marathi.

## Approach

### 1. Font-Based Heading Detection
- **Font Analysis**: Extracts all font information (size, type, flags) from the document
- **Hierarchical Classification**: Determines heading levels (H1, H2, H3) based on font size, frequency, and formatting flags
- **Smart Fallback**: Uses size-based classification when font information is insufficient

### 2. Multilingual Support
- **Language Detection**: Automatically detects document language using Unicode script analysis
- **Multi-script Handling**: Supports Latin, Devanagari (Hindi/Marathi), Hiragana/Katakana, and CJK scripts
- **Localized Form Detection**: Uses language-specific keywords for form identification

### 3. Form Detection
Enhanced form detection using multiple indicators:
- **Title Analysis**: Checks for form-related keywords in multiple languages
- **Structure Analysis**: Identifies form-like patterns (numbered items, short text blocks)
- **Content Ratio**: Analyzes the ratio of short text vs. substantial content

### 4. Text Normalization
- **Unicode Normalization**: Uses NFKC normalization for consistent text processing
- **Whitespace Cleanup**: Removes excessive spacing and formatting artifacts
- **Multi-language Character Handling**: Properly processes characters from different scripts

## Models and Libraries Used

- **PyMuPDF (fitz)**: Primary PDF processing library for text and font extraction
- **unicodedata**: Built-in Python library for Unicode normalization
- **re**: Regular expressions for pattern matching and text analysis
- **collections**: For efficient data structure operations

No external ML models are used, keeping the solution lightweight and fast.

## Key Features

### Multilingual Capabilities
- **English**: Standard Latin script processing
- **Japanese**: Hiragana, Katakana, and Kanji character support
- **Hindi/Marathi**: Devanagari script processing
- **Extensible**: Easy to add support for additional languages

### Robust Form Detection
- Automatically identifies application forms, surveys, and questionnaires
- Supports multilingual form keywords
- Prevents extraction of form field labels as headings

### Performance Optimizations
- **Efficient Font Analysis**: Single-pass font information extraction
- **Memory Management**: Processes documents page by page to minimize memory usage
- **Error Handling**: Graceful handling of malformed PDFs

## Build and Run Instructions

### Building the Docker Image
```bash
docker build --platform linux/amd64 -t pdf-extractor:latest .
```

### Running the Solution
```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor:latest
```

### Directory Structure
```
project/
├── process_pdfs.py              # Main application code
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker configuration
├── README.md            # This file
├── input/               # Input PDF files (mounted volume)
└── output/              # Output JSON files (mounted volume)
```

## Input/Output Format

### Input
- PDF files placed in `input` directory
- Supports up to 50 pages per document
- Multiple PDFs can be processed in batch

### Output
For each `filename.pdf`, generates `filename.json` with the structure:
```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Main Heading",
      "page": 0
    },
    {
      "level": "H2", 
      "text": "Sub Heading",
      "page": 1
    }
  ]
}
```

### Form Documents
For documents identified as forms (applications, surveys, etc.), the outline is empty:
```json
{
  "title": "Application Form Title",
  "outline": []
}
```

## Technical Details

### Performance Characteristics
- **Processing Time**: < 10 seconds for 50-page documents
- **Memory Usage**: Optimized for 16GB RAM systems
- **CPU Requirements**: Runs efficiently on 8-core AMD64 systems

### Language Detection Algorithm
1. **Script Analysis**: Counts characters from different Unicode blocks
2. **Dominant Script**: Identifies the most frequent script type
3. **Language Mapping**: Maps scripts to languages (Devanagari → Hindi/Marathi, etc.)

### Heading Detection Process
1. **Font Extraction**: Collects all font information from document
2. **Statistical Analysis**: Analyzes font usage patterns and frequencies
3. **Level Assignment**: Assigns H1/H2/H3 based on size and usage
4. **Text Extraction**: Extracts text blocks matching heading fonts

## Error Handling

- **Malformed PDFs**: Creates empty outline with filename as title
- **Encoding Issues**: Uses UTF-8 encoding throughout
- **Missing Fonts**: Falls back to size-based heading detection
- **Empty Documents**: Handles documents with no extractable text

## Compliance

- **Network Isolation**: No internet connectivity required
- **CPU Only**: No GPU dependencies
- **Size Constraints**: Minimal dependencies, well under 200MB limit
- **AMD64 Architecture**: Explicitly configured for linux/amd64 platform
