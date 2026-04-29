import re
from typing import List, Dict, Any, Optional
from collections import Counter


class PersonalizedRecommender:
    def __init__(self, retrieval=None, reranker=None):
        self.retrieval = retrieval
        self.reranker = reranker
        self.user_profiles = {}

    def extract_keywords(self, text: str) -> List[str]:
        chinese_pattern = r'[\u4e00-\u9fff]+'
        english_pattern = r'[a-zA-Z]{3,}'

        chinese_words = re.findall(chinese_pattern, text)
        english_words = re.findall(english_pattern, text.lower())

        keywords = chinese_words + english_words
        return [kw for kw in keywords if len(kw) >= 2]

    def analyze_user_interests(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        all_user_messages = []
        for msg in conversation_history:
            if msg.get("role") == "user":
                all_user_messages.append(msg.get("content", ""))

        combined_text = " ".join(all_user_messages)
        keywords = self.extract_keywords(combined_text)

        keyword_freq = Counter(keywords)
        top_keywords = keyword_freq.most_common(20)

        topics = []
        seen_topics = set()
        for keyword, freq in top_keywords:
            if keyword not in seen_topics and len(topics) < 10:
                topics.append({
                    "keyword": keyword,
                    "frequency": freq,
                    "relevance_score": min(freq * 2, 100)
                })
                seen_topics.add(keyword)

        research_areas = self._identify_research_areas(combined_text)

        return {
            "primary_interests": topics[:5],
            "secondary_interests": topics[5:10],
            "research_areas": research_areas,
            "total_messages_analyzed": len(all_user_messages),
            "query_suggestion": self._generate_query_suggestion(top_keywords[:5])
        }

    def _identify_research_areas(self, text: str) -> List[str]:
        area_keywords = {
            "深度学习": ["深度学习", "神经网络", "deep learning", "neural network"],
            "自然语言处理": ["自然语言处理", "NLP", "文本", "语言模型"],
            "计算机视觉": ["计算机视觉", "图像识别", "CV", "视觉"],
            "强化学习": ["强化学习", "reinforcement learning", "RL"],
            "机器学习": ["机器学习", "machine learning", "ML", "分类", "回归"],
            "数据挖掘": ["数据挖掘", "数据挖掘", "聚类"],
            "推荐系统": ["推荐系统", "recommendation", "协同过滤"],
            "知识图谱": ["知识图谱", "knowledge graph", "本体"]
        }

        detected_areas = []
        for area, keywords in area_keywords.items():
            for kw in keywords:
                if kw.lower() in text.lower():
                    detected_areas.append(area)
                    break

        return list(set(detected_areas))[:5]

    def _generate_query_suggestion(self, top_keywords: List[tuple]) -> str:
        if not top_keywords:
            return ""

        main_keyword = top_keywords[0][0]
        secondary_keywords = [kw[0] for kw in top_keywords[1:4]]

        query = main_keyword
        if secondary_keywords:
            query += f" {' '.join(secondary_keywords[:2])}"

        return query

    def get_personalized_recommendations(
        self,
        conversation_history: List[Dict],
        n_results: int = 10,
        use_rerank: bool = True
    ) -> Dict[str, Any]:
        if not self.retrieval:
            return {"success": False, "error": "Retrieval service not initialized"}

        interests = self.analyze_user_interests(conversation_history)

        suggested_query = interests.get("query_suggestion", "")
        if not suggested_query:
            return {"success": False, "error": "无法生成个性化查询"}

        print(f"[Personalized Recommender] Generated query: {suggested_query}")
        print(f"[Personalized Recommender] User interests: {interests['primary_interests'][:3]}")

        try:
            results = self.retrieval.search(
                query=suggested_query,
                n_results=n_results
            )

            if use_rerank and self.reranker and len(results) > 1:
                results = self.reranker.rerank(
                    query=suggested_query,
                    candidates=results,
                    top_k=min(n_results, len(results))
                )

            return {
                "success": True,
                "query": suggested_query,
                "user_profile": interests,
                "total_results": len(results),
                "results": results,
                "recommendation_type": "personalized",
                "based_on_history": len(conversation_history)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def enhance_search_with_context(
        self,
        original_query: str,
        conversation_history: List[Dict],
        n_results: int = 10
    ) -> Dict[str, Any]:
        if not self.retrieval:
            return {"success": False, "error": "Retrieval service not initialized"}

        interests = self.analyze_user_interests(conversation_history)
        context_keywords = [item["keyword"] for item in interests.get("primary_interests", [])]

        enhanced_query = original_query
        if context_keywords:
            enhanced_query += " " + " ".join(context_keywords[:3])

        print(f"[Personalized Recommender] Enhanced query: {enhanced_query}")

        try:
            results = self.retrieval.search(
                query=enhanced_query,
                n_results=n_results
            )

            if self.reranker and len(results) > 1:
                results = self.reranker.rerank(
                    query=original_query,
                    candidates=results,
                    top_k=n_results
                )

            return {
                "success": True,
                "original_query": original_query,
                "enhanced_query": enhanced_query,
                "context_keywords": context_keywords,
                "total_results": len(results),
                "results": results
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
