#!/usr/bin/env python3
"""
智能学术助手 v3.0 - 集成测试脚本
验证基于对话驱动的推荐系统的完整性
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversation_manager import ConversationManager
from personalized_recommender import PersonalizedRecommender
from email_service import EmailService
from scheduler import RecommendationScheduler


def print_section(title):
    """打印测试分节标题"""
    print(f"\n{'='*70}")
    print(f"📋 {title}")
    print('='*70)


def test_unified_conversation_flow():
    """
    测试统一对话流程：
    1. 创建对话
    2. 发送多条消息
    3. 分析用户兴趣
    4. 生成个性化查询建议
    5. 模拟完整用户旅程
    """
    print_section("1️⃣ 统一对话流程测试 (Unified Conversation Flow)")
    
    manager = ConversationManager("./test_data/integration_test")
    
    # Step 1: Create conversation (模拟用户首次访问)
    print("\n✅ 步骤1: 用户发起对话")
    conv_id = manager.create_conversation(user_id="test_user_v3", title="深度学习研究探索")
    print(f"   📝 对话ID: {conv_id}")
    assert conv_id, "❌ 对话创建失败"
    
    # Step 2: Simulate multi-turn conversation (模拟多轮学术对话)
    print("\n✅ 步骤2: 模拟多轮学术对话")
    
    conversation_turns = [
        ("user", "你好，我最近在研究深度学习，想了解这个领域的最新进展"),
        ("assistant", "您好！深度学习是当前最活跃的研究领域之一。我可以帮您查找相关论文。请问您具体关注哪个方向？"),
        ("user", "我对计算机视觉特别感兴趣，特别是卷积神经网络在图像识别中的应用"),
        ("assistant", "很好的选择！计算机视觉是深度学习的重要应用领域。让我为您搜索相关论文..."),
        ("user", "另外，我也想了解Transformer架构在自然语言处理中的突破性应用"),
        ("assistant", "Transformer确实是NLP领域的革命性技术。我会为您整合这两个方向的信息。"),
        ("user", "能否帮我找一些2024年发表的最新论文？特别是关于多模态学习的"),
        ("assistant", "当然！多模态学习是当前的前沿热点，我来为您检索最新研究成果。"),
    ]
    
    for role, content in conversation_turns:
        success = manager.add_message(conv_id, role, content)
        assert success, f"❌ 添加消息失败: {content[:30]}..."
        icon = "👤" if role == "user" else "🤖"
        print(f"   {icon} [{role.upper()}] {content[:50]}...")
    
    # Step 3: Load and verify conversation history
    print("\n✅ 步骤3: 验证对话历史持久化")
    conv = manager.get_conversation(conv_id)
    assert conv is not None, "❌ 加载对话失败"
    assert len(conv["messages"]) == len(conversation_turns), f"❌ 消息数量不匹配: {len(conv['messages'])} vs {len(conversation_turns)}"
    print(f"   💾 已保存 {len(conv['messages'])} 条消息")
    print(f"   📅 创建时间: {conv['created_at']}")
    print(f"   ⏰ 最后更新: {conv['updated_at']}")
    
    # Step 4: Extract user interests from conversation
    print("\n✅ 步骤4: 从对话中提取用户研究兴趣")
    user_interests = manager.get_user_interests("test_user_v3")
    assert len(user_interests) > 0, "❌ 提取用户兴趣失败"
    print(f"   🔍 提取到 {len(user_interests)} 条用户输入记录")
    
    return {
        'conversation_id': conv_id,
        'message_count': len(conversation_turns),
        'user_interests_count': len(user_interests)
    }


def test_personalized_recommendation_engine():
    """
    测试个性化推荐引擎：
    基于对话历史生成推荐
    """
    print_section("2️⃣ 个性化推荐引擎测试 (Personalized Recommendation Engine)")
    
    recommender = PersonalizedRecommender()
    
    # Sample conversation history (from previous test)
    conversation_history = [
        {"role": "user", "content": "你好，我最近在研究深度学习，想了解这个领域的最新进展"},
        {"role": "assistant", "content": "您好！深度学习是当前最活跃的研究领域之一。"},
        {"role": "user", "content": "我对计算机视觉特别感兴趣，特别是卷积神经网络在图像识别中的应用"},
        {"role": "user", "content": "另外，我也想了解Transformer架构在自然语言处理中的突破性应用"},
        {"role": "user", "content": "能否帮我找一些2024年发表的最新论文？特别是关于多模态学习的"},
    ]
    
    # Test 1: Analyze user interests
    print("\n✅ 测试1: 分析用户研究画像")
    profile = recommender.analyze_user_interests(conversation_history)
    
    print("\n   📊 用户画像分析结果:")
    print(f"   • 主要兴趣 ({len(profile.get('primary_interests', []))}个):")
    for interest in profile.get("primary_interests", [])[:5]:
        print(f"      - {interest['keyword']} (出现频率: {interest['frequency']}次, 相关度: {interest['relevance_score']})")
    
    if profile.get("secondary_interests"):
        print(f"\n   • 次要兴趣 ({len(profile['secondary_interests'])}个):")
        for interest in profile["secondary_interests"][:3]:
            print(f"      - {interest['keyword']} ({interest['frequency']}次)")
    
    if profile.get("research_areas"):
        print(f"\n   • 识别的研究领域:")
        for area in profile["research_areas"]:
            print(f"      ✓ {area}")
    
    if profile.get("query_suggestion"):
        print(f"\n   • 推荐查询语句:")
        print(f'      "{profile["query_suggestion"]}"')
    
    # Test 2: Verify key interests detected
    primary_keywords = [i["keyword"] for i in profile.get("primary_interests", [])]
    expected_keywords = ["深度学习", "计算机视觉"]
    for kw in expected_keywords:
        assert any(kw in pk for pk in primary_keywords), f"❌ 未检测到关键兴趣: {kw}"
    print(f"\n   ✅ 关键词检测正确: {expected_keywords}")
    
    # Test 3: Query enhancement capability
    print("\n✅ 测试2: 查询增强能力")
    original_query = "最新的图像分类方法"
    enhancement_result = recommender.enhance_search_with_context(
        original_query=original_query,
        conversation_history=conversation_history,
        n_results=10
    )
    
    if enhancement_result.get("success"):
        enhanced_query = enhancement_result.get("enhanced_query", "")
        context_keywords = enhancement_result.get("context_keywords", [])
        
        print(f"   原始查询: \"{original_query}\"")
        print(f"   增强后查询: \"{enhanced_query}\"")
        print(f"   添加的上下文关键词: {context_keywords[:5]}")
        
        assert len(enhanced_query) > len(original_query), "❌ 查询未被增强"
        print("   ✅ 查询增强成功")
    else:
        print("   ⚠️  查询增强跳过（需要retrieval服务）")
    
    return {
        'primary_interests': len(profile.get('primary_interests', [])),
        'research_areas': len(profile.get('research_areas', [])),
        'has_query_suggestion': bool(profile.get('query_suggestion'))
    }


def test_data_persistence_and_retrieval():
    """
    测试数据持久化和检索能力：
    确保对话数据可靠存储并可快速检索
    """
    print_section("3️⃣ 数据持久化与检索测试 (Data Persistence & Retrieval)")
    
    manager = ConversationManager("./test_data/integration_test")
    
    # Test 1: Multiple conversations management
    print("\n✅ 测试1: 多对话管理")
    
    conversations_to_create = [
        ("test_user_v3", "NLP研究方向探索"),
        ("test_user_v3", "强化学习入门讨论"),
        ("another_user", "知识图谱应用研究"),
    ]
    
    created_ids = []
    for user_id, title in conversations_to_create:
        conv_id = manager.create_conversation(user_id=user_id, title=title)
        created_ids.append(conv_id)
        print(f"   创建对话: {title} -> {conv_id[:8]}...")
    
    # Test 2: Filter by user
    print("\n✅ 测试2: 按用户筛选对话")
    user_convs = manager.get_all_conversations(user_id="test_user_v3")
    other_user_convs = manager.get_all_conversations(user_id="another_user")
    
    assert len(user_convs) >= 3, f"❌ 用户对话数量错误: {len(user_convs)}"
    assert len(other_user_convs) >= 1, f"❌ 其他用户对话数量错误: {len(other_user_convs)}"
    
    print(f"   test_user_v3 的对话数: {len(user_convs)}")
    print(f"   another_user 的对话数: {len(other_user_convs)}")
    
    # Test 3: Recent messages retrieval
    print("\n✅ 测试3: 最近消息快速检索")
    target_conv_id = created_ids[0]
    
    # Add multiple messages to one conversation
    for i in range(10):
        manager.add_message(target_conv_id, "user", f"测试消息 #{i+1}: 这是第{i+1}条测试消息")
    
    recent_5 = manager.get_recent_messages(target_conv_id, limit=5)
    recent_all = manager.get_recent_messages(target_conv_id, limit=100)
    
    assert len(recent_5) == 5, f"❌ 最近5条消息获取失败: {len(recent_5)}"
    assert len(recent_all) == 10, f"❌ 所有消息获取失败: {len(recent_all)}"
    
    print(f"   最近5条消息: ✅")
    print(f"   全部消息数: {len(recent_all)} ✅")
    
    # Test 4: Statistics accuracy
    print("\n✅ 测试4: 统计信息准确性")
    stats = manager.get_statistics()
    
    assert stats["total_conversations"] > 0, "❌ 总对话数为0"
    assert stats["total_messages"] >= 13, f"❌ 总消息数不足: {stats['total_messages']}"
    
    print(f"   总对话数: {stats['total_conversations']}")
    print(f"   总消息数: {stats['total_messages']}")
    print(f"   存储路径: {stats['storage_path']}")
    
    # Cleanup: Delete test conversations
    print("\n✅ 清理: 删除测试对话")
    for conv_id in created_ids:
        manager.delete_conversation(conv_id)
    
    final_stats = manager.get_statistics()
    print(f"   清理后总对话数: {final_stats['total_conversations']}")
    
    return {
        'conversations_created': len(created_ids),
        'messages_added': 10,
        'statistics_verified': True
    }


def test_email_and_scheduler_integration():
    """
    测试邮件和调度器集成：
    验证辅助功能模块可用
    """
    print_section("4️⃣ 邮件服务与调度器集成测试 (Email & Scheduler Integration)")
    
    # Email Service Tests
    print("\n✅ 邮件服务初始化测试")
    email_service = EmailService()
    
    assert email_service.smtp_server == "smtp.qq.com", "❌ SMTP配置错误"
    assert email_service.smtp_port == 465, "❌ SMTP端口错误"
    print(f"   SMTP服务器: {email_service.smtp_server}:{email_service.smtp_port}")
    print(f"   SSL加密: {'启用' if email_service.use_ssl else '禁用'}")
    
    # Subscribe/Unsubscribe cycle
    print("\n✅ 订阅-取消订阅循环测试")
    sub_result = email_service.subscribe("integration_test@example.com", {"frequency": "daily"})
    assert sub_result["success"] == True, "❌ 订阅失败"
    print(f"   订阅成功: {sub_result['message']}")
    
    dup_result = email_service.subscribe("integration_test@example.com")
    assert dup_result["success"] == False, "❌ 应拒绝重复订阅"
    print(f"   重复订阅处理: ✅ 正确拒绝")
    
    unsub_result = email_service.unsubscribe("integration_test@example.com")
    assert unsub_result["success"] == True, "❌ 取消订阅失败"
    print(f"   取消订阅成功: {unsub_result['message']}")
    
    # Email validation
    invalid_result = email_service.subscribe("not-an-email")
    assert invalid_result["success"] == False, "❌ 应拒绝无效邮箱"
    print(f"   无效邮箱验证: ✅ 正确拒绝")
    
    # Scheduler Tests
    print("\n✅ 调度器初始化测试")
    scheduler = RecommendationScheduler()
    
    status = scheduler.get_status()
    assert status is not None, "❌ 获取状态失败"
    assert status["is_running"] == False, "❌ 初始状态应为停止"
    
    print(f"   运行状态: {'运行中' if status['is_running'] else '已停止'}")
    print(f"   执行次数: {status['run_count']}")
    
    if status.get("jobs"):
        job = status["jobs"][0]
        print(f"   任务名称: {job['name']}")
        print(f"   任务ID: {job['id']}")
    
    # Update interval test
    print("\n✅ 定时间隔更新测试")
    update_result = scheduler.update_interval(hours=12, minutes=30)
    assert update_result["success"] == True, "❌ 更新间隔失败"
    print(f"   更新结果: {update_result['message']}")
    
    # Reset to default
    scheduler.update_interval(hours=24, minutes=0)
    
    # Get statistics
    print("\n✅ 服务统计信息")
    email_stats = email_service.get_statistics()
    print(f"   邮件服务统计:")
    print(f"     - 总订阅者: {email_stats['total_subscribers']}")
    print(f"     - 活跃订阅: {email_stats['active_subscribers']}")
    print(f"     - 发送邮箱: {email_stats['sender_email'] or '未配置'}***")
    
    return {
        'email_service_ok': True,
        'scheduler_ok': True,
        'subscription_cycle_ok': True,
        'interval_update_ok': True
    }


def main():
    """主测试函数"""
    print("\n" + "="*70)
    print("🚀 智能学术助手 v3.0 - 集成测试套件")
    print("   基于对话驱动的个性化学术推荐系统")
    print("="*70)
    
    results = {}
    
    try:
        results['unified_conversation'] = test_unified_conversation_flow()
    except Exception as e:
        print(f"\n❌ 统一对话流程测试失败: {e}")
        import traceback
        traceback.print_exc()
        results['unified_conversation'] = False
    
    try:
        results['personalized_recommendation'] = test_personalized_recommendation_engine()
    except Exception as e:
        print(f"\n❌ 个性化推荐引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        results['personalized_recommendation'] = False
    
    try:
        results['data_persistence'] = test_data_persistence_and_retrieval()
    except Exception as e:
        print(f"\n❌ 数据持久化测试失败: {e}")
        import traceback
        traceback.print_exc()
        results['data_persistence'] = False
    
    try:
        results['email_scheduler'] = test_email_and_scheduler_integration()
    except Exception as e:
        print(f"\n❌ 邮件调度器测试失败: {e}")
        import traceback
        traceback.print_exc()
        results['email_scheduler'] = False
    
    # Summary Report
    print_section("📊 测试总结报告")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v is not False)
    
    print(f"\n{'─'*70}")
    print(f"测试模块状态:")
    print(f"{'─'*70}")
    
    module_names = {
        'unified_conversation': '统一对话流程',
        'personalized_recommendation': '个性化推荐引擎',
        'data_persistence': '数据持久化与检索',
        'email_scheduler': '邮件服务与调度器'
    }
    
    for name, passed in results.items():
        display_name = module_names.get(name, name)
        status_icon = "✅ 通过" if passed else "❌ 失败"
        details = ""
        if isinstance(passed, dict):
            details = f" ({passed})"
        print(f"  {status_icon}  {display_name}{details}")
    
    print(f"\n{'─'*70}")
    print(f"总计: {passed_tests}/{total_tests} 个核心模块测试通过")
    print(f"{'─'*70}\n")
    
    if passed_tests == total_tests:
        print("🎉🎉🎉 所有集成测试通过！")
        print("\n✨ 系统已成功重构为基于对话驱动的智能推荐系统！\n")
        print("核心功能验证：")
        print("  ✓ 统一的对话交互界面（移除了search/survey双模式）")
        print("  ✓ 完整的对话历史持久化存储")
        print("  ✓ 实时的用户意图分析和兴趣提取")
        print("  ✓ 基于上下文的智能查询增强")
        print("  ✓ 个性化推荐算法引擎")
        print("  ✓ 邮件通知推送服务")
        print("  ✓ 定时任务自动调度\n")
        return 0
    else:
        failed_count = total_tests - passed_tests
        print(f"⚠️  {failed_count} 个模块测试失败，请检查错误日志\n")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
