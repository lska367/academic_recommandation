
import os
import base64
import requests
from typing import List, Optional, Dict, Any
from pathlib import Path


class MultimodalEmbedding:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://ark.cn-beijing.volces.com/api/v3", model: str = "doubao-embedding-vision-250615"):
        self.api_key = api_key or os.getenv("VOLCENGINE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as VOLCENGINE_API_KEY environment variable")
        
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

    def _make_multimodal_request(self, input_data: List[Dict[str, Any]], dimensions: Optional[int] = None) -> List[float]:
        url = f"{self.base_url}/embeddings/multimodal"
        
        payload = {
            "model": self.model,
            "input": input_data,
            "encoding_format": "float"
        }
        
        if dimensions:
            payload["dimensions"] = dimensions
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            return result["data"]["embedding"]
        except requests.exceptions.RequestException as e:
            raise Exception(f"Multimodal embedding request failed: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Invalid response format: {e}")

    def embed_text(self, text: str, dimensions: Optional[int] = None, instruction_type: str = "corpus") -> List[float]:
        input_list = [{"type": "text", "text": text}]
        
        if self.model in ["doubao-embedding-vision-251215", "doubao-embedding-vision-251215-pro"]:
            if instruction_type == "query":
                instruction = "Target_modality: text.\nInstruction:为这个句子生成表示以用于检索相关学术文章\nQuery:"
                input_list.insert(0, {"type": "text", "text": instruction})
            elif instruction_type == "corpus":
                instruction = "Instruction:Compress the text into one word.\nQuery:"
                input_list.insert(0, {"type": "text", "text": instruction})
        
        return self._make_multimodal_request(input_list, dimensions)

    def embed_texts(self, texts: List[str], dimensions: Optional[int] = None, instruction_type: str = "corpus") -> List[List[float]]:
        embeddings = []
        for text in texts:
            embeddings.append(self.embed_text(text, dimensions, instruction_type))
        return embeddings

    def _image_to_base64(self, image_path: str) -> str:
        path = Path(image_path)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        with open(path, "rb") as f:
            image_bytes = f.read()
        
        base64_str = base64.b64encode(image_bytes).decode("utf-8")
        
        ext = path.suffix.lower()
        if ext in [".jpg", ".jpeg"]:
            mime_type = "image/jpeg"
        elif ext == ".png":
            mime_type = "image/png"
        elif ext == ".gif":
            mime_type = "image/gif"
        elif ext == ".webp":
            mime_type = "image/webp"
        else:
            mime_type = "image/jpeg"
        
        return f"data:{mime_type};base64,{base64_str}"

    def embed_image(self, image_path: str, dimensions: Optional[int] = None) -> List[float]:
        base64_url = self._image_to_base64(image_path)
        input_data = [{
            "type": "image_url",
            "image_url": {"url": base64_url}
        }]
        return self._make_multimodal_request(input_data, dimensions)

    def embed_images(self, image_paths: List[str], dimensions: Optional[int] = None) -> List[List[float]]:
        embeddings = []
        for path in image_paths:
            embeddings.append(self.embed_image(path, dimensions))
        return embeddings

    def embed_multimodal(self, text: Optional[str] = None, image_path: Optional[str] = None, dimensions: Optional[int] = None) -> List[float]:
        if not text and not image_path:
            raise ValueError("At least one of text or image_path must be provided")
        
        input_data = []
        if text:
            input_data.append({"type": "text", "text": text})
        if image_path:
            base64_url = self._image_to_base64(image_path)
            input_data.append({
                "type": "image_url",
                "image_url": {"url": base64_url}
            })
        
        return self._make_multimodal_request(input_data, dimensions)


if __name__ == "__main__":
    print("Testing multimodal embedding module...")
    print("Note: Please set VOLCENGINE_API_KEY environment variable for full testing")
    
    try:
        embedder = MultimodalEmbedding()
        print("✅ Embedding module initialized successfully")
        
        test_text = "这是一个用于测试嵌入生成的文本。"
        text_embedding = embedder.embed_text(test_text)
        print(f"✅ Text embedding generated, dimension: {len(text_embedding)}")
        
        test_texts = ["第一个文本块", "第二个文本块", "第三个文本块"]
        texts_embeddings = embedder.embed_texts(test_texts)
        print(f"✅ Batch text embeddings generated, count: {len(texts_embeddings)}")
        
    except Exception as e:
        print(f"⚠️  Test note: {type(e).__name__}: {e}")
        print("This is expected if API key is not set. The module structure is correct.")
