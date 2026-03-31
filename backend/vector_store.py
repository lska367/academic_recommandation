
import uuid
from typing import List, Dict, Any, Optional
from pathlib import Path
import chromadb


class VectorStore:
    def __init__(self, persist_directory: str = "./chroma_db", collection_name: str = "academic_papers"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Academic paper chunks and embeddings"}
        )

    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, ids: Optional[List[str]] = None, embeddings: Optional[List[List[float]]] = None) -> List[str]:
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in texts]
        
        if metadatas is None:
            metadatas = [{} for _ in texts]
        
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings
        )
        
        return ids

    def similarity_search(self, query: str, n_results: int = 5, where: Optional[Dict[str, Any]] = None, query_embedding: Optional[List[float]] = None) -> List[Dict[str, Any]]:
        if query_embedding is not None:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where
            )
        else:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )
        
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i] if "distances" in results else None
            })
        
        return formatted_results

    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict[str, Any]] = None):
        self.collection.delete(ids=ids, where=where)

    def get_collection_stats(self) -> Dict[str, Any]:
        count = self.collection.count()
        return {
            "count": count,
            "collection_name": self.collection.name,
            "persist_directory": str(self.persist_directory)
        }

    def clear_collection(self):
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"description": "Academic paper chunks and embeddings"}
        )


if __name__ == "__main__":
    print("Testing vector store module...")
    
    vs = VectorStore(persist_directory="./test_chroma_db")
    
    print("Collection stats:", vs.get_collection_stats())
    
    test_texts = [
        "Machine learning is a subfield of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers.",
        "Natural language processing deals with text and speech.",
        "Computer vision analyzes visual content from images and videos.",
        "Reinforcement learning trains agents through trial and error."
    ]
    
    test_metadatas = [
        {"topic": "AI", "paper_id": "paper_1"},
        {"topic": "Deep Learning", "paper_id": "paper_2"},
        {"topic": "NLP", "paper_id": "paper_3"},
        {"topic": "Computer Vision", "paper_id": "paper_4"},
        {"topic": "RL", "paper_id": "paper_5"}
    ]
    
    print("\nAdding test documents...")
    ids = vs.add_texts(test_texts, test_metadatas)
    print("Added", len(ids), "documents")
    
    print("\nCollection stats:", vs.get_collection_stats())
    
    print("\nPerforming similarity search for 'neural networks'...")
    results = vs.similarity_search("neural networks", n_results=3)
    for result in results:
        print("  -", result["document"], "(distance:", "{:.4f}".format(result["distance"]), ")")
    
    print("\nPerforming similarity search with metadata filter (topic='NLP')...")
    results = vs.similarity_search("text", n_results=2, where={"topic": "NLP"})
    for result in results:
        print("  -", result["document"], "(metadata:", result["metadata"], ")")
    
    print("\nClearing test collection...")
    vs.clear_collection()
    print("Collection stats after clear:", vs.get_collection_stats())
    
    print("\nVector store module test completed!")

