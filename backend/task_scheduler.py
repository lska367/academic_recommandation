"""
智能学术助手 v4.0 - 智能定时任务调度器
功能：
1. 定期论文推荐推送（可配置间隔）
2. 定期综述报告生成与发送
3. 用户画像自动更新
4. 任务执行日志
"""

import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import os

load_dotenv()


class IntelligentTaskScheduler:
    """
    智能定时任务调度器
    
    功能：
    - 论文推荐定时推送
    - 综述报告自动生成
    - 用户兴趣追踪
    """

    def __init__(
        self,
        user_manager=None,
        intelligence_engine=None,
        email_service=None,
        retrieval=None,
        reranker=None,
        report_generator=None
    ):
        self.scheduler = AsyncIOScheduler()
        
        # 核心服务引用
        self.user_manager = user_manager
        self.intelligence_engine = intelligence_engine
        self.email_service = email_service
        self.retrieval = retrieval
        self.reranker = reranker
        self.report_generator = report_generator

        # 运行状态跟踪
        self.is_running = False
        self.execution_history = []
        self.last_executions = {
            "paper_recommendation": None,
            "survey_report": None
        }

        # 配置参数
        self.paper_rec_interval_hours = int(os.getenv("PAPER_REC_INTERVAL_HOURS", "168"))  # 默认每周
        self.survey_interval_hours = int(os.getenv("SURVEY_INTERVAL_HOURS", "720"))  # 默认每月(30天)

        # 初始化任务
        self._setup_tasks()

    def _setup_tasks(self):
        """配置所有定时任务"""

        # 1. 论文推荐推送任务
        if self.paper_rec_interval_hours > 0:
            self.scheduler.add_job(
                self._execute_paper_recommendation_task,
                trigger=IntervalTrigger(hours=self.paper_rec_interval_hours),
                id='paper_recommendation',
                name='论文推荐定时推送',
                replace_existing=True
            )
            print(f"[Scheduler] ✅ 论文推荐任务: 每{self.paper_rec_interval_hours}小时")

        # 2. 综述报告生成任务
        if self.survey_interval_hours > 0:
            self.scheduler.add_job(
                self._execute_survey_report_task,
                trigger=IntervalTrigger(hours=self.survey_interval_hours),
                id='survey_report',
                name='综述报告定时生成',
                replace_existing=True
            )
            print(f"[Scheduler] ✅ 综述报告任务: 每{self.survey_interval_hours}小时")

    async def _execute_paper_recommendation_task(self):
        """
        执行论文推荐推送任务
        
        流程：
        1. 获取所有活跃订阅用户
        2. 对每个用户：
           a) 获取对话历史并构建画像
           b) 生成个性化论文推荐
           c) 发送推荐邮件
        """
        task_start = datetime.now()
        print(f"\n{'='*60}")
        print(f"📚 [Scheduler] 开始执行论文推荐推送任务")
        print(f"   时间: {task_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        result = {
            "timestamp": task_start.isoformat(),
            "task_type": "paper_recommendation",
            "status": "running",
            "processed_users": 0,
            "successful_sends": 0,
            "failed_sends": 0,
            "errors": []
        }

        try:
            if not self.email_service or not self.intelligence_engine or not self.user_manager:
                result["status"] = "error"
                result["errors"].append("必要服务未初始化")
                self._record_execution(result)
                return result

            # 获取活跃订阅者
            active_subscribers = self.email_service.get_active_subscribers()
            
            if not active_subscribers:
                result["status"] = "skipped"
                result["message"] = "没有活跃的订阅者"
                self._record_execution(result)
                return result

            print(f"[Scheduler] 找到 {len(active_subscribers)} 位活跃订阅者\n")

            for subscriber in active_subscribers:
                user_id = subscriber.get("user_id")
                
                try:
                    print(f"\n[Scheduler] 处理用户: {user_id[:8]}...")
                    
                    # Step 1: 获取用户对话历史
                    user_messages = self.user_manager.get_all_user_messages_for_analysis(
                        user_id, 
                        limit_per_conv=10, 
                        max_conversations=20
                    )
                    
                    if not user_messages:
                        print(f"   ⏭️ 用户无对话历史，跳过")
                        continue

                    conversation_history = [
                        {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                        for msg in user_messages
                    ]

                    # Step 2: 构建用户画像
                    user_profile = self.intelligence_engine.build_user_profile(conversation_history)
                    
                    if not user_profile.get("recommendation_readiness"):
                        print(f"   ⏭️ 用户画像不成熟，暂不发送")
                        continue

                    # Step 3: 生成论文推荐
                    recommendations = self.intelligence_engine.generate_paper_recommendations(
                        user_profile=user_profile,
                        n_results=10,
                        use_rerank=True
                    )

                    if not recommendations.get("success"):
                        print(f"   ❌ 推荐生成失败: {recommendations.get('error')}")
                        result["failed_sends"] += 1
                        continue

                    papers = recommendations.get("results", [])
                    
                    if not papers:
                        print(f"   ⏭️ 未找到匹配论文")
                        continue

                    # Step 4: 发送邮件
                    send_result = self.email_service.send_paper_recommendations(
                        to_user_id=user_id,
                        papers=papers,
                        user_profile=user_profile
                    )

                    if send_result.get("success"):
                        print(f"   ✅ 邮件发送成功 ({len(papers)}篇论文)")
                        result["successful_sends"] += 1
                        
                        # 更新用户记录
                        self.user_manager.record_recommendation_sent(user_id, "papers")
                        
                        # 更新研究兴趣标签
                        interests = [item["keyword"] for item in user_profile.get("primary_interests", [])]
                        domains = [d["domain_name"] for d in user_profile.get("research_domains", [])]
                        all_tags = interests + domains
                        self.user_manager.update_research_interests(user_id, all_tags)
                    else:
                        print(f"   ❌ 邮件发送失败: {send_result.get('error')}")
                        result["failed_sends"] += 1

                    result["processed_users"] += 1

                except Exception as e:
                    error_msg = f"处理用户 {user_id[:8]} 失败: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    result["errors"].append(error_msg)
                    result["failed_sends"] += 1

            # 任务完成
            result["status"] = "completed"
            self.last_executions["paper_recommendation"] = datetime.now().isoformat()

            print(f"\n{'='*60}")
            print(f"✅ [Scheduler] 论文推荐任务完成!")
            print(f"   处理用户: {result['processed_users']}")
            print(f"   成功发送: {result['successful_sends']}")
            print(f"   发送失败: {result['failed_sends']}")
            print(f"{'='*60}\n")

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))
            print(f"❌ [Scheduler] 任务执行异常: {e}")

        finally:
            self._record_execution(result)

        return result

    async def _execute_survey_report_task(self):
        """
        执行综述报告生成任务
        
        流程：
        1. 选择有足够对话历史的用户
        2. 基于主要研究方向生成综述报告
        3. 发送报告邮件
        """
        task_start = datetime.now()
        print(f"\n{'='*60}")
        print(f"📋 [Scheduler] 开始执行综述报告生成任务")
        print(f"   时间: {task_start.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")

        result = {
            "timestamp": task_start.isoformat(),
            "task_type": "survey_report",
            "status": "running",
            "reports_generated": 0,
            "successful_sends": 0,
            "failed_sends": 0,
            "errors": []
        }

        try:
            if not (self.email_service and self.intelligence_engine and 
                self.user_manager and self.retrieval):
                result["status"] = "error"
                result["errors"].append("必要服务未初始化")
                self._record_execution(result)
                return result

            active_subscribers = self.email_service.get_active_subscribers()

            if not active_subscribers:
                result["status"] = "skipped"
                result["message"] = "没有活跃订阅者"
                self._record_execution(result)
                return result

            print(f"[Scheduler] 为 {len(active_subscribers)} 位用户生成综述报告\n")

            for subscriber in active_subscribers:
                user_id = subscriber.get("user_id")

                try:
                    print(f"\n[Scheduler] 为用户 {user_id[:8]} 生成报告...")

                    # 获取对话历史
                    user_messages = self.user_manager.get_all_user_messages_for_analysis(
                        user_id, limit_per_conv=15, max_conversations=25
                    )

                    if len(user_messages) < 5:
                        print(f"   ⏭️ 对话记录不足，跳过")
                        continue

                    conversation_history = [
                        {"role": msg.get("role", "user"), "content": msg.get("content", "")}
                        for msg in user_messages
                    ]

                    # 构建用户画像
                    user_profile = self.intelligence_engine.build_user_profile(conversation_history)

                    # 确定报告主题
                    primary_domain = user_profile.get("primary_domain")
                    if primary_domain:
                        report_topic = f"{primary_domain['domain_name']}研究进展综述"
                    else:
                        top_interests = user_profile.get("primary_interests", [])
                        if top_interests:
                            report_topic = f"{top_interests[0]['keyword']}相关研究综述"
                        else:
                            print(f"   ⏭️ 无法确定报告主题")
                            continue

                    print(f"   📝 报告主题: {report_topic}")

                    # 检索相关论文作为参考
                    query_parts = [
                        item["keyword"] for item in user_profile.get("primary_interests", [])[:5]
                    ]
                    if primary_domain:
                        query_parts.insert(0, primary_domain["domain_name"])
                    
                    search_query = " ".join(query_parts[:4])
                    referenced_papers = self.retrieval.search(query=search_query, n_results=8)

                    if self.reranker and len(referenced_papers) > 1:
                        referenced_papers = self.reranker.rerank(
                            query=search_query,
                            candidates=referenced_papers,
                            top_k=min(6, len(referenced_papers))
                        )

                    # 生成报告内容
                    report_content = self.intelligence_engine.generate_survey_report_content(
                        topic=report_topic,
                        papers=referenced_papers,
                        user_context=user_profile
                    )

                    if not report_content or "失败" in report_content:
                        print(f"   ❌ 报告生成失败")
                        result["failed_sends"] += 1
                        continue

                    # 发送报告邮件
                    send_result = self.email_service.send_survey_report(
                        to_user_id=user_id,
                        report_topic=report_topic,
                        report_content=report_content,
                        referenced_papers=referenced_papers
                    )

                    if send_result.get("success"):
                        print(f"   ✅ 报告发送成功")
                        result["reports_generated"] += 1
                        result["successful_sends"] += 1
                        self.user_manager.record_recommendation_sent(user_id, "report")
                    else:
                        print(f"   ❌ 发送失败: {send_result.get('error')}")
                        result["failed_sends"] += 1

                except Exception as e:
                    error_msg = f"处理用户 {user_id[:8]} 失败: {str(e)}"
                    print(f"   ❌ {error_msg}")
                    result["errors"].append(error_msg)
                    result["failed_sends"] += 1

            result["status"] = "completed"
            self.last_executions["survey_report"] = datetime.now().isoformat()

            print(f"\n{'='*60}")
            print(f"✅ [Scheduler] 综述报告任务完成!")
            print(f"   生成报告: {result['reports_generated']}")
            print(f"   成功发送: {result['successful_sends']}")
            print(f"{'='*60}\n")

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))
            print(f"❌ [Scheduler] 任务异常: {e}")

        finally:
            self._record_execution(result)

        return result

    def start(self):
        """启动调度器"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            print("\n✅ [Scheduler] 智能调度器已启动")
            print(f"   运行的任务:")
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time.strftime('%Y-%m-%d %H:%M') if job.next_run_time else 'N/A'
                print(f"     • {job.name}: 下次执行 → {next_run}")
            return {"success": True, "message": "调度器已启动"}
        return {"success": False, "message": "已在运行中"}

    def stop(self):
        """停止调度器"""
        if self.is_running:
            self.scheduler.shutdown(wait=False)
            self.is_running = False
            print("⏹️ [Scheduler] 调度器已停止")
            return {"success": True, "message": "调度器已停止"}
        return {"success": False, "message": "未在运行"}

    async def run_paper_recommendation_now(self):
        """立即执行一次论文推荐任务"""
        print("[Scheduler] 手动触发论文推荐任务...")
        return await self._execute_paper_recommendation_task()

    async def run_survey_report_now(self):
        """立即执行一次综述报告任务"""
        print("[Scheduler] 手动触发综述报告任务...")
        return await self._execute_survey_report_task()

    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            try:
                next_run = job.next_run_time.isoformat() if job.next_run_time else None
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
            "configured_tasks": len(jobs_info),
            "jobs": jobs_info,
            "last_executions": self.last_executions,
            "recent_executions": self.execution_history[-5:] if self.execution_history else [],
            "configuration": {
                "paper_recommendation_interval_hours": self.paper_rec_interval_hours,
                "survey_report_interval_hours": self.survey_interval_hours
            }
        }

    def update_intervals(
        self, 
        paper_hours: int = None, 
        survey_hours: int = None
    ) -> Dict[str, Any]:
        """更新任务时间间隔"""
        results = []

        if paper_hours is not None and paper_hours > 0:
            try:
                job = self.scheduler.get_job('paper_recommendation')
                if job:
                    job.reschedule(trigger=IntervalTrigger(hours=paper_hours))
                    self.paper_rec_interval_hours = paper_hours
                    results.append({
                        "task": "paper_recommendation",
                        "new_interval": f"{paper_hours}小时",
                        "success": True
                    })
                    print(f"[Scheduler] 论文推荐间隔已更新为: 每{paper_hours}小时")
            except Exception as e:
                results.append({"task": "paper_recommendation", "error": str(e), "success": False})

        if survey_hours is not None and survey_hours > 0:
            try:
                job = self.scheduler.get_job('survey_report')
                if job:
                    job.reschedule(trigger=IntervalTrigger(hours=survey_hours))
                    self.survey_interval_hours = survey_hours
                    results.append({
                        "task": "survey_report",
                        "new_interval": f"{survey_hours}小时",
                        "success": True
                    })
                    print(f"[Scheduler] 综述报告间隔已更新为: 每{survey_hours}小时")
            except Exception as e:
                results.append({"task": "survey_report", "error": str(e), "success": False})

        return {"results": results}

    def _record_execution(self, execution_record: Dict):
        """记录任务执行结果"""
        self.execution_history.append(execution_record)
        
        # 只保留最近50条记录
        if len(self.execution_history) > 50:
            self.execution_history = self.execution_history[-50:]
