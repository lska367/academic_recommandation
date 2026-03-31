
import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

from embedding_module import MultimodalEmbedding
from vector_store import VectorStore


class MultimodalRetrieval:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        embedding_model: Optional[str] = None,
        chroma_db_path: Optional[str] = None,
        collection_name: Optional[str] = None,
        data_dir: Optional[str] = None
    ):
        load_dotenv()
        
        self.api_key = api_key or os.getenv("VOLCENGINE_API_KEY")
        self.base_url = base_url or os.getenv("VOLCENGINE_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL", "doubao-embedding-vision-250615")
        self.chroma_db_path = chroma_db_path or os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.collection_name = collection_name or os.getenv("COLLECTION_NAME", "academic_papers")
        self.data_dir = Path(data_dir or os.getenv("DATA_DIR", "./data"))
        self.processed_dir = self.data_dir / "processed"
        
        self.embedder = MultimodalEmbedding(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.embedding_model
        )
        
        self.vector_store = VectorStore(
            persist_directory=self.chroma_db_path,
            collection_name=self.collection_name
        )
    
    def encode_and_index_paper(self, processed_paper: Dict[str, Any]) -&gt; int:
        paper_id = processed_paper["paper_id"]
        chunks = processed_paper["chunks"]
        title = processed_paper["title"]
        authors = processed_paper["authors"]
        summary = processed_paper["summary"]
        
        print(f"Encoding and indexing paper: {paper_id}")
        
        embeddings = self.embedder.embed_texts(chunks)
        
        metadatas = []
        for i, chunk in enumerate(chunks):
            metadatas.append({
                "paper_id": paper_id,
                "chunk_index": i,
                "title": title,
                "authors": ", ".join(authors),
                "summary": summary,
                "total_chunks": len(chunks)
            })
        
        ids = [f"{paper_id}_chunk_{i}" for i in range(len(chunks))]
        
        self.vector_store.add_texts(
            texts=chunks,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )
        
        print(f"Successfully indexed {len(chunks)} chunks for paper: {paper_id}")
        return len(chunks)
    
    def encode_and_index_all_processed(self) -&gt; int:
        total_chunks = 0
        
        if not self.processed_dir.exists():
            print(f"Processed directory not found: {self.processed_dir}")
            return 0
        
        processed_files = list(self.processed_dir.glob("*_processed.json"))
        
        if not processed_files:
            print("No processed papers found")
            return 0
        
        print(f"Found {len(processed_files)} processed papers")
        
        for processed_file in processed_files:
            try:
                with open(processed_file, "r", encoding="utf-8") as f:
                    processed_paper = json.load(f)
                
                chunks_indexed = self.encode_and_index_paper(processed_paper)
                total_chunks += chunks_indexed
            except Exception as e:
                print(f"Error processing {processed_file}: {e}")
        
        print(f"Total chunks indexed: {total_chunks}")
        return total_chunks
    
    def search(
        self,
        query: str,
        n_results: int = 10,
        where: Optional[Dict[str, Any]] = None
    ) -&gt; List[Dict[str, Any]]:
        query_embedding = self.embedder.embed_text(query)
        
        results = self.vector_store.similarity_search(
            query=query,
            n_results=n_results,
            where=where,
            query_embedding=query_embedding
        )
        
        return results
    
    def get_index_stats(self) -&gt; Dict[str, Any]:
        return self.vector_store.get_collection_stats()
    
    def clear_index(self):
        self.vector_store.clear_collection()


def main():
    print("Testing multimodal retrieval module...")
    
    try:
        retrieval = MultimodalRetrieval()
        print("✅ Multimodal retrieval module initialized successfully")
        
        stats = retrieval.get_index_stats()
        print("Index stats:", stats)
        
        print("\n📚 Testing search (with empty index)...")
        results = retrieval.search("machine learning", n_results=3)
        print(f"Search results count: {len(results)}")
        
        print("\nMultimodal retrieval module test completed!")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
