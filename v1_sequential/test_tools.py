"""
测试工具函数
"""
from tools import call_llm, search_web


def test_call_llm():
    """测试 LLM 调用"""
    prompt = "请用一句话介绍什么是 AI Agent"
    
    print("=" * 50)
    print("测试 call_llm()")
    print("=" * 50)
    print(f"输入: {prompt}")
    print("-" * 50)
    
    result = call_llm(prompt)
    
    if result:
        print(f"输出: {result}")
        print("=" * 50)
        print("✅ 测试通过！")
    else:
        print("❌ 测试失败！")

def test_search_web():
    """测试网络搜索"""
    query = "AI Agent 最新进展"
    
    print("\n" + "=" * 50)
    print("测试 search_web()")
    print("=" * 50)
    print(f"搜索关键词: {query}")
    print("-" * 50)
    
    results = search_web(query, max_results=3)
    
    if results:
        print(f"找到 {len(results)} 条结果：\n")
        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   摘要: {result['snippet'][:80]}...")
            print()
        print("=" * 50)
        print("✅ 测试通过！")
    else:
        print("❌ 测试失败！")


if __name__ == "__main__":
    test_call_llm()
    test_search_web()  # 添加这行
