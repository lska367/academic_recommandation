
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from openai import OpenAI
from datetime import datetime


class SurveyGenerator:
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
    
    def _aggregate_paper_info(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        papers = {}
        
        for result in results:
            metadata = result.get("metadata", {})
            paper_id = metadata.get("paper_id")
            
            if not paper_id:
                continue
            
            if paper_id not in papers:
                papers[paper_id] = {
                    "paper_id": paper_id,
                    "title": metadata.get("title", "无标题"),
                    "authors": metadata.get("authors", "无作者"),
                    "summary": metadata.get("summary", ""),
                    "chunks": []
                }
            
            papers[paper_id]["chunks"].append(result.get("document", ""))
        
        return {
            "papers": list(papers.values()),
            "total_papers": len(papers),
            "total_chunks": len(results)
        }
    
    def _build_survey_prompt(self, topic: str, paper_info: Dict[str, Any]) -> str:
        papers_list = paper_info["papers"]
        
        papers_text = ""
        for i, paper in enumerate(papers_list, 1):
            chunks_text = "\n".join(paper["chunks"][:3])
            papers_text += f"""
[{i}] 论文信息
标题: {paper['title']}
作者: {paper['authors']}
摘要: {paper['summary']}
关键内容: {chunks_text}

"""
        
        current_date = datetime.now().strftime("%Y年%m月%d日")
        
        prompt = f"""你是一位资深的学术研究专家，擅长撰写高质量的学术综述。请根据以下检索到的学术论文，撰写一份关于"{topic}"的学术综述报告。

检索到的论文信息:
{papers_text}

请按照以下结构撰写学术综述报告:

# {topic} 学术综述

## 摘要
简要概述该研究领域的背景、现状、主要进展和本文综述的目的。(150-200字)

## 1. 引言
- 研究背景与意义
- 该领域的发展历程简述
- 本文综述的范围和结构

## 2. 研究现状分析
根据检索到的论文，从以下方面进行分析:
- 核心研究问题
- 主要技术方法
- 代表性研究工作

## 3. 研究方法综述
详细介绍检索论文中提到的主要研究方法，包括:
- 理论基础
- 技术实现
- 方法的优缺点比较

## 4. 应用领域
介绍该研究主题在实际中的应用场景和案例。

## 5. 挑战与展望
- 当前研究面临的主要挑战
- 未来可能的研究方向
- 发展趋势预测

## 6. 总结
对整个综述进行总结，强调该领域的重要性和未来发展前景。

## 参考文献
列出本次综述所参考的论文，格式为:
[序号] 作者. 标题.

报告撰写要求:
1. 内容详实，逻辑清晰
2. 基于提供的论文内容，不要编造未提及的信息
3. 语言专业、准确、流畅
4. 总字数控制在3000-5000字
5. 生成时间: {current_date}

请直接输出完整的综述报告，无需额外说明。"""
        
        return prompt
    
    def generate_survey(
        self,
        topic: str,
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        if not search_results:
            return {
                "success": False,
                "error": "No search results provided to generate survey"
            }
        
        paper_info = self._aggregate_paper_info(search_results)
        
        if paper_info["total_papers"] == 0:
            return {
                "success": False,
                "error": "No valid papers found in search results"
            }
        
        prompt = self._build_survey_prompt(topic, paper_info)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            survey_content = response.choices[0].message.content
            
            return {
                "success": True,
                "topic": topic,
                "survey_content": survey_content,
                "paper_info": paper_info,
                "generated_at": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to generate survey: {str(e)}"
            }


def main():
    print("Testing survey generator module...")
    
    try:
        generator = SurveyGenerator()
        print("✅ Survey generator initialized successfully")
        
        test_topic = "深度学习在自然语言处理中的应用"
        
        test_results = [
            {
                "document": "Transformer架构已成为NLP领域的核心技术，通过自注意力机制实现了序列建模的突破。",
                "metadata": {
                    "paper_id": "paper1",
                    "title": "Attention Is All You Need",
                    "authors": "Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., & Polosukhin, I.",
                    "summary": "提出了Transformer架构，完全基于注意力机制，放弃了循环和卷积网络。"
                }
            },
            {
                "document": "BERT通过双向预训练显著提升了多项NLP任务的性能，包括文本分类、命名实体识别等。",
                "metadata": {
                    "paper_id": "paper2",
                    "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                    "authors": "Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.",
                    "summary": "引入了双向Transformer预训练模型BERT，在11项NLP任务上取得了state-of-the-art结果。"
                }
            },
            {
                "document": "GPT系列模型通过自回归方式进行大规模预训练，展现了强大的语言生成和理解能力。",
                "metadata": {
                    "paper_id": "paper3",
                    "title": "Language Models are Few-Shot Learners",
                    "authors": "Brown, T. B., Mann, B., Ryder, N., Subbiah, M., Kaplan, J., Dhariwal, P., ... & Amodei, D.",
                    "summary": "展示了GPT-3在few-shot学习上的惊人能力，参数规模达到1750亿。"
                }
            }
        ]
        
        print("\n📝 Test topic:", test_topic)
        print(f"📚 Number of paper chunks: {len(test_results)}")
        
        print("\n🚀 Generating survey (note: requires valid API key)...")
        try:
            result = generator.generate_survey(test_topic, test_results)
            if result["success"]:
                print("✅ Survey generated successfully!")
                print(f"   Total papers used: {result['paper_info']['total_papers']}")
                print(f"   Total chunks used: {result['paper_info']['total_chunks']}")
                preview = result["survey_content"][:500] + "..." if len(result["survey_content"]) > 500 else result["survey_content"]
                print(f"\n📄 Preview:\n{preview}")
            else:
                print(f"❌ Failed: {result['error']}")
        except Exception as e:
            print(f"⚠️  Survey generation test skipped: {type(e).__name__}")
        
        print("\nSurvey generator module test completed!")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
