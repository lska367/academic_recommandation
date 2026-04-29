#!/usr/bin/env python3
"""
系统功能测试脚本 - 验证所有新增模块是否正常工作
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation_manager import ConversationManager
from personalized_recommender import PersonalizedRecommender
from email_service import EmailService
from scheduler import RecommendationScheduler


def test_conversation_manager():
    print("\n" + "="*60)
    print("📝 测试对话管理器 (ConversationManager)")
    print("="*60)

    manager = ConversationManager("./test_data/conversations")

    # Test 1: Create conversation
    print("\n✅ 测试1: 创建对话")
    conv_id = manager.create_conversation(user_id="test_user", title="测试对话")
    print(f"   对话ID: {conv_id}")
    assert conv_id, "创建对话失败"

    # Test 2: Add messages
    print("\n✅ 测试2: 添加消息")
    assert manager.add_message(conv_id, "user", "你好，我想了解深度学习"), "添加用户消息失败"
    assert manager.add_message(conv_id, "assistant", "你好！深度学习是机器学习的一个子领域..."), "添加助手消息失败"
    assert manager.add_message(conv_id, "user", "请推荐一些关于CNN的论文"), "添加第二条用户消息失败"
    print("   成功添加3条消息")

    # Test 3: Get conversation
    print("\n✅ 测试3: 获取对话详情")
    conv = manager.get_conversation(conv_id)
    assert conv is not None, "获取对话失败"
    assert len(conv["messages"]) == 3, f"消息数量不正确: {len(conv['messages'])}"
    print(f"   对话标题: {conv['title']}")
    print(f"   消息数量: {len(conv['messages'])}")

    # Test 4: Get all conversations
    print("\n✅ 测试4: 获取所有对话")
    conversations = manager.get_all_conversations(user_id="test_user")
    assert len(conversations) >= 1, "获取对话列表失败"
    print(f"   用户对话数: {len(conversations)}")

    # Test 5: Get recent messages
    print("\n✅ 测试5: 获取最近消息")
    recent_msgs = manager.get_recent_messages(conv_id, limit=2)
    assert len(recent_msgs) == 2, f"最近消息数量不正确: {len(recent_msgs)}"
    print(f"   最近{len(recent_msgs)}条消息已加载")

    # Test 6: Get user interests
    print("\n✅ 测试6: 获取用户兴趣")
    interests = manager.get_user_interests("test_user")
    assert len(interests) > 0, "获取用户兴趣失败"
    print(f"   用户兴趣消息数: {len(interests)}")

    # Test 7: Update title
    print("\n✅ 测试7: 更新对话标题")
    assert manager.update_title(conv_id, "更新后的标题"), "更新标题失败"
    updated_conv = manager.get_conversation(conv_id)
    assert updated_conv["title"] == "更新后的标题", "标题未正确更新"
    print(f"   新标题: {updated_conv['title']}")

    # Test 8: Statistics
    print("\n✅ 测试8: 获取统计信息")
    stats = manager.get_statistics()
    assert stats["total_conversations"] > 0, "统计信息错误"
    print(f"   总对话数: {stats['total_conversations']}")
    print(f"   总消息数: {stats['total_messages']}")

    # Test 9: Delete conversation
    print("\n✅ 测试9: 删除对话")
    assert manager.delete_conversation(conv_id), "删除对话失败"
    deleted_conv = manager.get_conversation(conv_id)
    assert deleted_conv is None, "对话未被删除"
    print("   对话删除成功")

    print("\n✨ 对话管理器所有测试通过！")
    return True


def test_personalized_recommender():
    print("\n" + "="*60)
    print("🎯 测试个性化推荐引擎 (PersonalizedRecommender)")
    print("="*60)

    recommender = PersonalizedRecommender()

    # Test conversation history
    conversation_history = [
        {"role": "user", "content": "我对深度学习和计算机视觉很感兴趣"},
        {"role": "assistant", "content": "好的，我可以为您推荐相关论文"},
        {"role": "user", "content": "特别是关于卷积神经网络和图像识别的最新研究"},
        {"role": "user", "content": "还有自然语言处理方面的进展"},
        {"role": "user", "content": "Transformer模型在NLP中的应用"},
    ]

    # Test 1: Extract keywords
    print("\n✅ 测试1: 关键词提取")
    text = "深度学习在计算机视觉和自然语言处理领域的应用"
    keywords = recommender.extract_keywords(text)
    assert len(keywords) > 0, "关键词提取失败"
    print(f"   提取的关键词: {keywords[:5]}...")

    # Test 2: Analyze user interests
    print("\n✅ 测试2: 分析用户兴趣")
    interests = recommender.analyze_user_interests(conversation_history)
    assert interests is not None, "分析用户兴趣失败"
    print(f"   主要兴趣 ({len(interests.get('primary_interests', []))}个):")
    for interest in interests.get('primary_interests', [])[:3]:
        print(f"      - {interest['keyword']} (频率: {interest['frequency']})")
    if interests.get('research_areas'):
        print(f"   研究领域: {interests['research_areas']}")
    if interests.get('query_suggestion'):
        print(f"   推荐查询: {interests['query_suggestion']}")

    # Test 3: Identify research areas
    print("\n✅ 测试3: 识别研究领域")
    test_text = "我正在研究深度学习在自然语言处理中的应用，特别是Transformer和BERT模型"
    areas = recommender._identify_research_areas(test_text)
    assert len(areas) > 0, "研究领域识别失败"
    print(f"   识别到的研究领域: {areas}")

    print("\n✨ 个性化推荐引擎所有测试通过！")
    return True


def test_email_service():
    print("\n" + "="*60)
    print("📧 测试邮件服务 (EmailService)")
    print("="*60)

    service = EmailService()

    # Test 1: Initialize service
    print("\n✅ 测试1: 服务初始化")
    assert service.smtp_server == "smtp.qq.com", "SMTP服务器配置错误"
    assert service.smtp_port == 465, "SMTP端口配置错误"
    print(f"   SMTP服务器: {service.smtp_server}:{service.smtp_port}")
    print(f"   发送邮箱: {service.sender_email[:3] if service.sender_email else 'Not'}***")

    # Test 2: Subscribe (without actual sending)
    print("\n✅ 测试2: 订阅功能")
    result = service.subscribe("test@example.com", {"frequency": "daily"})
    assert result["success"] == True, "订阅失败"
    print(f"   订阅结果: {result['message']}")

    # Test 3: Duplicate subscription check
    print("\n✅ 测试3: 重复订阅检查")
    result = service.subscribe("test@example.com")
    assert result["success"] == False, "应该拒绝重复订阅"
    print(f"   重复订阅处理正确: {result['error']}")

    # Test 4: Unsubscribe
    print("\n✅ 测试4: 取消订阅")
    result = service.unsubscribe("test@example.com")
    assert result["success"] == True, "取消订阅失败"
    print(f"   取消订阅结果: {result['message']}")

    # Test 5: Get subscribers
    print("\n✅ 测试5: 获取订阅者列表")
    service.subscribe("user1@test.com")
    service.subscribe("user2@test.com")
    subscribers = service.get_subscribers(active_only=True)
    assert len(subscribers) == 2, "获取订阅者列表失败"
    print(f"   活跃订阅者数量: {len(subscribers)}")

    # Test 6: Statistics
    print("\n✅ 测试6: 统计信息")
    stats = service.get_statistics()
    assert stats["total_subscribers"] >= 2, "统计信息错误"
    print(f"   总订阅者: {stats['total_subscribers']}")
    print(f"   活跃订阅者: {stats['active_subscribers']}")

    # Test 7: Email validation
    print("\n✅ 测试7: 邮箱格式验证")
    invalid_result = service.subscribe("invalid-email")
    assert invalid_result["success"] == False, "应该拒绝无效邮箱"
    print(f"   无效邮箱处理正确: {invalid_result['error']}")

    print("\n✨ 邮件服务所有测试通过！")
    return True


def test_scheduler():
    print("\n" + "="*60)
    print("⏰ 测试定时任务调度器 (RecommendationScheduler)")
    print("="*60)

    scheduler = RecommendationScheduler()

    # Test 1: Initial status
    print("\n✅ 测试1: 初始状态检查")
    status = scheduler.get_status()
    assert status is not None, "获取状态失败"
    assert status["is_running"] == False, "初始状态应该是停止的"
    print(f"   运行状态: {'运行中' if status['is_running'] else '已停止'}")
    print(f"   执行次数: {status['run_count']}")

    # Test 2: Update interval
    print("\n✅ 测试2: 更新时间间隔")
    result = scheduler.update_interval(hours=12, minutes=30)
    assert result["success"] == True, "更新间隔失败"
    print(f"   更新结果: {result['message']}")

    # Test 3: Job info
    print("\n✅ 测试3: 任务信息")
    status = scheduler.get_status()
    if status.get("jobs"):
        for job in status["jobs"]:
            print(f"   任务ID: {job['id']}")
            print(f"   任务名称: {job['name']}")
            next_run = job.get('next_run_time', 'N/A')
            print(f"   下次执行: {next_run}")

    print("\n⚠️  注意: 调度器实际启动需要连接后端服务")
    print("✨ 定时任务调度器基本测试通过！")
    return True


def main():
    print("\n" + "="*70)
    print("🚀 学术推荐系统 v2.0 - 功能测试套件")
    print("="*70)

    results = {}

    try:
        results['conversation_manager'] = test_conversation_manager()
    except Exception as e:
        print(f"\n❌ 对话管理器测试失败: {e}")
        results['conversation_manager'] = False

    try:
        results['personalized_recommender'] = test_personalized_recommender()
    except Exception as e:
        print(f"\n❌ 个性化推荐引擎测试失败: {e}")
        results['personalized_recommender'] = False

    try:
        results['email_service'] = test_email_service()
    except Exception as e:
        print(f"\n❌ 邮件服务测试失败: {e}")
        results['email_service'] = False

    try:
        results['scheduler'] = test_scheduler()
    except Exception as e:
        print(f"\n❌ 调度器测试失败: {e}")
        results['scheduler'] = False

    # Summary
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)

    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)

    for name, passed in results.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"   {name.replace('_', ' ').title()}: {status}")

    print(f"\n   总计: {passed_tests}/{total_tests} 个模块测试通过")

    if passed_tests == total_tests:
        print("\n🎉 所有功能模块测试通过！系统升级成功！")
        return 0
    else:
        print(f"\n⚠️  {total_tests - passed_tests} 个模块测试失败，请检查错误信息")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
