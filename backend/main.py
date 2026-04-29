"""
智能学术助手 v4.0 - 主应用入口
核心功能：
1. 邮箱验证与用户管理
2. AI学术聊天机器人
3. 智能推荐引擎
4. 定时邮件推送服务
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# 导入核心模块
from arxiv_crawler import ArxivCrawler
from pdf_processor import PDFProcessor
from multimodal_retrieval import MultimodalRetrieval
from reranker import Reranker
from report_generator import ReportGenerator

# 导入v4.0新模块
from user_manager import SecureUserManager
from intelligence_engine import AcademicIntelligenceEngine
from email_service import EnhancedEmailService
from task_scheduler import IntelligentTaskScheduler


load_dotenv()

app = FastAPI(
    title="智能学术助手 API",
    version="4.0.0",
    description="基于邮箱验证的AI学术聊天助手系统"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局服务实例
retrieval = None
reranker = None
report_generator = None
crawler = None
pdf_processor = None

# v4.0 核心服务
user_manager = None
intelligence_engine = None
email_service = None
task_scheduler = None


def init_services():
    """初始化所有服务模块"""
    global retrieval, reranker, report_generator, crawler, pdf_processor
    global user_manager, intelligence_engine, email_service, task_scheduler
    
    print("\n" + "="*60)
    print("🚀 初始化智能学术助手 v4.0 服务")
    print("="*60 + "\n")

    # 基础检索服务
    try:
        retrieval = MultimodalRetrieval()
        print("✅ 多模态检索服务就绪")
    except Exception as e:
        print(f"⚠️  检索服务初始化异常: {e}")

    try:
        reranker = Reranker()
        print("✅ 重排序服务就绪")
    except Exception as e:
        print(f"⚠️  重排序服务初始化异常: {e}")

    try:
        report_generator = ReportGenerator()
        print("✅ 报告生成服务就绪")
    except Exception as e:
        print(f"⚠️  报告生成服务初始化异常: {e}")

    # 数据准备服务（保留历史数据）
    try:
        crawler = ArxivCrawler()
        pdf_processor = PDFProcessor()
        print("✅ 数据处理服务就绪")
        
        _ensure_data_ready()
    except Exception as e:
        print(f"⚠️  数据处理服务初始化异常: {e}")

    # v4.0 核心服务
    try:
        user_manager = SecureUserManager("./secure_data/users")
        print("✅ 安全用户管理系统就绪")
    except Exception as e:
        print(f"❌ 用户管理系统初始化失败: {e}")

    try:
        intelligence_engine = AcademicIntelligenceEngine(
            retrieval=retrieval,
            reranker=reranker,
            report_generator=report_generator
        )
        print("✅ 学术智能分析引擎就绪")
    except Exception as e:
        print(f"❌ 智能引擎初始化失败: {e}")

    try:
        email_service = EnhancedEmailService()
        if email_service.is_configured():
            print("✅ 邮件通知服务就绪 (已配置)")
        else:
            print("⚠️  邮件通知服务 (未配置SMTP)")
    except Exception as e:
        print(f"❌ 邮件服务初始化失败: {e}")

    try:
        task_scheduler = IntelligentTaskScheduler(
            user_manager=user_manager,
            intelligence_engine=intelligence_engine,
            email_service=email_service,
            retrieval=retrieval,
            reranker=reranker,
            report_generator=report_generator
        )
        print("✅ 智能任务调度器就绪")
    except Exception as e:
        print(f"❌ 调度器初始化失败: {e}")

    print("\n" + "="*60)
    print("✨ 所有服务初始化完成！")
    print("="*60 + "\n")


def _ensure_data_ready(target_count: int = 50):
    """确保有足够的历史数据可用"""
    data_dir = Path(os.getenv("DATA_DIR", "./data"))
    metadata_file = data_dir / "metadata.json"
    
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            if len(metadata) >= target_count:
                print(f"\n📊 发现 {len(metadata)} 条已处理的论文数据")
                return True
        except:
            pass
    
    print("\n📦 正在准备论文数据...")
    papers = crawler.run(target_count=target_count)
    if papers:
        processed = pdf_processor.process_all_papers(papers)
        if processed and retrieval:
            try:
                retrieval.encode_and_index_all_processed()
            except:
                pass
        return True
    return False


@app.on_event("startup")
async def startup_event():
    """应用启动时执行"""
    init_services()
    
    # 启动调度器
    if task_scheduler:
        task_scheduler.start()


# ========== 数据模型 ==========

class EmailVerificationRequest(BaseModel):
    email: str

class ChatMessageRequest(BaseModel):
    message: str
    user_id: str
    conversation_id: Optional[str] = None

class PreferencesUpdateRequest(BaseModel):
    preferences: Dict[str, Any]


# ========== 公开端点 ==========

@app.get("/")
async def root():
    return {
        "service": "智能学术助手",
        "version": "4.0.0",
        "description": "基于邮箱验证的AI学术聊天助手",
        "core_features": [
            "邮箱验证登录",
            "AI学术对话机器人",
            "个性化论文推荐",
            "定时邮件推送",
            "自动综述报告"
        ],
        "api_endpoints": {
            "auth": "/api/auth/verify-email",
            "chat": "/api/chat/stream",
            "user": "/api/user/*",
            "recommendations": "/api/recommendations/*",
            "scheduler": "/api/scheduler/*",
            "email": "/api/email/*"
        }
    }


@app.get("/health")
async def health_check():
    services_status = {
        "user_manager": user_manager is not None,
        "intelligence_engine": intelligence_engine is not None,
        "email_service": email_service is not None,
        "task_scheduler": task_scheduler is not None,
        "retrieval": retrieval is not None,
        "email_configured": email_service.is_configured() if email_service else False
    }
    return {"status": "healthy", "services": services_status}


# ========== 认证端点 ==========

@app.post("/api/auth/verify-email")
async def verify_email(request: EmailVerificationRequest):
    """
    邮箱验证入口 - 用户首次访问必须调用此接口
    自动注册新用户或登录已有用户
    """
    if not user_manager:
        raise HTTPException(status_code=500, detail="用户服务未初始化")

    result = user_manager.authenticate_user(request.email)

    if result.get("success"):
        # 注册为邮件订阅者
        if email_service:
            email_service.register_subscriber(
                user_id=result["user_id"],
                email=request.email
            )

        # 创建初始对话
        conv_id = user_manager.create_conversation(
            user_id=result["user_id"], 
            title="首次对话"
        )

        return {
            **result,
            "conversation_id": conv_id,
            "is_new_user": result.get("message") == "注册成功"
        }

    raise HTTPException(status_code=400, detail=result.get("error", "验证失败"))


# ========== 聊天端点（核心） ==========

@app.post("/api/chat/stream")
async def chat_stream(request: ChatMessageRequest):
    """
    AI学术聊天流式接口
    
    功能：
    - 接收用户消息
    - 保存到对话历史
    - 分析用户意图
    - 检索相关论文
    - 流式返回智能回复
    """
    if not (user_manager and intelligence_engine and report_generator):
        raise HTTPException(status_code=500, detail="核心服务未就绪")

    async def event_generator():
        try:
            user_id = request.user_id
            message = request.message
            
            # Step 1: 确保对话存在
            conv_id = request.conversation_id
            if not conv_id:
                conv_id = user_manager.create_conversation(user_id, message[:30])
                yield f"data: {json.dumps({'event': 'conversation_created', 'data': {'conversation_id': conv_id}}, ensure_ascii=False)}\n\n"

            # Step 2: 保存用户消息
            user_manager.add_message_to_conversation(conv_id, user_id, "user", message)
            yield f"data: {json.dumps({'event': 'stage', 'stage': 'analyzing', 'message': '正在分析您的问题...'}, ensure_ascii=False)}\n\n"

            # Step 3: 加载对话历史用于上下文理解
            conversation_history = []
            conv = user_manager.get_conversation(conv_id, user_id)
            if conv:
                conversation_history = conv.get("messages", [])

            # Step 4: 意图分析
            intent = intelligence_engine.analyze_user_intent(message)
            yield f"data: {json.dumps({'event': 'intent_detected', 'intent': intent}, ensure_ascii=False)}\n\n"

            # Step 5: 增强查询并检索论文
            enhanced_query = message
            if len(conversation_history) > 2 and retrieval:
                enhancement_result = intelligence_engine.enhance_search_with_context(
                    original_query=message,
                    conversation_history=conversation_history[:-1],
                    n_results=10
                )
                if enhancement_result.get("success"):
                    enhanced_query = enhancement_result["enhanced_query"]
                    yield f"data: {json.dumps({'event': 'query_enhanced', 'original': message, 'enhanced': enhanced_query}, ensure_ascii=False)}\n\n"

            search_results = []
            if retrieval:
                yield f"data: {json.dumps({'event': 'stage', 'stage': 'searching', 'message': '正在检索相关学术论文...'}, ensure_ascii=False)}\n\n"
                
                search_results = retrieval.search(query=enhanced_query, n_results=10)

                if search_results and reranker:
                    yield f"data: {json.dumps({'event': 'stage', 'stage': 'reranking', 'message': '优化排序结果...'}, ensure_ascii=False)}\n\n"
                    search_results = reranker.rerank(
                        query=message,
                        candidates=search_results,
                        top_k=min(8, len(search_results))
                    )

            # Step 6: 构建回复上下文
            context_text = ""
            if search_results:
                papers_info = {}
                for result in search_results[:5]:
                    metadata = result.get("metadata", {})
                    pid = metadata.get("paper_id")
                    if pid not in papers_info:
                        papers_info[pid] = {
                            "title": metadata.get("title", ""),
                            "authors": metadata.get("authors", ""),
                            "summary": metadata.get("summary", "")
                        }

                context_text = "\n\n【相关研究文献】\n"
                for i, (pid, info) in enumerate(list(papers_info.items())[:4], 1):
                    context_text += f"[{i}] {info['title']}\n作者: {info['authors']}\n摘要: {info['summary'][:200]}...\n"

                yield f"data: {json.dumps({'event': 'papers_found', 'count': len(search_results)}, ensure_ascii=False)}\n\n"

            # Step 7: 构建对话历史文本
            history_text = "\n".join([
                f"{m.get('role')}: {m.get('content', '')}"
                for m in conversation_history[-8:] if m.get('role') in ['user', 'assistant']
            ])

            # Step 8: 生成智能回复（流式）
            yield f"data: {json.dumps({'event': 'stage', 'stage': 'generating', 'message': '生成专业回复中...'}, ensure_ascii=False)}\n\n"

            prompt = f"""你是一位专业的学术研究助手，擅长根据用户的研究需求提供精准的学术指导。

{f'【对话上下文】\n{history_text}' if history_text else ''}

{context_text}

【用户当前问题】
{message}

请提供：
1. 直接回答用户的问题（2-3句话）
2. 如果有相关论文，选择最相关的2-3篇进行推荐，说明为什么重要
3. 给出后续可能的研究方向建议
4. 使用中文，语言专业但易懂"""

            response = report_generator.client.chat.completions.create(
                model=report_generator.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.75,
                max_tokens=2000,
                stream=True
            )

            full_content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content_chunk = chunk.choices[0].delta.content
                    full_content += content_chunk
                    
                    yield f"data: {json.dumps({
                        'event': 'streaming_chunk',
                        'content': content_chunk,
                        'fullContent': full_content
                    }, ensure_ascii=False)}\n\n"

            # Step 9: 保存助手回复
            user_manager.add_message_to_conversation(conv_id, user_id, "assistant", full_content)

            # Step 10: 更新用户画像
            all_user_msgs = [
                m["content"] for m in conversation_history 
                if m.get("role") == "user"
            ]
            all_user_msgs.append(message)
            
            updated_profile = intelligence_engine.build_user_profile([
                {"role": "user", "content": msg} for msg in all_user_msgs[-30:]
            ])

            interests = [item["keyword"] for item in updated_profile.get("primary_interests", [])]
            domains = [d["domain_name"] for d in updated_profile.get("research_domains", [])]
            user_manager.update_research_interests(user_id, interests + domains)

            yield f"data: {json.dumps({
                'event': 'profile_updated',
                'profile': {
                    'top_interests': interests[:5],
                    'domains': domains
                }
            }, ensure_ascii=False)}\n\n"

            # 最终完成事件
            yield f"data: {json.dumps({
                'event': 'chat_complete',
                'data': {
                    'success': True,
                    'response': full_content,
                    'papers_found': len(search_results),
                    'conversation_id': conv_id,
                    'user_profile_summary': {
                        'interests': interests[:3],
                        'domains': domains
                    }
                }
            }, ensure_ascii=False)}\n\n"

        except Exception as e:
            print(f"[Chat Error]: {type(e).__name__}: {e}")
            yield f"data: {json.dumps({'event': 'error', 'error': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )


# ========== 用户管理端点 ==========

@app.get("/api/user/profile/{user_id}")
async def get_user_profile(user_id: str):
    if not user_manager:
        raise HTTPException(status_code=500, detail="用户服务未初始化")
    
    profile = user_manager.get_user(user_id)
    if not profile:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"success": True, "profile": profile}


@app.put("/api/user/preferences/{user_id}")
async def update_preferences(user_id: str, request: PreferencesUpdateRequest):
    if not user_manager:
        raise HTTPException(status_code=500, detail="用户服务未初始化")
    
    result = user_manager.update_user_preferences(user_id, request.preferences)
    return result


@app.get("/api/user/conversations/{user_id}")
async def get_conversations(user_id: str, limit: int = 20):
    if not user_manager:
        raise HTTPException(status_code=500, detail="用户服务未初始化")
    
    conversations = user_manager.get_user_conversations(user_id, limit=limit)
    return {"success": True, "conversations": conversations, "total": len(conversations)}


@app.get("/api/user/conversation/{user_id}/{conv_id}")
async def get_conversation_detail(user_id: str, conv_id: str):
    if not user_manager:
        raise HTTPException(status_code=500, detail="用户服务未初始化")
    
    conv = user_manager.get_conversation(conv_id, user_id)
    if not conv:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    return {"success": True, "conversation": conv}


# ========== 推荐端点 ==========

@app.post("/api/recommendations/personalized/{user_id}")
async def get_personalized_recommendations(user_id: str):
    if not (intelligence_engine and user_manager):
        raise HTTPException(status_code=500, detail="必要服务未初始化")

    # 获取用户对话历史
    messages = user_manager.get_all_user_messages_for_analysis(user_id)
    if not messages:
        raise HTTPException(status_code=400, detail="暂无足够的对话记录")

    conversation_history = [
        {"role": msg.get("role", "user"), "content": msg.get("content", "")}
        for msg in messages[-40:]
    ]

    # 构建用户画像
    user_profile = intelligence_engine.build_user_profile(conversation_history)
    
    # 生成推荐
    recommendations = intelligence_engine.generate_paper_recommendations(
        user_profile=user_profile,
        n_results=10,
        use_rerank=True
    )

    return recommendations


# ========== 邮件服务端点 ==========

@app.get("/api/email/status")
async def get_email_status():
    if not email_service:
        raise HTTPException(status_code=500, detail="邮件服务未初始化")
    
    stats = email_service.get_statistics()
    return {"success": True, **stats}


@app.post("/api/email/test")
async def test_email_connection():
    if not email_service:
        raise HTTPException(status_code=500, detail="邮件服务未初始化")
    
    return email_service.test_connection()


@app.post("/api/email/send-test/{user_id}")
async def send_test_email(user_id: str):
    if not (email_service and retrieval):
        raise HTTPException(status_code=500, detail="必要服务未初始化")

    subscriber = email_service.subscribers.get(user_id)
    if not subscriber:
        raise HTTPException(status_code=400, detail="用户未订阅")

    sample_papers = retrieval.search(query="machine learning deep learning research", n_results=3)
    
    result = email_service.send_paper_recommendations(
        to_user_id=user_id,
        papers=sample_papers,
        subject="[测试] 智能学术助手 - 测试邮件",
        custom_message="这是一封测试邮件，验证邮件发送功能是否正常工作。"
    )
    
    return result


# ========== 调度器端点 ==========

@app.get("/api/scheduler/status")
async def get_scheduler_status():
    if not task_scheduler:
        raise HTTPException(status_code=500, detail="调度器未初始化")
    
    status = task_scheduler.get_status()
    return {"success": True, **status}


@app.post("/api/scheduler/start")
async def start_scheduler():
    if not task_scheduler:
        raise HTTPException(status_code=500, detail="调度器未初始化")
    return task_scheduler.start()


@app.post("/api/scheduler/stop")
async def stop_scheduler():
    if not task_scheduler:
        raise HTTPException(status_code=500, detail="调度器未初始化")
    return task_scheduler.stop()


@app.post("/api/scheduler/run-papers-now")
async def run_papers_now():
    if not task_scheduler:
        raise HTTPException(status_code=500, detail="调度器未初始化")
    result = await task_scheduler.run_paper_recommendation_now()
    return result


@app.post("/api/scheduler/run-survey-now")
async def run_survey_now():
    if not task_scheduler:
        raise HTTPException(status_code=500, detail="调度器未初始化")
    result = await task_scheduler.run_survey_report_now()
    return result


@app.put("/api/scheduler/configure")
async def configure_scheduler(
    paper_hours: int = Query(168),
    survey_hours: int = Query(720)
):
    if not task_scheduler:
        raise HTTPException(status_code=500, detail="调度器未初始化")
    
    result = task_scheduler.update_intervals(paper_hours, survey_hours)
    return result


# ========== 系统信息端点 ==========

@app.get("/api/system/stats")
async def get_system_stats():
    stats = {}
    
    if user_manager:
        stats["users"] = user_manager.get_statistics()
    
    if email_service:
        stats["email"] = email_service.get_statistics()
    
    if task_scheduler:
        scheduler_status = task_scheduler.get_status()
        stats["scheduler"] = {
            "is_running": scheduler_status["is_running"],
            "configured_tasks": scheduler_status["configured_tasks"],
            "last_executions": scheduler_status["last_executions"]
        }

    return {"success": True, "timestamp": datetime.now().isoformat(), **stats}


if __name__ == "__main__":
    from datetime import datetime
    import uvicorn

    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))

    print(f"\n{'='*60}")
    print(f"🎓 智能学术助手 v4.0")
    print(f"   基于邮箱验证的AI学术聊天系统")
    print(f"{'='*60}")
    print(f"Starting on {host}:{port}\n")

    uvicorn.run(app, host=host, port=port)
