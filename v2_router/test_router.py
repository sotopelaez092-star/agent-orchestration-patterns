"""
测试完整的 Router 系统
"""
from info_agent import router_info_agent


def test_router_complete():
    """测试完整的路由功能"""
    
    # 测试用例（不同类型的主题）
    test_cases = [
        ("OpenAI 完成 100 亿美元融资", "funding"),
        ("GitHub 上最火的 AI 项目", "tech_news"),
        ("Transformer 最新研究论文", "research"),
        ("AI 的发展历史", "general"),
    ]
    
    print("=" * 70)
    print("测试完整的 Router 系统")
    print("=" * 70)
    
    for topic, expected_category in test_cases:
        print(f"\n主题: {topic}")
        print(f"期望分类: {expected_category}")
        print("-" * 70)
        
        try:
            result = router_info_agent(topic, max_results=3)
            
            actual_category = result['category']
            print(f"实际分类: {actual_category}")
            
            if actual_category == expected_category:
                print("✅ 分类正确")
            else:
                print(f"⚠️  分类不符（期望 {expected_category}，实际 {actual_category}）")
            
            # 显示摘要前200字
            print(f"\n摘要预览:\n{result['summary'][:200]}...")
            print("=" * 70)
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            print("=" * 70)


def test_router_single():
    """单个详细测试"""
    topic = "AI Agent 领域最新投融资"
    
    print("\n" + "=" * 70)
    print("详细测试单个主题")
    print("=" * 70)
    print(f"主题: {topic}\n")
    
    result = router_info_agent(topic, max_results=5)
    
    print(f"分类: {result['category']}")
    print("\n完整报告:")
    print("-" * 70)
    print(result['formatted_output'])


if __name__ == "__main__":
    # 测试多个用例
    test_router_complete()
    
    # 详细测试单个（可选）
    # test_router_single()