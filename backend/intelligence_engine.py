"""
智能学术助手 v4.0 - 智能推荐与分析引擎
功能：
1. 对话内容深度分析（关键词提取、主题识别、意图理解）
2. 个性化论文推荐算法
3. 自动综述报告生成
4. 用户画像构建与更新
"""

import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
from datetime import datetime


class AcademicIntelligenceEngine:
    """
    学术智能分析引擎
    - NLP驱动的对话理解
    - 多维度兴趣建模
    - 智能推荐排序
    """

    # 学术领域知识库
    RESEARCH_DOMAINS = {
        "deep_learning": {
            "keywords": ["深度学习", "deep learning", "神经网络", "neural network", "CNN", "RNN", "LSTM", "GAN"],
            "description": "深度学习与神经网络",
            "related_topics": ["计算机视觉", "自然语言处理", "强化学习"]
        },
        "computer_vision": {
            "keywords": ["计算机视觉", "图像识别", "目标检测", "image recognition", "object detection", "CV", "视觉"],
            "description": "计算机视觉",
            "related_topics": ["深度学习", "图像处理", "医学影像"]
        },
        "nlp": {
            "keywords": ["自然语言处理", "NLP", "文本分类", "情感分析", "语言模型", "text classification", "sentiment analysis"],
            "description": "自然语言处理",
            "related_topics": ["深度学习", "Transformer", "信息检索"]
        },
        "transformer": {
            "keywords": ["Transformer", "BERT", "GPT", "注意力机制", "attention mechanism", "预训练模型", "pre-trained model"],
            "description": "Transformer架构与预训练模型",
            "related_topics": ["NLP", "多模态学习", "大语言模型"]
        },
        "reinforcement_learning": {
            "keywords": ["强化学习", "reinforcement learning", "RL", "Q-learning", "策略梯度", "policy gradient"],
            "description": "强化学习",
            "related_topics": ["深度学习", "机器人", "游戏AI"]
        },
        "multimodal_learning": {
            "keywords": ["多模态", "multimodal", "跨模态", "cross-modal", "视觉语言", "vision-language", "CLIP"],
            "description": "多模态学习",
            "related_topics": ["计算机视觉", "NLP", "Transformer"]
        },
        "graph_neural_network": {
            "keywords": ["图神经网络", "GNN", "图卷积", "knowledge graph", "知识图谱", "GCN"],
            "description": "图神经网络与知识图谱",
            "related_topics": ["推荐系统", "分子发现", "社交网络"]
        },
        "llm": {
            "keywords": ["大语言模型", "LLM", "大型语言模型", "ChatGPT", "LLaMA", "prompt engineering", "提示工程"],
            "描述": "大语言模型与应用",
            "related_topics": ["NLP", "Transformer", "Agent"]
        }
    }

    # 高频学术词汇表
    ACADEMIC_VOCABULARY = [
        "研究", "方法", "实验", "结果", "分析", "模型", "算法", "数据集",
        "性能", "准确率", "精度", "召回率", "F1", "损失函数", "优化",
        "训练", "推理", "特征提取", "嵌入", "表示学习", "迁移学习",
        "微调", "预训练", "fine-tuning", "baseline", "state-of-the-art", "SOTA"
    ]

    def __init__(self, retrieval=None, reranker=None, report_generator=None):
        self.retrieval = retrieval
        self.reranker = reranker
        self.report_generator = report_generator

    def extract_keywords(self, text: str, top_k: int = 15) -> List[Dict[str, Any]]:
        """
        从文本中提取关键词（支持中英文混合）
        返回：[{"keyword": str, "frequency": int, "type": str}]
        """
        # 中文分词（简单实现，实际可使用jieba等）
        chinese_pattern = r'[\u4e00-\u9fff]{2,}'
        chinese_words = re.findall(chinese_pattern, text)

        # 英文单词提取
        english_pattern = r'[a-zA-Z]{3,}(?:[-\']?[a-zA-Z]+)*'
        english_words = [w.lower() for w in re.findall(english_pattern, text.lower())]

        # 过滤停用词
        stop_words = {'的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都',
                      '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你',
                      '会', '着', '没有', '看', '好', '这', '那', '她', '他', '它',
                      'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
                      'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
                      'would', 'could', 'should', 'may', 'might', 'must', 'shall',
                      'can', 'need', 'dare', 'ought', 'used', 'to', 'of', 'in',
                      'for', 'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through'}

        chinese_filtered = [w for w in chinese_words if w not in stop_words]
        english_filtered = [w for w in english_words if w not in stop_words and len(w) >= 2]

        all_keywords = chinese_filtered + english_filtered

        # 统计频率
        keyword_freq = Counter(all_keywords)
        top_keywords = keyword_freq.most_common(top_k)

        result = []
        for keyword, freq in top_keywords:
            word_type = "chinese" if re.match(r'^[\u4e00-\u9fff]', keyword) else "english"
            result.append({
                "keyword": keyword,
                "frequency": freq,
                "type": word_type,
                "relevance_score": min(freq * 10, 100)
            })

        return result

    def identify_research_domains(self, text: str) -> List[Dict[str, Any]]:
        """
        识别文本涉及的研究领域
        返回：[{"domain": str, "confidence": float, "matched_keywords": []}]
        """
        text_lower = text.lower()
        detected_domains = []

        for domain_id, domain_info in self.RESEARCH_DOMAINS.items():
            matched_keywords = []
            for kw in domain_info["keywords"]:
                if kw.lower() in text_lower:
                    matched_keywords.append(kw)

            if matched_keywords:
                confidence = min(len(matched_keywords) / len(domain_info["keywords"]) * 100, 100)
                detected_domains.append({
                    "domain_id": domain_id,
                    "domain_name": domain_info["description"],
                    "confidence": round(confidence, 1),
                    "matched_keywords": matched_keywords[:5],
                    "related_topics": domain_info.get("related_topics", [])
                })

        # 按置信度排序
        detected_domains.sort(key=lambda x: x["confidence"], reverse=True)
        return detected_domains

    def analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """
        分析用户消息的意图
        返回意图类型和置信度
        """
        intent_patterns = {
            "paper_recommendation": {
                "patterns": ["推荐", "recommend", "找论文", "搜索", "search", "相关文献", "最新进展", "latest"],
                "weight": 1.0
            },
            "knowledge_inquiry": {
                "patterns": ["什么是", "what is", "如何", "how to", "解释", "explain", "原理", "principle", "介绍"],
                "weight": 0.9
            },
            "comparison_request": {
                "patterns": ["比较", "compare", "区别", "difference", "vs", "versus", "哪个更好", "优劣"],
                "weight": 0.85
            },
            "implementation_help": {
                "patterns": ["怎么实现", "how to implement", "代码", "code", "框架", "framework", "工具", "tool"],
                "weight": 0.8
            },
            "survey_report": {
                "patterns": ["综述", "survey", "总结", "summary", "发展历程", "history", "趋势", "trend", "现状"],
                "weight": 0.95
            }
        }

        message_lower = message.lower()
        detected_intents = []

        for intent_type, intent_info in intent_patterns.items():
            matches = sum(
                1 for pattern in intent_info["patterns"]
                if pattern.lower() in message_lower
            )
            
            if matches > 0:
                confidence = min(matches * intent_info["weight"], 1.0)
                detected_intents.append({
                    "intent": intent_type,
                    "confidence": confidence,
                    "matches": matches
                })

        if detected_intents:
            detected_intents.sort(key=lambda x: x["confidence"], reverse=True)
            return {
                "primary_intent": detected_intents[0]["intent"],
                "confidence": detected_intents[0]["confidence"],
                "all_intents": detected_intents
            }
        
        return {
            "primary_intent": "general_chat",
            "confidence": 0.5,
            "all_intents": []
        }

    def build_user_profile(
        self, 
        conversation_history: List[Dict],
        max_messages: int = 50
    ) -> Dict[str, Any]:
        """
        构建完整的用户研究画像
        
        输入：对话历史 [{"role": "user/assistant", "content": "..."}]
        输出：用户画像字典
        """
        # 提取所有用户消息
        user_messages = [
            msg["content"] for msg in conversation_history
            if msg.get("role") == "user"
        ][-max_messages:]

        if not user_messages:
            return self._empty_profile()

        combined_text = "\n".join(user_messages)

        # 1. 关键词分析
        keywords = self.extract_keywords(combined_text, top_k=20)
        primary_interests = keywords[:10]
        secondary_interests = keywords[10:]

        # 2. 领域识别
        domains = self.identify_research_domains(combined_text)
        primary_domain = domains[0] if domains else None

        # 3. 意图分布统计
        intent_distribution = Counter()
        for msg in user_messages:
            intent_analysis = self.analyze_user_intent(msg)
            intent_distribution[intent_analysis["primary_intent"]] += 1

        # 4. 生成智能查询建议
        suggested_queries = self._generate_suggested_queries(primary_interests, primary_domain)

        # 5. 研究成熟度评估
        maturity_level = self._assess_research_maturity(user_messages, domains)

        profile = {
            "analysis_timestamp": datetime.now().isoformat(),
            "messages_analyzed": len(user_messages),
            "primary_interests": primary_interests,
            "secondary_interests": secondary_interests,
            "research_domains": domains,
            "primary_domain": primary_domain,
            "intent_distribution": dict(intent_distribution.most_common(5)),
            "suggested_queries": suggested_queries,
            "research_maturity": maturity_level,
            "engagement_score": self._calculate_engagement_score(conversation_history),
            "recommendation_readiness": self._check_recommendation_readiness(domains, keywords)
        }

        return profile

    def generate_paper_recommendations(
        self,
        user_profile: Dict,
        n_results: int = 10,
        use_rerank: bool = True
    ) -> Dict[str, Any]:
        """
        基于用户画像生成个性化论文推荐
        """
        if not self.retrieval:
            return {"success": False, "error": "检索服务未初始化"}

        try:
            # 构建增强查询
            query_parts = []
            
            # 主要兴趣关键词
            primary_kw = [item["keyword"] for item in user_profile.get("primary_interests", [])[:5]]
            if primary_kw:
                query_parts.append(" ".join(primary_kw))

            # 领域名称
            if user_profile.get("primary_domain"):
                query_parts.append(user_profile["primary_domain"]["domain_name"])

            # 使用建议的查询
            suggested = user_profile.get("suggested_queries", [])
            if suggested:
                query_parts.insert(0, suggested[0])

            enhanced_query = " ".join(query_parts[:3])  # 合并前3个部分
            
            print(f"[Recommendation] Generated query: {enhanced_query}")

            # 执行检索
            results = self.retrieval.search(query=enhanced_query, n_results=n_results + 5)

            if not results:
                return {"success": False, "error": "未找到匹配的论文"}

            # 重排序
            if use_rerank and self.reranker and len(results) > 1:
                results = self.reranker.rerank(
                    query=enhanced_query,
                    candidates=results,
                    top_k=n_results
                )
            else:
                results = results[:n_results]

            # 为每篇论文添加推荐理由
            enriched_results = []
            for i, paper in enumerate(results):
                metadata = paper.get("metadata", {})
                
                recommendation_rationale = self._generate_recommendation_rationale(
                    paper, user_profile, i + 1
                )

                enriched_results.append({
                    **paper,
                    "rank": i + 1,
                    "recommendation_rationale": recommendation_rationale,
                    "relevance_to_user": self._calculate_relevance_score(paper, user_profile)
                })

            return {
                "success": True,
                "query_used": enhanced_query,
                "total_results": len(enriched_results),
                "results": enriched_results,
                "based_on_profile": {
                    "primary_domain": user_profile.get("primary_domain", {}).get("domain_name"),
                    "top_interests": [item["keyword"] for item in user_profile.get("primary_interests", [])[:3]]
                }
            }

        except Exception as e:
            print(f"[Recommendation Error]: {e}")
            return {"success": False, "error": str(e)}

    def generate_survey_report_content(
        self,
        topic: str,
        papers: List[Dict],
        user_context: Dict = None
    ) -> str:
        """
        生成学术综述报告内容（供邮件发送使用）
        """
        if not self.report_generator or not papers:
            return ""

        try:
            # 准备论文摘要
            papers_summary = ""
            for i, paper in enumerate(papers[:8], 1):
                metadata = paper.get("metadata", {})
                papers_summary += f"\n[{i}] {metadata.get('title', '无标题')}\n"
                papers_summary += f"    作者: {metadata.get('authors', '未知')}\n"
                papers_summary += f"    核心贡献: {metadata.get('summary', '')[:200]}...\n"

            context_info = ""
            if user_context:
                interests = user_context.get("primary_interests", [])
                domain = user_context.get("primary_domain")
                context_info = f"\n\n用户背景信息:\n"
                context_info += f"- 主要研究方向: {domain.get('domain_name') if domain else '未明确'}\n"
                context_info += f"- 关注的关键词: {', '.join([i['keyword'] for i in interests[:5]])}\n"

            prompt = f"""请为以下学术主题生成一份专业的中文综述报告。

主题: {topic}
{context_info}

参考文献:
{papers_summary}

请按以下结构撰写报告：

# {topic} 研究综述报告

## 1. 研究背景与意义
（阐述该领域的重要性和应用价值）

## 2. 核心技术与方法
（总结该领域的主要技术路线和方法论）

## 3. 重要工作回顾
（对上述参考文献进行归纳和评述，指出关键创新点）

## 4. 当前挑战与局限
（讨论现有方法的不足之处）

## 5. 未来发展趋势
（展望未来可能的研究方向）

## 6. 推荐阅读清单
（列出最重要的3-5篇论文及简要说明）

要求：
- 语言专业但不晦涩
- 逻辑清晰，层次分明
- 引用具体论文时标注编号
- 总字数控制在2000-3000字"""

            response = self.report_generator.client.chat.completions.create(
                model=self.report_generator.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=3500
            )

            report_content = response.choices[0].message.content
            return report_content

        except Exception as e:
            print(f"[Survey Generation Error]: {e}")
            return f"报告生成失败: {str(e)}"

    # ========== 私有辅助方法 ==========

    def _empty_profile(self) -> Dict:
        """返回空的用户画像"""
        return {
            "messages_analyzed": 0,
            "primary_interests": [],
            "research_domains": [],
            "suggested_queries": [],
            "research_maturity": "beginner",
            "recommendation_readiness": False
        }

    def _generate_suggested_queries(
        self, 
        interests: List[Dict], 
        domain: Dict
    ) -> List[str]:
        """基于兴趣和领域生成建议查询"""
        queries = []

        if interests:
            main_keyword = interests[0]["keyword"]
            secondary = [i["keyword"] for i in interests[1:4]]
            
            # 组合主查询
            queries.append(f"{main_keyword} {' '.join(secondary[:2])}")
            
            # 领域特定查询
            if domain:
                queries.append(f"{domain['domain_name']} {main_keyword} 最新进展")

            # 应用导向查询
            if any(kw["keyword"] in ["方法", "算法", "模型"] for kw in interests):
                queries.append(f"{main_keyword} 方法对比 实验评估")

        return queries[:3]

    def _assess_research_maturity(
        self, 
        messages: List[str], 
        domains: List[Dict]
    ) -> str:
        """评估用户的研究成熟度"""
        technical_terms_count = 0
        for msg in messages:
            terms = [term for term in self.ACADEMIC_VOCABULARY if term in msg]
            technical_terms_count += len(terms)

        avg_technical_per_msg = technical_terms_count / max(len(messages), 1)

        domain_specificity = len(domains) if domains else 0

        if avg_technical_per_msg >= 3 and domain_specificity >= 2:
            return "advanced"
        elif avg_technical_per_msg >= 1.5 and domain_specificity >= 1:
            return "intermediate"
        else:
            return "beginner"

    def _calculate_engagement_score(self, history: List[Dict]) -> float:
        """计算用户参与度分数 (0-100)"""
        if not history:
            return 0.0

        total_messages = len(history)
        user_messages = sum(1 for m in history if m.get("role") == "user")
        
        avg_user_length = 0
        user_contents = [m["content"] for m in history if m.get("role") == "user"]
        if user_contents:
            avg_user_length = sum(len(c) for c in user_contents) / len(user_contents)

        # 计算得分
        engagement = 0.0
        
        # 消息数量因子 (最多50分)
        engagement += min(total_messages * 2, 50)
        
        # 用户活跃度因子 (最多30分)
        user_ratio = user_messages / max(total_messages, 1)
        engagement += user_ratio * 30
        
        # 消息质量因子 (平均长度，最多20分)
        quality_score = min(avg_user_length / 20 * 20, 20)
        engagement += quality_score

        return round(min(engagement, 100), 1)

    def _check_recommendation_readiness(
        self, 
        domains: List[Dict], 
        keywords: List[Dict]
    ) -> bool:
        """检查是否具备足够的推荐依据"""
        has_clear_domain = len(domains) >= 1
        has_enough_interests = len(keywords) >= 3
        
        return has_clear_domain and has_enough_interests

    def _generate_recommendation_rationale(
        self, 
        paper: Dict, 
        profile: Dict, 
        rank: int
    ) -> str:
        """为推荐论文生成理由说明"""
        metadata = paper.get("metadata", {})
        title = metadata.get("title", "")
        
        rationales = []
        
        # 基于领域的理由
        if profile.get("primary_domain"):
            domain_name = profile["primary_domain"]["domain_name"]
            rationales.append(f"属于{domain_name}核心研究领域")
        
        # 基于关键词匹配的理由
        interests = [item["keyword"].lower() for item in profile.get("primary_interests", [])[:5]]
        title_lower = title.lower()
        matched_interests = [kw for kw in interests if kw in title_lower]
        if matched_interests:
            rationales.append(f"与您关注的'{matched_interests[0]}'高度相关")
        
        # 基于排名的理由
        if rank <= 3:
            rationales.append(f"排名第{位}，是该方向的高影响力工作")
        
        return "；".join(rationales) if rationales else "根据您的研究兴趣智能推荐"

    def _calculate_relevance_score(
        self, 
        paper: Dict, 
        profile: Dict
    ) -> float:
        """计算论文与用户的关联度 (0-100)"""
        score = 50.0  # 基础分
        
        metadata = paper.get("metadata", {})
        title = (metadata.get("title", "") + " " + metadata.get("summary", "")).lower()
        
        # 关键词匹配加分
        for interest in profile.get("primary_interests", [])[:5]:
            kw = interest["keyword"].lower()
            if kw in title:
                score += 8
            elif any(c in kw for c in title.split()):
                score += 3
        
        # 领域匹配加分
        if profile.get("primary_domain"):
            domain_keywords = profile["primary_domain"].get("matched_keywords", [])
            for dk in domain_keywords:
                if dk.lower() in title:
                    score += 5
        
        return round(min(score, 99), 1)
