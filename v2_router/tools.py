"""
工具函数模块
"""
import os
from typing import Optional
import logging
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def call_llm(
    prompt: str,
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Optional[str]:
    """
        调用 LLM 生成回答
        
        Args:
            prompt: 输入提示词
            model: 模型名称，默认 deepseek-chat
            temperature: 温度参数，控制随机性，默认 0.7
            max_tokens: 最大生成 token 数，默认 2000
        
        Returns:
            LLM 生成的文本，失败返回 None
        
        Raises:
            ValueError: 当 prompt 为空时
    """
    # 1. 输入验证
    if not prompt or not isinstance(prompt, str):
        raise ValueError("prompt 必须是非空字符串")
    
    if not 0 <= temperature <= 2:
        raise ValueError("temperature 必须在 0-2 之间")
    
    if max_tokens <= 0:
        raise ValueError("max_tokens 必须大于 0")
    
    # 记录日志
    logger.info(f"开始调用 LLM，模型：{model}，prompt 长度：{len(prompt)}")
    
    # 2. 获取 API Key
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        logger.error("未找到 DEEPSEEK_API_KEY 环境变量")
        raise ValueError("请在 .env 文件中设置 DEEPSEEK_API_KEY")

    # 3. 初始化客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1",
    )

    # 4. 调用 API
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )

        # 5. 提取结果
        result = response.choices[0].message.content
        
        logger.info(f"LLM 调用成功，返回长度：{len(result)}")
        return result

    except Exception as e:
        logger.error(f"LLM 调用失败：{str(e)}")
        return None

def search_web(
    query: str,
    max_results: int = 5
) -> Optional[list]:
    """
    网络搜索
    
    Args:
        query: 搜索关键词
        max_results: 返回结果数量，默认 5
    
    Returns:
        搜索结果列表，每个结果包含 title, url, snippet
        [
            {
                "title": "标题",
                "url": "链接", 
                "snippet": "摘要"
            },
            ...
        ]
        失败返回 None
    
    Raises:
        ValueError: 当 query 为空时
    """
    # 1. 输入验证
    if not query or not isinstance(query, str):
        raise ValueError("query 必须是非空字符串")
    
    if max_results <= 0:
        raise ValueError("max_results 必须大于 0")
    
    logger.info(f"开始搜索：{query}，返回 {max_results} 条结果")
    
    # 2. Mock 数据（模拟搜索结果）
    # TODO: 将来替换为真实的搜索 API
    mock_results = [
        {
            "title": "AI Agent 技术白皮书 2024",
            "url": "https://example.com/ai-agent-whitepaper-2024",
            "snippet": "本白皮书详细介绍了 2024 年 AI Agent 技术的最新发展，包括 LangChain、LangGraph 等主流框架的应用实践，以及多智能体协作的创新模式。"
        },
        {
            "title": "OpenAI 宣布推出 GPT-5，Agent 能力大幅提升",
            "url": "https://example.com/openai-gpt5-agent",
            "snippet": "OpenAI 今日宣布推出 GPT-5 模型，新模型在 Agent 任务规划、工具调用等方面性能提升 40%，支持更复杂的多步骤推理。"
        },
        {
            "title": "AI 投融资周报：Agent 赛道融资总额突破 5 亿美元",
            "url": "https://example.com/ai-funding-weekly",
            "snippet": "本周 AI Agent 领域共完成 8 笔融资，总金额达 5.2 亿美元。其中，AutoGPT 完成 C 轮 2 亿美元融资，估值达 15 亿美元。"
        },
        {
            "title": "LangChain 发布 0.3 版本，新增状态图编排功能",
            "url": "https://example.com/langchain-0.3-release",
            "snippet": "LangChain 团队宣布发布 0.3 版本，新增 LangGraph 状态图编排功能，支持更灵活的 Agent 工作流设计，并优化了性能和易用性。"
        },
        {
            "title": "AI Agent 在企业中的应用现状调研报告",
            "url": "https://example.com/ai-agent-enterprise-survey",
            "snippet": "最新调研显示，68% 的企业已经开始尝试 AI Agent 技术，主要应用于客服、数据分析、代码生成等场景，平均效率提升 30%。"
        },
        {
            "title": "Multi-Agent 系统设计最佳实践",
            "url": "https://example.com/multi-agent-best-practices",
            "snippet": "本文总结了 Multi-Agent 系统设计的 10 条最佳实践，包括角色定义、通信协议、任务分配策略等，并提供了多个实际案例。"
        },
        {
            "title": "Anthropic Claude 3.5 正式发布，Agent 性能行业领先",
            "url": "https://example.com/claude-3.5-release",
            "snippet": "Anthropic 发布 Claude 3.5 模型，在 Agent 基准测试中超越 GPT-4，特别是在复杂推理和工具调用场景下表现出色。"
        }
    ]
    
    # 3. 返回指定数量的结果
    results = mock_results[:max_results]
    logger.info(f"搜索完成，返回 {len(results)} 条结果")
    
    return results
