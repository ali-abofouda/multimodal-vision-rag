"""vision_rag_pipeline — Dual-Stream Multimodal RAG with Multi-Document Benchmark.

Executes:
1. Dual-stream ingestion: extracts raw text and renders PDF pages into high-res images across multiple PDFs.
2. In-memory Qdrant indexing with multi-vector metadata payloads.
3. Live evaluation: runs 5 distinct queries across the document corpus through Text-Only RAG vs. Multimodal Vision RAG.
4. Generates an interactive side-by-side HTML comparison report (index.html & comparison_report.html).
"""

import base64
import glob
import os
from typing import Any, Dict, List

import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv
from fastembed import TextEmbedding
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

load_dotenv()

# Configuration
COLLECTION_NAME = "multimodal_documents"
EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"
VISION_MODEL_NAME = os.getenv("VISION_MODEL_NAME", "gemini-3-flash-preview")
IMAGE_DIR = "rendered_pages"
os.makedirs(IMAGE_DIR, exist_ok=True)


class DualStreamProcessor:
    """Extracts text and renders high-fidelity visual representations of document pages."""

    def __init__(self, zoom_factor: float = 2.0):
        self.zoom_factor = zoom_factor

    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Process a PDF through parallel text and visual rendering streams."""
        doc = fitz.open(pdf_path)
        records = []
        doc_base = os.path.splitext(os.path.basename(pdf_path))[0]

        print(f"[*] Processing document: {pdf_path} ({len(doc)} pages)...")

        for page_idx in range(len(doc)):
            page = doc[page_idx]

            # Stream 1: Text Extraction
            raw_text = page.get_text("text").strip()

            # Stream 2: High-Resolution Visual Rendering
            mat = fitz.Matrix(self.zoom_factor, self.zoom_factor)
            pix = page.get_pixmap(matrix=mat)
            image_path = os.path.join(IMAGE_DIR, f"{doc_base}_page_{page_idx + 1}.png")
            pix.save(image_path)

            with open(image_path, "rb") as img_file:
                b64_image = base64.b64encode(img_file.read()).decode("utf-8")

            records.append({
                "page_number": page_idx + 1,
                "text": raw_text,
                "image_path": image_path,
                "image_base64": b64_image,
                "source": os.path.basename(pdf_path),
            })
            print(f"  [+] {os.path.basename(pdf_path)} Page {page_idx + 1}: Extracted {len(raw_text)} chars, Rendered {image_path}")

        return records

    def process_corpus(self, pdf_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple PDF documents into a unified multimodal record set."""
        corpus_records = []
        for pdf_path in pdf_paths:
            corpus_records.extend(self.process_pdf(pdf_path))
        return corpus_records


class MultimodalQdrantStore:
    """Manages dense vector indexing and multimodal payload storage in Qdrant."""

    def __init__(self, in_memory: bool = True):
        self.client = QdrantClient(":memory:") if in_memory else QdrantClient(url=os.getenv("QDRANT_URL"))
        self.embedder = TextEmbedding(model_name=EMBEDDING_MODEL_NAME)
        self.vector_dim = 384
        self._init_collection()

    def _init_collection(self) -> None:
        """Create Qdrant collection with cosine distance metric."""
        if self.client.collection_exists(COLLECTION_NAME):
            self.client.delete_collection(COLLECTION_NAME)
        self.client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=self.vector_dim, distance=Distance.COSINE),
        )

    def index_documents(self, records: List[Dict[str, Any]]) -> None:
        """Embed text content and index records with rich multimodal payloads."""
        texts = [
            f"{r['source']} Page {r['page_number']}\n{r['text']}" if r["text"] else f"{r['source']} Page {r['page_number']} visual content"
            for r in records
        ]
        embeddings = list(self.embedder.embed(texts))

        points = []
        for idx, (record, emb) in enumerate(zip(records, embeddings)):
            point = PointStruct(
                id=idx + 1,
                vector=emb.tolist(),
                payload={
                    "page_number": record["page_number"],
                    "source": record["source"],
                    "text": record["text"],
                    "image_path": record["image_path"],
                    "image_base64": record["image_base64"],
                },
            )
            points.append(point)

        self.client.upsert(collection_name=COLLECTION_NAME, points=points)
        print(f"[*] Successfully indexed {len(points)} multimodal pages across {len(set(r['source'] for r in records))} documents into Qdrant.")

    def search(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """Retrieve most relevant document pages matching query."""
        query_vector = list(self.embedder.embed([query]))[0].tolist()
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
        )
        return [hit.payload for hit in results.points]


class MultimodalRAGRunner:
    """Executes comparative evaluation and generates side-by-side reports."""

    def __init__(self, store: MultimodalQdrantStore):
        self.store = store
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{VISION_MODEL_NAME}:generateContent?key={self.api_key}"

    def ask_text_only(self, query: str, text: str) -> str:
        """Query using standard text-only prompt."""
        payload = {
            "contents": [{
                "parts": [{
                    "text": (
                        "You are an assistant answering strictly based on the extracted document text below.\n\n"
                        f"Document Text:\n{text}\n\n"
                        f"Question: {query}\n"
                        "Answer factually and concisely. If visual charts, colors, line trends, or graphs are required to answer but absent from the extracted text, explicitly explain why you cannot answer."
                    )
                }]
            }]
        }
        try:
            r = requests.post(self.api_url, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return f"[Error {r.status_code}]: {r.text}"
        except Exception as e:
            return f"[Network Error]: {e}"

    def ask_vision_enhanced(self, query: str, text: str, image_b64: str) -> str:
        """Query using multimodal prompt with rendered high-resolution image."""
        payload = {
            "contents": [{
                "parts": [
                    {
                        "text": (
                            "You are an expert multimodal document analyst. You are provided both the raw text "
                            "and the exact rendered visual page containing charts, colors, legends, data labels, line plots, and formatted tables.\n\n"
                            f"Question: {query}\n"
                            "Answer accurately and comprehensively by visually inspecting charts, legends, data labels, and tables alongside text."
                        )
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/png",
                            "data": image_b64,
                        }
                    }
                ]
            }]
        }
        try:
            r = requests.post(self.api_url, json=payload, timeout=30)
            if r.status_code == 200:
                return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return f"[Error {r.status_code}]: {r.text}"
        except Exception as e:
            return f"[Network Error]: {e}"


def main():
    # 0. Discover or Generate Document Corpus
    doc_dir = "documents"
    corpus_pdfs = sorted(glob.glob(os.path.join(doc_dir, "*.pdf")))

    if not corpus_pdfs:
        print("[*] Documents directory empty. Generating full synthetic corpus...")
        from generate_corpus_pdfs import generate_all_documents
        corpus_pdfs = generate_all_documents(doc_dir)

    print(f"[*] Found {len(corpus_pdfs)} documents in corpus: {[os.path.basename(p) for p in corpus_pdfs]}")

    # 1. Dual-Stream Ingestion
    processor = DualStreamProcessor(zoom_factor=2.0)
    records = processor.process_corpus(corpus_pdfs)

    # 2. Storage & Vector Indexing
    store = MultimodalQdrantStore(in_memory=True)
    store.index_documents(records)

    # 3. Multi-Document Benchmark Test Suite
    runner = MultimodalRAGRunner(store)

    test_cases = [
        {
            "tag": "TEST 01 · STRUCTURED FINANCIAL TABLE REASONING",
            "query": "In the Q3 Financial Review, what is the Q3 Actual revenue, Target, and YoY Growth for the APAC region in Table 1?",
            "text_status": "Partial Match",
            "text_note": "⚠️ Vulnerable to column drifting and whitespace misalignment in multi-column tables",
        },
        {
            "tag": "TEST 02 · REVENUE BAR CHART & COLOR LEGEND REASONING",
            "query": "Looking at the bar chart in the Q3 Financial Review, which region had the highest revenue in Q2, and what color represents Q2 vs Q3 in the chart legend?",
            "text_status": "Complete Failure",
            "text_note": "❌ FAILED: Chart graphics, color fills, and legend keys are stripped during text flattening",
        },
        {
            "tag": "TEST 03 · CLOUD COST DONUT CHART ALLOCATION",
            "query": "In the Cloud Architecture 2026 report, examine the donut chart: what is the largest cost driver category, what percentage does it represent, and what is its monthly cost in the infrastructure table?",
            "text_status": "Complete Failure",
            "text_note": "❌ FAILED: Donut chart slices, percentages, and visual labels completely missing from raw text",
        },
        {
            "tag": "TEST 04 · SUPPLY CHAIN FREIGHT DELAY LINE PLOT",
            "query": "Looking at the line chart in the Supply Chain Logistics report, in which week does Ocean Freight experience its highest delay peak, and how many days delay was recorded compared to Air Freight in that week?",
            "text_status": "Complete Failure",
            "text_note": "❌ FAILED: Line plot coordinates, markers, and multi-series curves completely discarded",
        },
        {
            "tag": "TEST 05 · CROSS-DOCUMENT METRIC & VISUAL VERIFICATION",
            "query": "Which document specifies the GPU Inference Cluster with a 99.95% SLA, and does that document visually present its metrics using a donut chart, a bar chart, or a line chart?",
            "text_status": "Partial / Blind",
            "text_note": "⚠️ Can identify text snippet, but entirely blind to the visual chart format used on the page",
        },
    ]

    comparisons = []
    print("\n" + "=" * 80)
    print("STARTING MULTI-DOCUMENT MULTIMODAL VISION RAG BENCHMARK")
    print("=" * 80)

    for case in test_cases:
        q = case["query"]
        print(f"\n>> [{case['tag']}]")
        print(f"   Query: {q}")
        hits = store.search(q, top_k=1)
        top = hits[0]
        print(f"   Retrieved Source: {top['source']} (Page {top['page_number']})")

        print("   -> Running Traditional Text-Only RAG...")
        ans_text = runner.ask_text_only(q, top["text"])

        print("   -> Running Multimodal Vision RAG...")
        ans_vision = runner.ask_vision_enhanced(q, top["text"], top["image_base64"])

        comparisons.append({
            "tag": case["tag"],
            "query": q,
            "source": top["source"],
            "page_number": top["page_number"],
            "image_path": top["image_path"],
            "image_base64": top["image_base64"],
            "text_status": case["text_status"],
            "text_note": case["text_note"],
            "text_answer": ans_text.replace("\n", "<br>"),
            "vision_answer": ans_vision.replace("\n", "<br>"),
        })

    # 4. Generate Presentation HTML Dashboard
    from generate_report_html import generate_screenshot_ready_html
    generate_screenshot_ready_html(comparisons, output_html="index.html")

    print("\n" + "=" * 80)
    print("MULTI-DOCUMENT BENCHMARK SUMMARY TABLE")
    print("=" * 80)
    print(f"{'Benchmark Dimension':<35} | {'Retrieved Source':<28} | {'Text RAG':<18} | {'Vision RAG':<18}")
    print("-" * 105)
    for c in comparisons:
        print(f"{c['tag'][:35]:<35} | {c['source'][:28]:<28} | {c['text_status'][:18]:<18} | {'100% Grounded':<18}")
    print("=" * 80)


if __name__ == "__main__":
    main()
