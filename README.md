# Vision-Enhanced Multimodal RAG Lab

A production-grade reference implementation demonstrating **Dual-Stream Vision-Enhanced Retrieval-Augmented Generation (RAG)** across a multi-document enterprise corpus using **PyMuPDF**, **Qdrant**, and **Vision-Language Models (Gemini Flash Vision)**.

---

## The Problem: Why Naive Text-Only RAG Fails

Traditional RAG pipelines extract plain text from complex enterprise documents (PDFs, PPTXs, financial reports) using OCR or basic text-extraction libraries. This approach suffers from **Text Flattening**:
- **Loss of Spatial Layout**: Two-column layouts, sidebars, and hierarchical headers are collapsed into continuous unstructured text streams.
- **Corrupted Tables**: Multi-row, multi-column tables lose their cell relationships; headers become decoupled from numeric values.
- **Ignored Visual Context**: Charts, trend graphs, donut allocations, and infographics are completely discarded.

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
           Payload: { text, image_path, base64_image, source }
                            │
                            ▼ (Retrieval)
     [ Retrieved Context: Text + High-Res Image ]
                            │
                            ▼
        [ Multimodal Vision LLM (Gemini Flash) ]
       "Sees" charts, legends & reads structured tables
```

---

## Multi-Document Enterprise Corpus

The benchmark evaluates queries across three distinct enterprise document domains:

| Document | Type | Key Visual Elements | Key Tabular Data |
| :--- | :--- | :--- | :--- |
| `q3_financial_review.pdf` | Corporate Finance | 2-Color Q2 vs Q3 Revenue Bar Chart | Multi-region Revenue, Target, YoY Growth |
| `cloud_architecture_2026.pdf` | Cloud Infrastructure | 4-Category Cost Allocation Donut Chart | Compute, GPU, Vector DB Instance Costs & SLAs |
| `supply_chain_logistics.pdf` | Supply Chain | Ocean vs. Air Freight Delay Multi-Line Plot | Fulfillment Center Capacities & Dispatch % |

---

## Benchmark Results (3 Core Visual Dimensions)

| Benchmark Dimension | Retrieved Document | Traditional Text-Only RAG | Dual-Stream Vision RAG |
| :--- | :--- | :--- | :--- |
| **01 · Bar Chart & Color Legends** | `q3_financial_review.pdf` | ❌ Complete Failure (Color/Bars lost) | ✅ **100% Grounded** |
| **02 · Freight Delay Line Curves** | `supply_chain_logistics.pdf` | ❌ Complete Failure (Trends lost) | ✅ **100% Grounded** |
| **03 · Cross-Document Verification** | `cloud_architecture_2026.pdf` | ⚠️ Degraded (Blind to chart type) | ✅ **100% Grounded** |

---

## Project Structure

```text
multimodal-vision-rag/
├── README.md               # Architecture documentation and benchmarks
├── index.html              # Live interactive presentation dashboard (GitHub Pages)
├── comparison_report.html  # Standalone benchmark comparison report
├── requirements.txt        # Pinned dependencies (PyMuPDF, Qdrant, FastEmbed, Pillow)
├── generate_corpus_pdfs.py # Generates 3 multi-domain synthetic enterprise PDFs
├── generate_report_html.py # Compiles ultra-premium HTML dashboard with modal zoom
├── vision_rag_pipeline.py  # End-to-end multi-document ingestion, retrieval & evaluation
├── documents/              # Enterprise PDF corpus (Finance, Cloud, Logistics)
│   ├── cloud_architecture_2026.pdf
│   ├── q3_financial_review.pdf
│   └── supply_chain_logistics.pdf
└── rendered_pages/         # High-resolution rendered page images (PNG)
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

### 3. Run Pipeline & Generate Dashboard

```bash
python generate_corpus_pdfs.py
python vision_rag_pipeline.py
```

Open `index.html` in any browser to explore the interactive visual comparison report with modal zoom and live evaluation metrics.
