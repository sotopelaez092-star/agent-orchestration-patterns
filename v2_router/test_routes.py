"""
测试路由分类
"""
from routes import classify_topic


def test_classify_topic():
    """测试主题分类"""
    
    # 测试用例
    test_cases = [
        ("OpenAI 完成 100 亿美元融资", "funding"),
        ("GitHub 上最火的 AI 项目", "tech_news"),
        ("Transformer 最新论文解读", "research"),
        ("AI 的发展历史", "general"),
        ("字节跳动准备上市", "funding"),
        ("Hacker News 热门讨论", "tech_news"),
        ("arXiv 上的新研究", "research"),
    ]
    
    print("=" * 60)
    print("测试 classify_topic()")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for topic, expected in test_cases:
        print(f"\n主题: {topic}")
        print(f"期望分类: {expected}")
        
        try:
            result = classify_topic(topic)
            print(f"实际分类: {result}")
            
            if result == expected:
                print("✅ 通过")
                passed += 1
            else:
                print("❌ 失败")
                failed += 1
        except Exception as e:
            print(f"❌ 错误: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试完成：通过 {passed}/{len(test_cases)}，失败 {failed}/{len(test_cases)}")
    print("=" * 60)


if __name__ == "__main__":
    test_classify_topic()