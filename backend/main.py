
import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from arxiv_crawler import ArxivCrawler
from pdf_processor import PDFProcessor
from multimodal_retrieval import MultimodalRetrieval
from reranker import Reranker
from report_generator import ReportGenerator


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
report_generator = None
crawler = None
pdf_processor = None


def init_services():
    global retrieval, reranker, report_generator, crawler, pdf_processor
    
    try:
        retrieval = MultimodalRetrieval()
        print("✅ MultimodalRetrieval initialized")
    except Exception as e:
        print(f"⚠️  MultimodalRetrieval initialization error: {e}")
    
    try:
        reranker = Reranker()
        print("✅ Reranker initialized")
    except Exception as e:
        print(f"⚠️  Reranker initialization error: {e}")
    
    try:
        report_generator = ReportGenerator()
        print("✅ ReportGenerator initialized")
    except Exception as e:
        print(f"⚠️  ReportGenerator initialization error: {e}")
    
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


def ensure_sufficient_data(target_count: int = 50):
    api_key = os.getenv("VOLCENGINE_API_KEY")
    has_valid_api_key = api_key and api_key != "your_api_key_here"
    
    data_dir = Path(os.getenv("DATA_DIR", "./data"))
    pdf_dir = data_dir / "pdfs"
    processed_dir = data_dir / "processed"
    metadata_file = data_dir / "metadata.json"
    
    print("\n" + "=" * 60)
    print("📊 Checking data status...")
    print("=" * 60)
    
    metadata_count = 0
    if metadata_file.exists():
        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                metadata = json.load(f)
                metadata_count = len(metadata)
        except:
            pass
    
    pdf_count = 0
    if pdf_dir.exists():
        pdf_count = len(list(pdf_dir.glob("*.pdf")))
    
    processed_count = 0
    if processed_dir.exists():
        processed_count = len(list(processed_dir.glob("*_processed.json")))
    
    index_count = 0
    if retrieval and has_valid_api_key:
        try:
            index_stats = retrieval.get_index_stats()
            index_count = index_stats.get("count", 0)
        except:
            pass
    
    print(f"📄 Metadata papers: {metadata_count}")
    print(f"📚 PDF files: {pdf_count}")
    print(f"✂️  Processed papers: {processed_count}")
    print(f"🔍 Indexed chunks: {index_count}")
    print(f"🔑 API key configured: {'Yes' if has_valid_api_key else 'No'}")
    
    if metadata_count >= target_count and processed_count >= target_count:
        if has_valid_api_key and index_count > 0:
            print(f"\n✅ Data check passed! Already have sufficient data and index.")
            return True
        elif not has_valid_api_key:
            print(f"\n⚠️  Data check passed (papers and PDFs ready), but API key not configured for indexing.")
            print(f"   Run 'python prepare_data.py' after setting API key to build index.")
            return True
    
    print(f"\n⚠️  Insufficient data. Starting data pipeline...")
    
    if not crawler or not pdf_processor:
        print("❌ Required services not initialized")
        return False
    
    try:
        print("\n" + "=" * 60)
        print("📥 Step 1: Crawling papers from arXiv")
        print("=" * 60)
        papers = crawler.run(target_count=target_count)
        
        if not papers:
            print("❌ No papers crawled")
            return False
        
        print(f"\n✅ Crawled {len(papers)} papers")
        
        print("\n" + "=" * 60)
        print("📄 Step 2: Processing PDF files")
        print("=" * 60)
        processed_papers = pdf_processor.process_all_papers(papers)
        
        if not processed_papers:
            print("❌ No papers processed")
            return False
        
        print(f"\n✅ Processed {len(processed_papers)} papers")
        
        if has_valid_api_key and retrieval:
            print("\n" + "=" * 60)
            print("🔍 Step 3: Encoding and indexing papers")
            print("=" * 60)
            try:
                total_chunks = retrieval.encode_and_index_all_processed()
                print(f"\n✅ Indexed {total_chunks} chunks")
            except Exception as e:
                print(f"\n⚠️  Indexing skipped due to error: {e}")
                print(f"   You can run 'python prepare_data.py' later to build index.")
        else:
            print(f"\n⚠️  Skipping indexing step (API key not configured)")
            print(f"   Run 'python prepare_data.py' after setting API key to build index.")
        
        print("\n" + "=" * 60)
        print("✅ Data pipeline completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Data pipeline failed: {e}")
        return False


@app.on_event("startup")
async def startup_event():
    init_services()
    target_count = int(os.getenv("TARGET_PAPER_COUNT", 50))
    ensure_sufficient_data(target_count)


class SearchRequest(BaseModel):
    query: str
    n_results: int = 10
    use_rerank: bool = True
    top_k: Optional[int] = None


class ReportRequest(BaseModel):
    topic: str
    n_results: int = 15


class ConversationRequest(BaseModel):
    messages: List[Dict[str, str]]
    use_context: bool = True


@app.get("/")
async def root():
    return {
        "message": "Academic Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "search": "/api/search",
            "report": "/api/report",
            "conversation": "/api/conversation",
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
        
        if request.use_rerank and reranker and len(results) > 1:
            results = reranker.rerank(
                query=request.query,
                candidates=results,
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


@app.post("/api/report")
async def generate_report(request: ReportRequest):
    if not retrieval:
        raise HTTPException(status_code=500, detail="Retrieval service not initialized")

    if not report_generator:
        raise HTTPException(status_code=500, detail="Report generator service not initialized")

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

        report_result = report_generator.generate_report(
            topic=request.topic,
            search_results=search_results
        )

        return report_result
    except Exception as e:
        print(f"Error in /api/report: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/conversation")
async def conversation(request: ConversationRequest):
    if not retrieval or not report_generator:
        raise HTTPException(status_code=500, detail="Required services not initialized")
    
    try:
        last_message = request.messages[-1] if request.messages else None
        if not last_message or last_message.get("role") != "user":
            raise HTTPException(status_code=400, detail="Last message must be from user")
        
        user_query = last_message.get("content", "")
        
        search_results = []
        if request.use_context:
            search_results = retrieval.search(
                query=user_query,
                n_results=10
            )
        
        context_text = ""
        if search_results:
            papers = {}
            for result in search_results:
                metadata = result.get("metadata", {})
                paper_id = metadata.get("paper_id")
                if paper_id not in papers:
                    papers[paper_id] = {
                        "title": metadata.get("title", ""),
                        "authors": metadata.get("authors", ""),
                        "summary": metadata.get("summary", ""),
                        "chunks": []
                    }
                papers[paper_id]["chunks"].append(result.get("document", ""))
            
            context_text = "\n\n相关论文信息：\n"
            for i, (paper_id, paper_info) in enumerate(papers.items(), 1):
                context_text += f"\n[{i}] {paper_info['title']}\n"
                context_text += f"    作者: {paper_info['authors']}\n"
                context_text += f"    摘要: {paper_info['summary']}\n"
                context_text += f"    关键内容: {' '.join(paper_info['chunks'][:2])}\n"
        
        conversation_history = "\n".join([
            f"{msg.get('role', 'user')}: {msg.get('content', '')}"
            for msg in request.messages[:-1]
        ])
        
        prompt = f"""你是一位学术研究助手，请根据用户的问题提供专业、准确的回答。

对话历史：
{conversation_history}

{context_text}

用户问题：{user_query}

请根据上述信息回答用户的问题。如果提供了相关论文，请在回答中适当引用。回答要专业、清晰、有帮助。"""
        
        response = report_generator.client.chat.completions.create(
            model=report_generator.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        
        assistant_response = response.choices[0].message.content
        
        return {
            "success": True,
            "response": assistant_response,
            "papers_used": len(search_results) if search_results else 0
        }
        
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


async def sse_progress_generator(progress_events):
    for event in progress_events:
        yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
    yield f"data: {json.dumps({'event': 'done', 'data': {}}, ensure_ascii=False)}\n\n"


@app.post("/api/search/stream")
async def search_with_progress(request: SearchRequest):
    if not retrieval:
        raise HTTPException(status_code=500, detail="Retrieval service not initialized")

    async def event_generator():
        progress_events = []

        def progress_callback(stage: str, message: str, extra_data: Dict[str, Any]):
            progress_events.append({
                "stage": stage,
                "message": message,
                **extra_data
            })

        try:
            results = retrieval.search(
                query=request.query,
                n_results=request.n_results,
                progress_callback=progress_callback
            )

            if request.use_rerank and reranker and len(results) > 1:
                for event in progress_events:
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
                progress_events.clear()

                reranker_progress = []
                def rerank_callback(stage: str, message: str, extra_data: Dict[str, Any]):
                    reranker_progress.append({
                        "stage": stage,
                        "message": message,
                        **extra_data
                    })

                results = reranker.rerank(
                    query=request.query,
                    candidates=results,
                    top_k=request.top_k,
                    progress_callback=rerank_callback
                )

                for event in reranker_progress:
                    yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
            elif request.top_k:
                results = results[:request.top_k]

            for event in progress_events:
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

            yield f"data: {json.dumps({'event': 'search_complete', 'success': True, 'query': request.query, 'total_results': len(results), 'results': results}, ensure_ascii=False)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'success': False, 'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.post("/api/report/stream")
async def generate_report_with_progress(request: ReportRequest):
    if not retrieval:
        raise HTTPException(status_code=500, detail="Retrieval service not initialized")

    if not report_generator:
        raise HTTPException(status_code=500, detail="Report generator service not initialized")

    async def event_generator():
        try:
            search_results = retrieval.search(
                query=request.topic,
                n_results=request.n_results
            )

            if not search_results:
                yield f"data: {json.dumps({'event': 'report_error', 'success': False, 'error': 'No relevant papers found for this topic'}, ensure_ascii=False)}\n\n"
                return

            for event_data in report_generator.generate_report_stream(
                topic=request.topic,
                search_results=search_results
            ):
                yield f"data: {json.dumps(event_data, ensure_ascii=False)}\n\n"

        except Exception as e:
            print(f"Error in /api/report/stream: {type(e).__name__}: {e}")
            yield f"data: {json.dumps({'event': 'report_error', 'success': False, 'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))
    
    print(f"Starting Academic Recommendation API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)
