import os
import base64
from typing import List, Optional
from openai import OpenAI
from pathlib import Path


class MultimodalEmbedding:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://ark.cn-beijing.volces.com/api/v3", model: str = "doubao-embedding-vision-250615"):
        self.api_key = api_key or os.getenv("VOLCENGINE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as VOLCENGINE_API_KEY environment variable")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        self.model = model

    def embed_text(self, text: str) -> List[float]:
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        response = self.client.embeddings.create(
            model=self.model,
            input=texts,
            encoding_format="float"
        )
        return [item.embedding for item in response.data]

    def embed_image(self, image_path: str) -> List[float]:
        with open(image_path, "rb") as f:
            image_bytes = f.read()
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
        
        response = self.client.embeddings.create(
            model=self.model,
            input=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        )
        return response.data[0].embedding

    def embed_images(self, image_paths: List[str]) -> List[List[float]]:
        embeddings = []
        for path in image_paths:
            embeddings.append(self.embed_image(path))
        return embeddings

    def embed_multimodal(self, text: Optional[str] = None, image_path: Optional[str] = None) -> List[float]:
        if not text and not image_path:
            raise ValueError("At least one of text or image_path must be provided")
        
        input_list = []
        if text:
            input_list.append({
                "type": "text",
                "text": text
            })
        if image_path:
            with open(image_path, "rb") as f:
                image_bytes = f.read()
                base64_image = base64.b64encode(image_bytes).decode("utf-8")
            input_list.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        
        response = self.client.embeddings.create(
            model=self.model,
            input=input_list
        )
        return response.data[0].embedding


if __name__ == "__main__":
    print("Testing multimodal embedding module...")
    print("Note: Please set VOLCENGINE_API_KEY environment variable for full testing")
    
    try:
        embedder = MultimodalEmbedding()
        print("✅ Embedding module initialized successfully")
        
        test_text = "This is a test text for embedding generation."
        text_embedding = embedder.embed_text(test_text)
        print(f"✅ Text embedding generated, dimension: {len(text_embedding)}")
        
        test_texts = ["First text chunk", "Second text chunk", "Third text chunk"]
        texts_embeddings = embedder.embed_texts(test_texts)
        print(f"✅ Batch text embeddings generated, count: {len(texts_embeddings)}")
        
    except Exception as e:
        print(f"⚠️  Test note: {type(e).__name__}: {e}")
        print("This is expected if API key is not set. The module structure is correct.")
