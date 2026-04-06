
import os
import json
from typing import List, Dict, Any, Optional, Callable
from openai import OpenAI
from dotenv import load_dotenv


class Reranker:
    def __init__(self, api_key=None, base_url=None, model=None):
        load_dotenv()
        
        self.api_key = api_key or os.getenv("VOLCENGINE_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as VOLCENGINE_API_KEY environment variable")
        
        self.base_url = base_url or os.getenv("VOLCENGINE_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.model = model or os.getenv("CHAT_MODEL", "doubao-seed-2-0-lite-260215")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def _build_rerank_prompt(self, query, candidates):
        prompt = f"""作为学术论文推荐系统的专业重排序助手，请根据用户查询，对候选论文进行评分和排序。

用户查询：{query}

候选论文列表：
"""
        
        for i, candidate in enumerate(candidates, 1):
            metadata = candidate.get("metadata", {})
            title = metadata.get("title", "无标题")
            authors = metadata.get("authors", "无作者")
            summary = metadata.get("summary", "")
            document = candidate.get("document", "")
            
            prompt += f"""
候选论文 {i}:
标题: {title}
作者: {authors}
摘要: {summary}
内容片段: {document[:500]}...

"""
        
        prompt += """
请根据以下标准对每篇候选论文进行评分（0-10分）：
1. 相关性：论文主题与用户查询的匹配程度
2. 质量：论文的学术价值和可信度
3. 新颖性：研究内容的创新性

请严格按照以下JSON格式返回结果，不要包含任何其他文字：
{
    "reranked_papers": [
        {
            "index": 1,
            "score": 8.5,
            "reason": "论文主题与查询高度相关，研究内容具有创新性"
        }
    ]
}
"""
        return prompt
    
    def _parse_rerank_response(self, response):
        try:
            json_str = response
            json_start = json_str.find("{")
            json_end = json_str.rfind("}") + 1
            if json_start != -1 and json_end != -1:
                json_str = json_str[json_start:json_end]
            
            result = json.loads(json_str)
            return result.get("reranked_papers", [])
        except Exception as e:
            print(f"解析重排序响应失败: {e}")
            return []
    
    def rerank(self, query, candidates, top_k=None, progress_callback=None):
        if not candidates:
            return []

        if top_k is None:
            top_k = len(candidates)

        if progress_callback:
            progress_callback("rerank_start", f"开始对 {len(candidates)} 篇候选论文进行重排序", {"total": len(candidates)})

        prompt = self._build_rerank_prompt(query, candidates)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的学术论文推荐助手，擅长根据用户查询对论文进行评分和排序。请严格按照要求的JSON格式返回结果。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )

            if progress_callback:
                progress_callback("rerank_scoring", "论文打分完成，正在处理结果", {})

            response_text = response.choices[0].message.content
            rerank_results = self._parse_rerank_response(response_text)

            reranked_candidates = []
            for result in rerank_results:
                idx = result.get("index", 1) - 1
                if idx >= 0 and idx < len(candidates):
                    candidate = candidates[idx].copy()
                    candidate["rerank_score"] = result.get("score", 0)
                    candidate["rerank_reason"] = result.get("reason", "")
                    reranked_candidates.append(candidate)

            reranked_candidates.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)

            if progress_callback:
                progress_callback("rerank_complete", f"重排序完成，返回 Top {len(reranked_candidates[:top_k])} 篇论文", {"returned": len(reranked_candidates[:top_k])})

            return reranked_candidates[:top_k]

        except Exception as e:
            print(f"重排序过程出错: {e}")
            if progress_callback:
                progress_callback("rerank_error", f"重排序出错: {str(e)}", {})
            return candidates[:top_k]
    
    def aggregate_candidates_by_paper(self, candidates):
        paper_dict = {}
        
        for candidate in candidates:
            metadata = candidate.get("metadata", {})
            paper_id = metadata.get("paper_id")
            
            if not paper_id:
                continue
            
            if paper_id not in paper_dict:
                paper_dict[paper_id] = {
                    "paper_id": paper_id,
                    "title": metadata.get("title", ""),
                    "authors": metadata.get("authors", ""),
                    "summary": metadata.get("summary", ""),
                    "chunks": [],
                    "min_distance": candidate.get("distance", float("inf"))
                }
            
            paper_dict[paper_id]["chunks"].append({
                "document": candidate.get("document", ""),
                "distance": candidate.get("distance", float("inf"))
            })
            
            if candidate.get("distance", float("inf")) < paper_dict[paper_id]["min_distance"]:
                paper_dict[paper_id]["min_distance"] = candidate.get("distance", float("inf"))
        
        aggregated_papers = list(paper_dict.values())
        aggregated_papers.sort(key=lambda x: x["min_distance"])
        
        return aggregated_papers


def main():
    print("Testing reranker module...")
    
    try:
        reranker = Reranker()
        print("✅ Reranker module initialized successfully")
        
        test_query = "深度学习在自然语言处理中的应用"
        
        test_candidates = [
            {
                "metadata": {
                    "title": "Attention Is All You Need",
                    "authors": "Vaswani et al.",
                    "summary": "提出了Transformer架构，彻底改变了自然语言处理领域",
                    "paper_id": "paper_1"
                },
                "document": "本文提出了Transformer，一种完全基于注意力机制的网络架构，摒弃了循环和卷积神经网络...",
                "distance": 0.3
            },
            {
                "metadata": {
                    "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                    "authors": "Devlin et al.",
                    "summary": "介绍了BERT预训练模型，在多项NLP任务上取得了突破性成果",
                    "paper_id": "paper_2"
                },
                "document": "BERT通过在大规模文本语料上预训练深度双向Transformer表示，然后在特定任务上微调...",
                "distance": 0.25
            },
            {
                "metadata": {
                    "title": "ImageNet Classification with Deep Convolutional Neural Networks",
                    "authors": "Krizhevsky et al.",
                    "summary": "提出了AlexNet，开启了深度学习在计算机视觉领域的革命",
                    "paper_id": "paper_3"
                },
                "document": "本文训练了一个大型深度卷积神经网络来对ImageNet LSVRC-2010竞赛中的图像进行分类...",
                "distance": 0.6
            }
        ]
        
        print("\n📚 Test candidates:")
        for i, c in enumerate(test_candidates, 1):
            print(f"  {i}. {c['metadata']['title']} (distance: {c['distance']:.3f})")
        
        print("\n🔄 Testing candidate aggregation...")
        aggregated = reranker.aggregate_candidates_by_paper(test_candidates)
        print(f"✅ Aggregated {len(aggregated)} unique papers")
        
        print("\n⚠️  Note: Full reranking requires valid API key.")
        print("Reranker module test completed!")
        
    except Exception as e:
        print(f"⚠️  Test note: {type(e).__name__}: {e}")
        print("This is expected if API key is not set. The module structure is correct.")


if __name__ == "__main__":
    main()

