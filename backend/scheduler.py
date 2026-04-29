import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import os
from dotenv import load_dotenv

load_dotenv()


class RecommendationScheduler:
    def __init__(
        self,
        retrieval=None,
        reranker=None,
        conversation_manager=None,
        email_service=None,
        personalized_recommender=None
    ):
        self.scheduler = AsyncIOScheduler()
        self.retrieval = retrieval
        self.reranker = reranker
        self.conversation_manager = conversation_manager
        self.email_service = email_service
        self.personalized_recommender = personalized_recommender

        self.is_running = False
        self.last_run_time = None
        self.run_count = 0
        self.run_history = []

        self._setup_jobs()

    def _setup_jobs(self):
        interval_hours = int(os.getenv("SCHEDULER_INTERVAL_HOURS", "24"))
        interval_minutes = int(os.getenv("SCHEDULER_INTERVAL_MINUTES", "0"))

        if interval_hours > 0 or interval_minutes > 0:
            self.scheduler.add_job(
                self._run_scheduled_recommendation,
                trigger=IntervalTrigger(hours=interval_hours, minutes=interval_minutes),
                id='recommendation_job',
                name='定时论文推荐任务',
                replace_existing=True
            )
            print(f"[Scheduler] 定时任务已配置: 每 {interval_hours}小时 {interval_minutes}分钟 执行一次")

    async def _run_scheduled_recommendation(self):
        print(f"\n{'='*60}")
        print(f"📅 [Scheduler] 开始执行定时推荐任务")
        print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        try:

            active_subscribers = []
            if self.email_service:
                active_subscribers = self.email_service.get_subscribers(active_only=True)

            if not active_subscribers:
                print("[Scheduler] 没有活跃的订阅者，跳过本次推荐")

                result = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "skipped",
                    "reason": "No active subscribers",
                    "subscribers_count": 0
                }
                self._record_run(result)
                return result

            query = await self._generate_recommendation_query()

            if not query or not self.retrieval:
                print("[Scheduler] 无法生成查询或检索服务未初始化")
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "failed",
                    "error": "Cannot generate query or retrieval service not ready"
                }
                self._record_run(result)
                return result

            print(f"[Scheduler] 使用查询: {query}")

            papers = self.retrieval.search(query=query, n_results=15)

            if self.reranker and len(papers) > 1:
                papers = self.rererank(query=query, candidates=papers, top_k=10)

            if not papers:
                print("[Scheduler] 未找到相关论文")
                result = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "no_results",
                    "query": query,
                    "papers_count": 0
                }
                self._record_run(result)
                return result

            print(f"[Scheduler] 找到 {len(papers)} 篇论文")

            custom_message = (
                "根据您的研究兴趣和最近的学术动态，"
                f"我们为您精选了以下 {len(papers)} 篇高质量论文。\n\n"
                "这些论文涵盖了您关注的研究领域最新进展。"
            )

            email_result = None
            if self.email_service and active_subscribers:
                print(f"[Scheduler] 发送邮件给 {len(active_subscribers)} 位订阅者...")
                email_result = self.email_service.send_bulk_recommendations(
                    papers=papers,
                    subject=f"📚 学术论文每日推荐 - {datetime.now().strftime('%Y/%m/%d')}",
                    custom_message=custom_message
                )

            result = {
                "timestamp": datetime.now().isoformat(),
                "status": "success",
                "query": query,
                "papers_count": len(papers),
                "subscribers_count": len(active_subscribers),
                "email_result": email_result
            }

            self._record_run(result)
            self.run_count += 1

            print(f"\n✅ [Scheduler] 推荐任务完成!")
            print(f"   论文数: {len(papers)}")
            if email_result:
                print(f"   邮件发送: 成功 {email_result.get('successful', 0)}/{email_result.get('total_subscribers', 0)}")

            return result

        except Exception as e:
            error_result = {
                "timestamp": datetime.now().isoformat(),
                "status": "error",
                "error": str(e)
            }
            self._record_run(error_result)
            print(f"❌ [Scheduler] 任务执行失败: {e}")
            return error_result

    async def _generate_recommendation_query(self) -> Optional[str]:
        if self.personalized_recommender and self.conversation_manager:
            user_interests = self.conversation_manager.get_user_interests()

            if user_interests:
                conversation_history = [
                    {"role": "user", "content": msg}
                    for msg in user_interests[-20:]
                ]

                interests_analysis = self.personalized_recommender.analyze_user_interests(conversation_history)
                suggested_query = interests_analysis.get("query_suggestion", "")

                if suggested_query:
                    return suggested_query

        default_queries = [
            "machine learning deep learning latest advances",
            "artificial intelligence research breakthroughs",
            "neural networks natural language processing computer vision"
        ]

        import random
        return random.choice(default_queries)

    def _record_run(self, result: Dict):
        self.last_run_time = datetime.now().isoformat()
        self.run_history.append(result)

        if len(self.run_history) > 100:
            self.run_history = self.run_history[-100:]

    def start(self):
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            print("✅ [Scheduler] 调度器已启动")
            return {"success": True, "message": "调度器已启动"}
        return {"success": False, "message": "调度器已在运行中"}

    def stop(self):
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            print("⏹️ [Scheduler] 调度器已停止")
            return {"success": True, "message": "调度器已停止"}
        return {"success": False, "message": "调度器未在运行"}

    def get_status(self) -> Dict[str, Any]:
        jobs_info = []
        for job in self.scheduler.get_jobs():
            try:
                next_run = str(job.next_run_time) if hasattr(job, 'next_run_time') and job.next_run_time else None
            except:
                next_run = None

            jobs_info.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": next_run,
                "trigger": str(job.trigger)
            })

        return {
            "is_running": self.is_running,
            "last_run_time": self.last_run_time,
            "run_count": self.run_count,
            "jobs": jobs_info,
            "recent_runs": self.run_history[-5:] if self.run_history else []
        }

    async def run_now(self) -> Dict[str, Any]:
        print("[Scheduler] 手动触发推荐任务...")
        result = await self._run_scheduled_recommendation()
        return result

    def update_interval(self, hours: int = 24, minutes: int = 0):
        try:
            job = self.scheduler.get_job('recommendation_job')
            if job:
                job.reschedule(trigger=IntervalTrigger(hours=hours, minutes=minutes))
                print(f"[Scheduler] 时间间隔已更新为: {hours}小时 {minutes}分钟")
                return {
                    "success": True,
                    "message": f"时间间隔已更新为 {hours}小时 {minutes}分钟"
                }
            else:
                return {"success": False, "message": "未找到推荐任务"}
        except Exception as e:
            return {"success": False, "error": str(e)}
