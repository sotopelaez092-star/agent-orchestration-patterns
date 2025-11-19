"""
测试不同的处理函数
"""
from info_agent import handle_funding, handle_general, handle_tech_news, handle_research


def test_handle_funding():
    """测试投融资处理"""
    topic = "OpenAI 最新融资情况"
    
    print("=" * 60)
    print("测试 handle_funding()")
    print("=" * 60)
    print(f"主题: {topic}\n")
    
    try:
        result = handle_funding(topic, max_results=3)
        print("✅ 执行成功！\n")
        print(result['summary'][:300] + "...\n")
    except Exception as e:
        print(f"❌ 执行失败: {e}")


def test_handle_tech_news():
    """测试技术资讯处理"""
    topic = "GitHub 上最火的 AI 项目"
    
    print("=" * 60)
    print("测试 handle_tech_news()")
    print("=" * 60)
    print(f"主题: {topic}\n")
    
    try:
        result = handle_tech_news(topic, max_results=3)
        print("✅ 执行成功！\n")
        print(result['summary'][:300] + "...\n")
    except Exception as e:
        print(f"❌ 执行失败: {e}")


def test_handle_research():
    """测试学术研究处理"""
    topic = "Transformer 最新研究进展"
    
    print("=" * 60)
    print("测试 handle_research()")
    print("=" * 60)
    print(f"主题: {topic}\n")
    
    try:
        result = handle_research(topic, max_results=3)
        print("✅ 执行成功！\n")
        print(result['summary'][:300] + "...\n")
    except Exception as e:
        print(f"❌ 执行失败: {e}")


if __name__ == "__main__":
    # 测试所有处理函数
    test_handle_funding()
    print("\n")
    test_handle_tech_news()
    print("\n")
    test_handle_research()