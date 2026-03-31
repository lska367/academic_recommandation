
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI


class MultimodalReranker:
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        load_dotenv()
        
        self.api_key = api_key or os.getenv("VOLCENGINE_API_KEY")
        self.base_url = base_url or os.getenv("VOLCENGINE_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.model = model or os.getenv("CHAT_MODEL", "doubao-seed-2-0-lite-260215")
        
        if not self.api_key:
            raise ValueError("API key must be provided or set as VOLCENGINE_API_KEY environment variable")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def _build_rerank_prompt(self, query: str, results: List[Dict[str, Any]]) -&gt; str:
        prompt = f"""作为学术文献检索助手，请根据用户查询，对以下候选文献片段进行相关性评估和排序。

用户查询: {query}

候选文献片段:
"""
        
        for i, result in enumerate(results, 1):
            doc = result.get("document", "")
            metadata = result.get("metadata", {})
            title = metadata.get("title", "无标题")
            authors = metadata.get("authors", "无作者")
            
            prompt += f"""
[{i}]
标题: {title}
作者: {authors}
内容片段: {doc}

"""
        
        prompt += """请按照以下格式输出排序结果：
1. 首先列出每个文献片段的相关性分数（0-10分，10分表示最相关）
2. 然后按相关性从高到低重新排序，输出文献片段的编号列表

格式示例:
分数:
[1]: 8
[2]: 5
[3]: 9
排序: 3, 1, 2

请只输出上述格式的内容，不要有其他额外解释。"""
        
        return prompt
    
    def _parse_rerank_response(self, response: str, original_results: List[Dict[str, Any]]) -&gt; List[Dict[str, Any]]:
        try:
            lines = [line.strip() for line in response.split("\n") if line.strip()]
            
            scores_section = False
            order_section = False
            scores = {}
            order = []
            
            for line in lines:
                if line.startswith("分数:"):
                    scores_section = True
                    order_section = False
                    continue
                elif line.startswith("排序:"):
                    scores_section = False
                    order_section = True
                    continue
                
                if scores_section:
                    if line.startswith("[") and ":" in line:
                        try:
                            idx_part, score_part = line.split(":", 1)
                            idx = int(idx_part.strip("[]"))
                            score = float(score_part.strip())
                            scores[idx] = score
                        except:
                            continue
                
                if order_section:
                    try:
                        order_str = line.strip()
                        order = [int(x.strip()) for x in order_str.split(",") if x.strip().isdigit()]
                    except:
                        continue
            
            if order:
                reranked_results = []
                for idx in order:
                    if 1 &lt;= idx &lt;= len(original_results):
                        result = original_results[idx - 1].copy()
                        result["rerank_score"] = scores.get(idx, 0.0)
                        reranked_results.append(result)
                return reranked_results
            
            if scores:
                scored_results = []
                for idx, result in enumerate(original_results, 1):
                    result_copy = result.copy()
                    result_copy["rerank_score"] = scores.get(idx, 0.0)
                    scored_results.append(result_copy)
                
                scored_results.sort(key=lambda x: x["rerank_score"], reverse=True)
                return scored_results
            
            return original_results
        
        except Exception as e:
            print(f"Error parsing rerank response: {e}")
            return original_results
    
    def rerank(
        self,
        query: str,
        results: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -&gt; List[Dict[str, Any]]:
        if not results:
            return []
        
        if len(results) == 1:
            return results
        
        prompt = self._build_rerank_prompt(query, results)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            rerank_response = response.choices[0].message.content
            
            reranked_results = self._parse_rerank_response(rerank_response, results)
            
            if top_k is not None:
                reranked_results = reranked_results[:top_k]
            
            return reranked_results
        
        except Exception as e:
            print(f"Error during reranking: {e}")
            return results[:top_k] if top_k else results


def main():
    print("Testing multimodal reranker module...")
    
    try:
        reranker = MultimodalReranker()
        print("✅ Reranker initialized successfully")
        
        test_query = "What is transformer architecture?"
        
        test_results = [
            {
                "document": "Transformers use self-attention mechanisms to process sequences.",
                "metadata": {
                    "title": "Attention Is All You Need",
                    "authors": "Vaswani et al."
                }
            },
            {
                "document": "Convolutional neural networks are widely used in computer vision tasks.",
                "metadata": {
                    "title": "CNN Basics",
                    "authors": "Author A"
                }
            },
            {
                "document": "The transformer architecture revolutionized natural language processing.",
                "metadata": {
                    "title": "Transformers Overview",
                    "authors": "Author B"
                }
            }
        ]
        
        print("\n📚 Original results:")
        for i, r in enumerate(test_results, 1):
            print(f"  {i}. {r['document'][:50]}...")
        
        print("\n🔄 Reranking (note: may require valid API key)...")
        try:
            reranked = reranker.rerank(test_query, test_results)
            print("  ✅ Reranking completed (or fallback to original)")
            for i, r in enumerate(reranked, 1):
                score = r.get("rerank_score", "N/A")
                print(f"  {i}. {r['document'][:50]}... (score: {score})")
        except Exception as e:
            print(f"  ⚠️  Reranking test skipped: {type(e).__name__}")
        
        print("\nMultimodal reranker module test completed!")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
