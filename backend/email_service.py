"""
智能学术助手 v4.0 - 增强版邮件通知服务
功能：
1. QQ邮箱SMTP集成（SSL加密）
2. 论文推荐邮件模板
3. 综述报告邮件模板
4. 用户订阅管理
5. 发送日志与统计
"""

import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, formataddr
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import os

load_dotenv()


class EnhancedEmailService:
    """
    增强版学术邮件服务
    - 精美的HTML邮件模板
    - 论文推荐/综述报告双模式
    - 完整的发送追踪
    """

    def __init__(self):
        self.smtp_server = os.getenv("EMAIL_SMTP_SERVER", "smtp.qq.com")
        self.smtp_port = int(os.getenv("EMAIL_SMTP_PORT", "465"))
        self.sender_email = os.getenv("EMAIL_SENDER_ADDRESS", "")
        self.sender_password = os.getenv("EMAIL_SENDER_PASSWORD", "")
        self.sender_name = os.getenv("EMAIL_SENDER_NAME", "智能学术助手")
        self.use_ssl = os.getenv("EMAIL_USE_SSL", "true").lower() == "true"

        # 数据存储
        self.storage_path = Path("./secure_data/email_service")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.subscribers_file = self.storage_path / "subscribers.json"
        self.logs_dir = self.storage_path / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self._load_subscribers()

    def _load_subscribers(self):
        """加载订阅者数据"""
        if self.subscribers_file.exists():
            try:
                with open(self.subscribers_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.subscribers = json.loads(content) if content.strip() else {}
            except Exception as e:
                print(f"[Email] Error loading subscribers: {e}")
                self.subscribers = {}
        else:
            self.subscribers = {}

    def _save_subscribers(self):
        """安全保存订阅者数据"""
        try:
            with open(self.subscribers_file, 'w', encoding='utf-8') as f:
                json.dump(self.subscribers, f, ensure_ascii=False, indent=2)
            # 设置文件权限
            try:
                import os
                os.chmod(self.subscribers_file, 0o600)
            except:
                pass
        except Exception as e:
            print(f"[Email] Error saving subscribers: {e}")

    def is_configured(self) -> bool:
        """检查邮箱是否已配置"""
        return bool(self.sender_email and self.sender_password)

    def test_connection(self) -> Dict[str, Any]:
        """测试SMTP连接"""
        if not self.is_configured():
            return {
                "success": False,
                "error": "邮箱未配置。请在.env文件中设置 EMAIL_SENDER_ADDRESS 和 EMAIL_SENDER_PASSWORD"
            }

        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10)
                server.starttls()

            server.login(self.sender_email, self.sender_password)
            server.quit()

            return {
                "success": True,
                "message": "✅ SMTP连接测试成功",
                "smtp_server": self.smtp_server,
                "sender": self._mask_email(self.sender_email),
                "encryption": "SSL/TLS" if self.use_ssl else "STARTTLS"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"❌ 连接失败: {str(e)}"
            }

    def register_subscriber(
        self,
        user_id: str,
        email: str,
        preferences: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        注册订阅用户
        """
        # 验证邮箱格式
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email.strip()):
            return {"success": False, "error": "无效的邮箱地址格式"}

        email_normalized = email.lower().strip()

        # 检查是否已注册
        existing = self.subscribers.get(user_id)
        if existing and existing.get("email") == email_normalized and existing.get("is_active"):
            return {"success": False, "error": "该邮箱已订阅"}

        subscriber_data = {
            "user_id": user_id,
            "email": email_normalized,
            "registered_at": datetime.now().isoformat(),
            "is_active": True,
            "preferences": preferences or {
                "paper_recommendations": True,
                "report_generation": True,
                "frequency": "weekly",
                "max_papers_per_email": 10,
                "include_abstracts": True
            },
            "stats": {
                "papers_sent": 0,
                "reports_sent": 0,
                "total_emails": 0,
                "last_sent_at": None,
                "last_paper_sent_at": None,
                "last_report_sent_at": None
            }
        }

        self.subscribers[user_id] = subscriber_data
        self._save_subscribers()

        print(f"[Email] ✅ New subscriber: {self._mask_email(email_normalized)}")
        return {
            "success": True,
            "message": "订阅成功！您将定期收到个性化论文推荐和综述报告",
            "email_masked": self._mask_email(email_normalized)
        }

    def unregister_subscriber(self, user_id: str) -> Dict[str, Any]:
        """取消订阅"""
        if user_id in self.subscribers:
            self.subscribers[user_id]["is_active"] = False
            self.subscribers[user_id]["unsubscribed_at"] = datetime.now().isoformat()
            self._save_subscribers()

            return {"success": True, "message": "已取消订阅"}
        return {"success": False, "error": "未找到订阅记录"}

    def get_active_subscribers(self) -> List[Dict]:
        """获取所有活跃订阅者"""
        return [
            sub for sub in self.subscribers.values()
            if sub.get("is_active", False)
        ]

    def update_preferences(
        self,
        user_id: str,
        preferences: Dict[str, Any]
    ) -> Dict[str, Any]:
        """更新订阅偏好"""
        if user_id not in self.subscribers:
            return {"success": False, "error": "用户未订阅"}

        self.subscribers[user_id]["preferences"].update(preferences)
        self._save_subscribers()

        return {
            "success": True,
            "message": "偏好设置已更新",
            "preferences": self.subscribers[user_id]["preferences"]
        }

    def send_paper_recommendations(
        self,
        to_user_id: str,
        papers: List[Dict],
        subject: str = None,
        custom_message: str = None,
        user_profile: Dict = None
    ) -> Dict[str, Any]:
        """
        发送论文推荐邮件
        
        参数：
        - to_user_id: 接收者用户ID
        - papers: 论文列表 [{"metadata": {...}, "rank": int, ...}]
        - subject: 邮件主题（可选）
        - custom_message: 自定义消息（可选）
        - user_profile: 用户画像（用于个性化）
        """
        subscriber = self.subscribers.get(to_user_id)
        if not subscriber or not subscriber.get("is_active"):
            return {"success": False, "error": "用户未订阅或已停用"}

        to_email = subscriber["email"]

        if not self.is_configured():
            return {"success": False, "error": "邮件服务未配置"}

        try:
            # 生成邮件主题
            if not subject:
                domain = "学术论文"
                if user_profile and user_profile.get("primary_domain"):
                    domain = user_profile["primary_domain"]["domain_name"]
                subject = f"📚 为您精选的{domain}论文推荐 - {datetime.now().strftime('%Y年%m月%d日')}"

            # 构建HTML内容
            html_content = self._build_paper_recommendation_html(
                papers=papers[:subscriber["preferences"].get("max_papers_per_email", 10)],
                custom_message=custom_message or self._get_default_paper_message(user_profile),
                user_profile=user_profile
            )

            # 发送邮件
            result = self._send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content
            )

            if result["success"]:
                # 更新统计
                stats = subscriber.get("stats", {})
                stats["papers_sent"] = stats.get("papers_sent", 0) + 1
                stats["total_emails"] = stats.get("total_emails", 0) + 1
                stats["last_sent_at"] = datetime.now().isoformat()
                stats["last_paper_sent_at"] = datetime.now().isoformat()
                subscriber["stats"] = stats
                self._save_subscribers()

                # 记录发送日志
                self._log_send(to_user_id, to_email, "paper_recommendation", len(papers))

            return result

        except Exception as e:
            error_msg = f"发送失败: {str(e)}"
            self._log_error(to_user_id, "paper_recommendation", str(e))
            return {"success": False, "error": error_msg}

    def send_survey_report(
        self,
        to_user_id: str,
        report_topic: str,
        report_content: str,
        referenced_papers: List[Dict] = None,
        subject: str = None
    ) -> Dict[str, Any]:
        """
        发送综述报告邮件
        """
        subscriber = self.subscribers.get(to_user_id)
        if not subscriber or not subscriber.get("is_active"):
            return {"success": False, "error": "用户未订阅或已停用"}

        to_email = subscriber["email"]

        if not self.is_configured():
            return {"success": False, "error": "邮件服务未配置"}

        try:
            if not subject:
                subject = f"📋 学术综述报告：{report_topic} - {datetime.now().strftime('%Y年%m月%d日')}"

            html_content = self._build_survey_report_html(
                topic=report_topic,
                report_content=report_content,
                papers=referenced_papers or []
            )

            result = self._send_email(
                to_email=to_email,
                subject=subject,
                html_content=html_content
            )

            if result["success"]:
                stats = subscriber.get("stats", {})
                stats["reports_sent"] = stats.get("reports_sent", 0) + 1
                stats["total_emails"] = stats.get("total_emails", 0) + 1
                stats["last_sent_at"] = datetime.now().isoformat()
                stats["last_report_sent_at"] = datetime.now().isoformat()
                subscriber["stats"] = stats
                self._save_subscribers()

                self._log_send(to_user_id, to_email, "survey_report", len(referenced_papers or []))

            return result

        except Exception as e:
            self._log_error(to_user_id, "survey_report", str(e))
            return {"success": False, "error": f"发送失败: {str(e)}"}

    def get_statistics(self) -> Dict[str, Any]:
        """获取邮件服务统计信息"""
        total_subs = len(self.subscribers)
        active_subs = sum(1 for s in self.subscribers.values() if s.get("is_active"))

        total_papers_sent = sum(s.get("stats", {}).get("papers_sent", 0) for s in self.subscribers.values())
        total_reports_sent = sum(s.get("stats", {}).get("reports_sent", 0) for s in self.subscribers.values())
        total_emails = sum(s.get("stats", {}).get("total_emails", 0) for s in self.subscribers.values())

        return {
            "total_subscribers": total_subs,
            "active_subscribers": active_subs,
            "total_papers_sent": total_papers_sent,
            "total_reports_sent": total_reports_sent,
            "total_emails_sent": total_emails,
            "sender_configured": self.is_configured(),
            "sender_display": self._mask_email(self.sender_email) if self.sender_email else "未配置",
            "smtp_server": self.smtp_server
        }

    # ========== HTML模板构建方法 ==========

    def _build_paper_recommendation_html(
        self,
        papers: List[Dict],
        custom_message: str,
        user_profile: Dict = None
    ) -> str:
        """构建论文推荐邮件HTML"""

        # 论文卡片列表
        papers_html = ""
        for idx, paper in enumerate(papers[:10], 1):
            metadata = paper.get("metadata", {})
            title = metadata.get("title", "无标题")
            authors = metadata.get("authors", "未知作者")
            summary = metadata.get("summary", "暂无摘要")
            paper_id = metadata.get("paper_id", "")
            arxiv_url = f"https://arxiv.org/abs/{paper_id}" if paper_id else "#"

            rank = paper.get("rank", idx)
            rationale = paper.get("recommendation_rationale", "智能匹配推荐")
            relevance = paper.get("relevance_to_user", 85)

            # 相关度颜色
            if relevance >= 80:
                color_class = "text-green-600 bg-green-50"
                label = "高度相关"
            elif relevance >= 60:
                color_class = "text-blue-600 bg-blue-50"
                label = "相关"
            else:
                color_class = "text-orange-600 bg-orange-50"
                label = "可能相关"

            papers_html += f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-left: 4px solid #6366f1; border-radius: 12px; padding: 20px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07);">
                <div style="display: flex; align-items: start; gap: 16px;">
                    <div style="flex-shrink: 0; width: 40px; height: 40px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white;">#{rank}</div>
                    <div style="flex: 1; min-width: 0;">
                        <h3 style="margin: 0 0 8px 0; font-size: 16px; font-weight: 700; color: #1e293b; line-height: 1.4;">{title}</h3>
                        <p style="margin: 0 0 8px 0; font-size: 13px; color: #64748b;"><strong>👤 作者：</strong>{authors}</p>
                        <p style="margin: 0 0 12px 0; font-size: 14px; color: #475569; line-height: 1.6;">📝 {summary[:280]}{'...' if len(summary) > 280 else ''}</p>
                        
                        <div style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap; margin-top: 12px;">
                            <span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 12px; background: #f1f5f9; border-radius: 20px; font-size: 12px; color: #475569;">
                                💡 {rationale}
                            </span>
                            <span style="display: inline-flex; align-items: center; gap: 4px; padding: 4px 12px; background: {'#dcfce7' if relevance >= 80 else '#dbeafe' if relevance >= 60 else '#fed7aa'}; border-radius: 20px; font-size: 12px; font-weight: 600; {'color: #16a34a' if relevance >= 80 else '#2563eb' if relevance >= 60 else '#ea580c'};">
                                🎯 {label} ({relevance}%)
                            </span>
                        </div>

                        <a href="{arxiv_url}" target="_blank" style="display: inline-block; margin-top: 14px; padding: 10px 24px; background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px; box-shadow: 0 4px 12px rgba(99,102,241,0.25);">
                            🔗 查看论文详情 →
                        </a>
                    </div>
                </div>
            </div>
            """

        # 完整HTML
        html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f1f5f9; margin: 0; padding: 20px; }}
.container {{ max-width: 720px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15); }}
.header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; color: white; }}
.content {{ padding: 30px; }}
.footer {{ background: #f8fafc; padding: 24px; text-align: center; color: #94a3b8; font-size: 13px; border-top: 1px solid #e2e8f0; }}
</style></head><body>
<div class="container">
    <div class="header">
        <h1 style="margin: 0; font-size: 28px; font-weight: 800;">📚 学术论文智能推荐</h1>
        <p style="margin: 12px 0 0 0; opacity: 0.95; font-size: 15px;">为您精心挑选的最新研究成果 · {datetime.now().strftime('%Y年%m月%d')}</p>
    </div>
    
    <div class="content">
        <div style="background: linear-gradient(135deg, #ede9fe 0%, #ddd6fe 100%); padding: 24px; border-radius: 16px; margin-bottom: 28px; border: 1px solid #c4b5fd;">
            <p style="margin: 0; color: #5b21b6; font-size: 15px; line-height: 1.7; font-weight: 500;">
                ✨ {custom_message}
            </p>
        </div>

        <h2 style="font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 20px; display: flex; align-items: center; gap: 8px;">
            📖 推荐论文清单 (共{len(papers)}篇)
        </h2>

        {papers_html}

        <div style="background: #fef3c7; padding: 20px; border-radius: 12px; margin-top: 28px; border: 1px solid #fcd34d;">
            <p style="margin: 0; color: #92400e; font-size: 14px; line-height: 1.7;">
                💡 <strong>温馨提示：</strong>这些推荐完全基于您的研究兴趣和对话历史生成。<br>
                如需调整推荐方向或频率，请在系统中更新您的偏好设置。
            </p>
        </div>
    </div>

    <div class="footer">
        <p style="margin: 0 0 8px 0;">此邮件由「智能学术助手」自动发送</p>
        <p style="margin: 0;">如需退订，请访问系统设置页面</p>
        <p style="margin: 12px 0 0 0; font-size: 11px; opacity: 0.7;">© {datetime.now().year} Academic Intelligence Assistant</p>
    </div>
</div></body></html>"""

        return html

    def _build_survey_report_html(
        self,
        topic: str,
        report_content: str,
        papers: List[Dict]
    ) -> str:
        """构建综述报告邮件HTML"""

        # 将Markdown转换为简单HTML
        formatted_report = self._markdown_to_html(report_content)

        # 参考文献列表
        refs_html = ""
        if papers:
            refs_html = "<h3 style='color: #1e293b; margin-top: 32px;'>📚 参考文献</h3>"
            for i, paper in enumerate(papers[:8], 1):
                metadata = paper.get("metadata", {})
                refs_html += f"<p style='margin: 8px 0; padding-left: 20px; color: #475569;'><strong>[{i}]</strong> {metadata.get('title', '')}</p>"

        html = f"""<!DOCTYPE html><html><head><meta charset="UTF-8"><style>
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Georgia, serif; background: #fafaf9; margin: 0; padding: 20px; line-height: 1.8; }}
.container {{ max-width: 800px; margin: 0 auto; background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0,0,0,0.15); }}
.header {{ background: linear-gradient(135deg, #059669 0%, #0d9488 100%); padding: 45px 35px; text-align: center; color: white; }}
.content {{ padding: 40px 35px; color: #334155; font-size: 15px; }}
.content h1 {{ color: #065f46; font-size: 26px; margin-bottom: 24px; }}
.content h2 {{ color: #047857; font-size: 20px; margin-top: 32px; margin-bottom: 16px; border-bottom: 2px solid #d1fae5; padding-bottom: 8px; }}
.content h3 {{ color: #065f46; font-size: 17px; margin-top: 24px; }}
.content p {{ margin: 12px 0; }}
.footer {{ background: #f0fdf4; padding: 28px; text-align: center; color: #6b7280; font-size: 13px; border-top: 1px solid #bbf7d0; }}
</style></head><body>
<div class="container">
    <div class="header">
        <h1 style="margin: 0; font-size: 30px; font-weight: 800;">📋 学术综述报告</h1>
        <p style="margin: 14px 0 0 0; font-size: 17px; opacity: 0.95;">{topic}</p>
        <p style="margin: 10px 0 0 0; font-size: 14px; opacity: 0.85;">生成时间：{datetime.now().strftime('%Y年%m月%d日 %H:%M')}</p>
    </div>
    
    <div class="content">
        {formatted_report}
        {refs_html}
    </div>

    <div class="footer">
        <p style="margin: 0 0 8px 0;">本报告由「智能学术助手」基于您的对话历史自动生成</p>
        <p style="margin: 0;">报告内容仅供参考，请以原文为准</p>
        <p style="margin: 14px 0 0 0; font-size: 11px; opacity: 0.7;">© {datetime.now().year} Academic Intelligence Assistant</p>
    </div>
</div></body></html>"""

        return html

    # ========== 私有辅助方法 ==========

    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> Dict[str, Any]:
        """执行实际的邮件发送"""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = formataddr((self.sender_name, self.sender_email))
        msg['To'] = to_email
        msg['Date'] = formatdate(localtime=True)

        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)

        try:
            if self.use_ssl:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
            else:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                server.starttls()

            server.login(self.sender_email, self.sender_password)
            server.sendmail(self.sender_email, [to_email], msg.as_string())
            server.quit()

            return {
                "success": True,
                "message": f"✅ 邮件已发送至 {self._mask_email(to_email)}"
            }

        except Exception as e:
            raise Exception(f"SMTP错误: {str(e)}")

    def _get_default_paper_message(self, profile: Dict = None) -> str:
        """生成默认的推荐消息"""
        if profile and profile.get("primary_domain"):
            domain = profile["primary_domain"]["domain_name"]
            interests = ", ".join([i["keyword"] for i in profile.get("primary_interests", [])[:3]])
            return (
                f"根据您对<strong>{domain}</strong>领域的关注，以及近期讨论的"
                f"<strong>{interests}</strong>等话题，我们为您筛选了以下高质量论文。"
                f"这些工作代表了该方向的最新研究进展。"
            )
        
        return (
            "基于您的学术研究兴趣和最近的对话交流，"
            "我们运用AI算法为您精选了以下论文。"
            "希望这些资料能为您的研究提供有价值的参考！"
        )

    def _markdown_to_html(self, text: str) -> str:
        """简单的Markdown转HTML"""
        import re
        
        # 标题转换
        text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
        text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
        
        # 粗体和斜体
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        
        # 列表
        text = re.sub(r'^- (.+)$', r'<li>\1</li>', text, flags=re.MULTILINE)
        text = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', text)
        
        # 段落
        paragraphs = text.split('\n\n')
        text = '\n'.join([f'<p>{p}</p>' if not p.startswith('<') else p for p in paragraphs])
        
        return text

    @staticmethod
    def _mask_email(email: str) -> str:
        """遮蔽邮箱显示"""
        if '@' not in email:
            return email
        local, domain = email.split('@')
        masked = local[0] + '*' * (len(local) - 2) + local[-1] if len(local) > 2 else '***'
        return f"{masked}@{domain}"

    def _log_send(self, user_id: str, email: str, email_type: str, count: int):
        """记录成功发送"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "to_email": self._mask_email(email),
            "type": email_type,
            "count": count,
            "status": "success"
        }
        self._write_log(log_entry)

    def _log_error(self, user_id: str, email_type: str, error: str):
        """记录发送错误"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "type": email_type,
            "status": "failed",
            "error": error
        }
        self._write_log(log_entry)

    def _write_log(self, entry: Dict):
        """写入日志文件"""
        try:
            date_str = datetime.now().strftime("%Y-%m-%d")
            log_file = self.logs_dir / f"{date_str}.json"

            logs = []
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)

            logs.append(entry)

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Email Log] Error writing log: {e}")
