
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from arxiv_crawler import ArxivCrawler
from pdf_processor import PDFProcessor
from multimodal_retrieval import MultimodalRetrieval
from reranker import MultimodalReranker
from survey_generator import SurveyGenerator


load_dotenv()

app = FastAPI(title="Academic Recommendation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retrieval = None
reranker = None
survey_generator = None
crawler = None
pdf_processor = None


def init_services():
    global retrieval, reranker, survey_generator, crawler, pdf_processor
    
    try:
        retrieval = MultimodalRetrieval()
        print("✅ MultimodalRetrieval initialized")
    except Exception as e:
        print(f"⚠️  MultimodalRetrieval initialization error: {e}")
    
    try:
        reranker = MultimodalReranker()
        print("✅ MultimodalReranker initialized")
    except Exception as e:
        print(f"⚠️  MultimodalReranker initialization error: {e}")
    
    try:
        survey_generator = SurveyGenerator()
        print("✅ SurveyGenerator initialized")
    except Exception as e:
        print(f"⚠️  SurveyGenerator initialization error: {e}")
    
    try:
        crawler = ArxivCrawler()
        print("✅ ArxivCrawler initialized")
    except Exception as e:
        print(f"⚠️  ArxivCrawler initialization error: {e}")
    
    try:
        pdf_processor = PDFProcessor()
        print("✅ PDFProcessor initialized")
    except Exception as e:
        print(f"⚠️  PDFProcessor initialization error: {e}")


@app.on_event("startup")
async def startup_event():
    init_services()


class SearchRequest(BaseModel):
    query: str
    n_results: int = 10
    use_rerank: bool = True
    top_k: Optional[int] = None


class SurveyRequest(BaseModel):
    topic: str
    n_results: int = 15


@app.get("/")
async def root():
    return {
        "message": "Academic Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search": "/api/search",
            "survey": "/api/survey",
            "data/check": "/api/data/check",
            "index/stats": "/api/index/stats"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/search")
async def search(request: SearchRequest):
    if not retrieval:
        raise HTTPException(status_code=500, detail="Retrieval service not initialized")
    
    try:
        results = retrieval.search(
            query=request.query,
            n_results=request.n_results
        )
        
        if request.use_rerank and reranker and len(results) &gt; 1:
            results = reranker.rerank(
                query=request.query,
                results=results,
                top_k=request.top_k
            )
        elif request.top_k:
            results = results[:request.top_k]
        
        return {
            "success": True,
            "query": request.query,
            "total_results": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/survey")
async def generate_survey(request: SurveyRequest):
    if not retrieval or not survey_generator:
        raise HTTPException(status_code=500, detail="Required services not initialized")
    
    try:
        search_results = retrieval.search(
            query=request.topic,
            n_results=request.n_results
        )
        
        if not search_results:
            return {
                "success": False,
                "error": "No relevant papers found for this topic"
            }
        
        survey_result = survey_generator.generate_survey(
            topic=request.topic,
            search_results=search_results
        )
        
        return survey_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/data/check")
async def check_data():
    data_dir = Path(os.getenv("DATA_DIR", "./data"))
    pdf_dir = data_dir / "pdfs"
    processed_dir = data_dir / "processed"
    metadata_file = data_dir / "metadata.json"
    
    pdf_count = 0
    if pdf_dir.exists():
        pdf_count = len(list(pdf_dir.glob("*.pdf")))
    
    processed_count = 0
    if processed_dir.exists():
        processed_count = len(list(processed_dir.glob("*_processed.json")))
    
    metadata_count = 0
    if metadata_file.exists():
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                metadata_count = len(metadata)
        except:
            pass
    
    index_stats = {}
    if retrieval:
        try:
            index_stats = retrieval.get_index_stats()
        except:
            pass
    
    return {
        "data_directory": str(data_dir),
        "metadata_count": metadata_count,
        "pdf_count": pdf_count,
        "processed_count": processed_count,
        "index_stats": index_stats
    }


@app.get("/api/index/stats")
async def get_index_stats():
    if not retrieval:
        raise HTTPException(status_code=500, detail="Retrieval service not initialized")
    
    try:
        stats = retrieval.get_index_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/index/build")
async def build_index():
    if not retrieval:
        raise HTTPException(status_code=500, detail="Retrieval service not initialized")
    
    try:
        total_chunks = retrieval.encode_and_index_all_processed()
        return {
            "success": True,
            "total_chunks_indexed": total_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/index/clear")
async def clear_index():
    if not retrieval:
        raise HTTPException(status_code=500, detail="Retrieval service not initialized")
    
    try:
        retrieval.clear_index()
        return {
            "success": True,
            "message": "Index cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))
    
    print(f"Starting Academic Recommendation API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
