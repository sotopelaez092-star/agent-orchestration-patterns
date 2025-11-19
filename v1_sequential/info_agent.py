"""
V1: Sequential 模式 - AI 信息获取助手
"""
from typing import Dict
import logging
from tools import search_web, call_llm

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def sequential_info_agent(topic: str, max_results: int = 5) -> Dict:
    """
    Sequential 模式：顺序执行信息获取流程
    
    流程：搜索 → 筛选 → 总结 → 格式化
    
    Args:
        topic: 要查询的主题
        max_results: 搜索结果数量，默认 5
    
    Returns:
        {
            "topic": "主题",
            "summary": "总结内容",
            "formatted_output": "Markdown 格式的完整报告"
        }
    
    Raises:
        ValueError: 当 topic 为空时
    """
    # 1. 输入验证
    if not topic or not isinstance(topic, str):
        raise ValueError("topic 必须是非空字符串")
    
    logger.info(f"=" * 60)
    logger.info(f"开始 Sequential 流程，主题：{topic}")
    logger.info(f"=" * 60)
    
    # Step 1: 搜索信息
    logger.info("Step 1: 搜索信息...")
    search_results = search_web(topic, max_results=max_results)

    if not search_results:
        logger.error("搜索失败，无法继续")
        raise RuntimeError("搜索失败")
    
    logger.info(f"搜索完成，找到 {len(search_results)} 条结果")

    # step 2: 筛选内容
    logger.info("\nStep 2: 筛选内容...")

    # 构建搜索结果文件
    search_text = ""
    for i, result in enumerate(search_results, 1):
        search_text += f"{i}. {result['title']}\n"
        search_text += f"   {result['snippet']}\n\n"

    # 让 LLM 筛选相关内容
    filter_prompt = f"""
你是一个信息筛选专家。请分析以下搜索结果，判断哪些内容与主题 "{topic}" 相关。

搜索结果：
{search_text}

请输出：
1. 相关的结果编号（如：1, 3, 5）
2. 简要说明为什么相关

格式：
相关编号：1, 3, 5
理由：这些结果直接讨论了该主题的核心内容
"""

    filter_result = call_llm(filter_prompt, temperature=0.3)

    if not filter_result:
        logger.warning("筛选失败，使用所有搜索结果")
        filtered_results = search_results
    else:
        logger.info(f"筛选完成：\n{filter_result}")
        # 这里简化处理，实际应该解析 LLM 返回的编号
        # 暂时使用所有结果
        filtered_results = search_results
    
    logger.info(f"保留 {len(filtered_results)} 条相关结果")

    logger.info(f"保留 {len(filtered_results)} 条相关结果")
    
    # Step 3: 总结信息
    logger.info("\nStep 3: 生成摘要...")
    
    # 构建用于总结的内容
    content_for_summary = ""
    for i, result in enumerate(filtered_results, 1):
        content_for_summary += f"## 来源 {i}: {result['title']}\n"
        content_for_summary += f"{result['snippet']}\n"
        content_for_summary += f"链接：{result['url']}\n\n"
    
    # 让 LLM 生成摘要
    summary_prompt = f"""
你是一个专业的信息分析师。请根据以下内容，生成关于 "{topic}" 的深度摘要。

要求：
1. 提取核心要点（3-5个）
2. 突出最新动态和趋势
3. 语言简洁专业
4. 300-500字

内容：
{content_for_summary}

请直接输出摘要内容，不要有其他废话。
"""
    
    summary = call_llm(summary_prompt, temperature=0.5, max_tokens=1000)
    
    if not summary:
        logger.error("摘要生成失败")
        raise RuntimeError("无法生成摘要")
    
    logger.info("摘要生成完成")

    logger.info("摘要生成完成")
    
    # Step 4: 格式化输出
    logger.info("\nStep 4: 格式化输出...")
    
    # 生成 Markdown 格式报告
    formatted_output = f"""# 📊 {topic} - 信息报告

## 📝 核心摘要

{summary}

---

## 📚 详细来源

"""
    
    # 添加每个来源的详细信息
    for i, result in enumerate(filtered_results, 1):
        formatted_output += f"### {i}. {result['title']}\n\n"
        formatted_output += f"**摘要**: {result['snippet']}\n\n"
        formatted_output += f"**链接**: [{result['url']}]({result['url']})\n\n"
        formatted_output += "---\n\n"
    
    # 添加生成时间
    from datetime import datetime
    formatted_output += f"\n*报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
    
    logger.info("格式化完成")
    logger.info("=" * 60)
    logger.info("Sequential 流程执行完毕！")
    logger.info("=" * 60)
    
    # 返回结果
    return {
        "topic": topic,
        "summary": summary,
        "formatted_output": formatted_output,
        "sources": filtered_results
    }

if __name__ == "__main__":
    # 测试
    topic = "AI Agent 最新进展"
    result = sequential_info_agent(topic)
    print(result['formatted_output'])