# Vision-Enhanced Multimodal RAG Lab

A minimal, production-grade reference implementation demonstrating **Dual-Stream Vision-Enhanced Retrieval-Augmented Generation (RAG)** using **PyMuPDF**, **Qdrant**, and **Vision-Language Models (Gemini Flash Vision)**.

---

## The Problem: Why Naive Text-Only RAG Fails

Traditional RAG pipelines extract plain text from complex enterprise documents (PDFs, PPTXs, scanned contracts) using OCR or text-extraction libraries. This approach suffers from **Text Flattening**:
- **Loss of Spatial Layout**: Two-column layouts, sidebars, and hierarchical headers are collapsed into continuous text streams.
- **Corrupted Tables**: Multi-row, multi-column tables lose their cell relationships; headers become decoupled from numeric values.
- **Ignored Visual Context**: Charts, trend graphs, architecture diagrams, and infographics are completely discarded.

```
[ Complex Enterprise PDF ]
     │
     ▼ (Traditional Parser)
[ Flattened Text Stream ] ──> Tables broken, charts deleted! ──> Hallucinations & Failed Q&A
```

---

## The Architecture: Dual-Stream Multimodal RAG

This laboratory implements a **Dual-Stream Pipeline**:

```
                 [ Multi-Modal PDF Page ]
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
     [ Stream 1: Text ]           [ Stream 2: Vision ]
  page.get_text("text")         fitz.Matrix(2.0, 2.0)
              │                           │
              ▼                           ▼
   [ Text Embedding (BGE) ]      [ High-Res Page PNG ]
              │                           │
              └─────────────┬─────────────┘
                            ▼
           [ Qdrant Multi-Vector Store ]
           Vector: Text Embeddings
           Payload: { text, image_path, base64_image }
                            │
                            ▼ (Retrieval)
     [ Retrieved Context: Text + High-Res Image ]
                            │
                            ▼
        [ Multimodal Vision LLM (Gemini Flash) ]
            "Sees" the chart & reads the table
```

---

## Project Structure

```text
multimodal-vision-rag/
├── README.md               # Architecture documentation and benchmarks
├── index.html              # Live interactive dashboard (GitHub Pages)
├── requirements.txt        # Pinned dependencies (PyMuPDF, Qdrant, FastEmbed, Pillow)
├── generate_sample_pdf.py  # Generates synthetic report with tables & colored bar charts
├── vision_rag_pipeline.py  # End-to-end dual-stream pipeline and side-by-side comparison
├── rendered_pages/         # High-resolution rendered page images (PNG)
└── sample_document.pdf     # Synthetic enterprise test document
```

---

## Quickstart

### 1. Installation

```bash
git clone https://github.com/ali-abofouda/multimodal-vision-rag.git
cd multimodal-vision-rag
uv venv --python 3.12
.venv\Scripts\activate
uv pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Generate Test PDF & Run Pipeline

```bash
python generate_sample_pdf.py
python vision_rag_pipeline.py
```
