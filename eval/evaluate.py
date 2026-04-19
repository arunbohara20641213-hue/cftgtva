#!/usr/bin/env python
"""
Evaluation script for RAG system.
Measures: retrieval quality, answer accuracy, response time.
Produces: summary report with key metrics.

Usage:
    python eval/evaluate.py
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any
import json

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from config import settings, verify_ollama_connection
from core.embeddings import OllamaEmbeddings
from rag.vector_store import ChromaVectorStore
from rag.retriever import HybridRetriever
from rag.agent import create_rag_agent
from langchain_ollama import OllamaLLM
from langchain_core.documents import Document
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# Test dataset: (query, expected_keywords, expected_topic)
TEST_QUERIES = [
    {
        "query": "What is Python used for?",
        "expected_keywords": ["python", "language", "programming"],
        "expected_topic": "Python",
        "expected_answer": "Python is used for web development, data science, automation, and machine learning",
    },
    {
        "query": "Explain REST API design principles",
        "expected_keywords": ["rest", "api", "http", "methods"],
        "expected_topic": "REST API",
        "expected_answer": "REST uses HTTP methods (GET, POST, PUT, DELETE) to perform operations on resources",
    },
    {
        "query": "What are the types of machine learning?",
        "expected_keywords": ["supervised", "unsupervised", "reinforcement"],
        "expected_topic": "Machine Learning",
        "expected_answer": "Supervised, unsupervised, and reinforcement learning",
    },
    {
        "query": "How does Docker help with deployment?",
        "expected_keywords": ["docker", "container", "deployment", "consistency"],
        "expected_topic": "DevOps",
        "expected_answer": "Docker packages applications with dependencies in containers for consistent deployment",
    },
    {
        "query": "What are React hooks?",
        "expected_keywords": ["react", "hooks", "useState", "useEffect"],
        "expected_topic": "React",
        "expected_answer": "React Hooks are functions that let you use state and effects in functional components",
    },
    {
        "query": "Explain vector search vs keyword search",
        "expected_keywords": ["vector", "keyword", "semantic", "bm25"],
        "expected_topic": "Search",
        "expected_answer": "Vector search captures semantic similarity while keyword search finds exact matches",
    },
    {
        "query": "What is ChromaDB used for?",
        "expected_keywords": ["chroma", "vector", "database", "embeddings"],
        "expected_topic": "Databases",
        "expected_answer": "ChromaDB is a vector database for storing and searching embeddings",
    },
    {
        "query": "How does hybrid search improve retrieval?",
        "expected_keywords": ["hybrid", "vector", "bm25", "recall"],
        "expected_topic": "RAG",
        "expected_answer": "Hybrid search combines vector and keyword matching for better recall",
    },
]


class RAGEvaluator:
    """Evaluates RAG system performance."""

    def __init__(self):
        """Initialize evaluator with RAG components."""
        logger.info("Initializing RAG Evaluator...")

        # Check Ollama
        if not verify_ollama_connection():
            raise RuntimeError("Ollama not running. Start with: ollama serve")

        # Initialize components
        self.embeddings = OllamaEmbeddings()
        self.vector_store = ChromaVectorStore(embeddings=self.embeddings)
        self.llm = OllamaLLM(
            model=settings.OLLAMA_LLM_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
        )

        # Load sample documents from sample_docs/
        self._load_sample_documents()

        # Create retriever and agent
        self.retriever = HybridRetriever(self.vector_store, self.sample_docs)
        self.agent = create_rag_agent(self.llm, self.vector_store, self.retriever)

        logger.info(f"Evaluator ready with {len(self.sample_docs)} documents")

    def _load_sample_documents(self):
        """Load sample documents from sample_docs/ folder."""
        sample_dir = Path(__file__).parent.parent / "sample_docs"
        self.sample_docs = []

        if not sample_dir.exists():
            logger.warning(f"Sample docs directory not found: {sample_dir}")
            return

        for file_path in sample_dir.glob("*"):
            if file_path.is_file() and file_path.suffix in [".md", ".txt"]:
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    
                    # Split long documents into chunks
                    chunks = self._chunk_text(content, chunk_size=1000, overlap=200)
                    
                    for i, chunk in enumerate(chunks):
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                "source": file_path.stem,
                                "source_name": file_path.name,
                                "chunk": i,
                            },
                        )
                        self.sample_docs.append(doc)
                    
                    logger.info(f"Loaded {file_path.name}: {len(chunks)} chunks")
                except Exception as e:
                    logger.error(f"Failed to load {file_path}: {e}")

        # Add to vector store
        if self.sample_docs:
            self.vector_store.add_documents(self.sample_docs)
            logger.info(f"Added {len(self.sample_docs)} chunks to vector store")

    @staticmethod
    def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunks.append(text[i : i + chunk_size])
        return chunks

    def evaluate_query(self, test_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a single query.

        Returns:
            Metrics dict with scores and timing
        """
        query = test_query["query"]
        expected_keywords = test_query["expected_keywords"]
        start_time = time.time()

        try:
            # Run through RAG pipeline
            result = self.agent.invoke(query)

            elapsed = time.time() - start_time

            if not result["success"]:
                return {
                    "query": query,
                    "success": False,
                    "error": result["error"],
                    "time_sec": elapsed,
                }

            response = result["response"].lower()
            sources = result["sources"]

            # Calculate metrics
            keyword_matches = sum(
                1 for kw in expected_keywords if kw.lower() in response
            )
            keyword_score = keyword_matches / len(expected_keywords)

            has_sources = len(sources) > 0
            avg_source_confidence = (
                sum(s.get("confidence", 0) for s in sources) / len(sources)
                if sources
                else 0
            )

            return {
                "query": query,
                "success": True,
                "response_length": len(result["response"]),
                "keyword_match_rate": keyword_score,
                "num_sources": len(sources),
                "avg_source_confidence": avg_source_confidence,
                "time_sec": elapsed,
                "docs_retrieved": result["metadata"].get("docs_retrieved", 0),
                "has_context": result["metadata"].get("has_context", False),
            }

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Query failed: {e}")
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "time_sec": elapsed,
            }

    def run_evaluation(self) -> Dict[str, Any]:
        """Run evaluation on all test queries."""
        logger.info(f"\n{'='*70}")
        logger.info("Starting RAG Evaluation")
        logger.info(f"{'='*70}\n")

        results = []
        for i, test_query in enumerate(TEST_QUERIES, 1):
            logger.info(f"[{i}/{len(TEST_QUERIES)}] Evaluating: {test_query['query']}")
            result = self.evaluate_query(test_query)
            results.append(result)

        # Calculate summary statistics
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        summary = {
            "total_queries": len(results),
            "successful": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(results),
            "avg_time_sec": sum(r["time_sec"] for r in results) / len(results),
            "avg_keyword_match_rate": (
                sum(r["keyword_match_rate"] for r in successful) / len(successful)
                if successful
                else 0
            ),
            "avg_sources_per_response": (
                sum(r["num_sources"] for r in successful) / len(successful)
                if successful
                else 0
            ),
            "avg_source_confidence": (
                sum(r["avg_source_confidence"] for r in successful) / len(successful)
                if successful
                else 0
            ),
            "results": results,
        }

        return summary

    def print_report(self, summary: Dict[str, Any]):
        """Print evaluation report."""
        print(f"\n{'='*70}")
        print("RAG SYSTEM EVALUATION REPORT")
        print(f"{'='*70}\n")

        # Summary metrics
        print("📊 SUMMARY METRICS")
        print(f"├─ Total Queries: {summary['total_queries']}")
        print(f"├─ Success Rate: {summary['success_rate']*100:.1f}%")
        print(f"│  ({summary['successful']} successful, {summary['failed']} failed)")
        print(f"├─ Avg Response Time: {summary['avg_time_sec']:.2f}s")
        print(f"├─ Avg Keyword Match Rate: {summary['avg_keyword_match_rate']*100:.1f}%")
        print(f"├─ Avg Sources per Response: {summary['avg_sources_per_response']:.1f}")
        print(f"└─ Avg Source Confidence: {summary['avg_source_confidence']:.2f}\n")

        # Detailed results table
        print("📋 DETAILED RESULTS")
        print(f"{'Query':<40} {'Status':<10} {'Time':<8} {'Keywords':<10} {'Sources':<8}")
        print("-" * 80)

        for result in summary["results"]:
            status = "✓ OK" if result["success"] else "✗ FAIL"
            time_str = f"{result['time_sec']:.2f}s"
            
            if result["success"]:
                keywords = f"{result['keyword_match_rate']*100:.0f}%"
                sources = f"{result['num_sources']}"
            else:
                keywords = "N/A"
                sources = "N/A"

            query_short = result["query"][:35] + "..." if len(result["query"]) > 35 else result["query"]
            
            print(f"{query_short:<40} {status:<10} {time_str:<8} {keywords:<10} {sources:<8}")

        print(f"\n{'='*70}\n")

        # Performance interpretation
        print("🎯 PERFORMANCE INTERPRETATION")
        if summary["success_rate"] >= 0.95:
            print("✓ Excellent: Near-perfect success rate")
        elif summary["success_rate"] >= 0.80:
            print("✓ Good: Most queries succeed")
        elif summary["success_rate"] >= 0.60:
            print("⚠ Fair: Many queries succeed, but some issues")
        else:
            print("✗ Poor: Multiple failures, needs debugging")

        if summary["avg_keyword_match_rate"] >= 0.80:
            print("✓ Excellent keyword coverage in responses")
        elif summary["avg_keyword_match_rate"] >= 0.60:
            print("✓ Good keyword coverage")
        else:
            print("⚠ Keyword coverage could be improved")

        if summary["avg_source_confidence"] >= 0.8:
            print("✓ High confidence source citations")
        else:
            print("⚠ Source confidence could be improved")

        print(f"\n{'='*70}\n")


def main():
    """Main entry point."""
    try:
        evaluator = RAGEvaluator()
        summary = evaluator.run_evaluation()
        evaluator.print_report(summary)

        # Save results to JSON
        output_file = Path(__file__).parent / "eval_results.json"
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2, default=str)
        logger.info(f"Results saved to {output_file}")

    except Exception as e:
        logger.error(f"Evaluation failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
