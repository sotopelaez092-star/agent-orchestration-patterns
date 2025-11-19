"""
路由策略模块
"""
import logging
from typing import Literal
from tools import call_llm
import re
logger = logging.getLogger(__name__)

# 定义支持的的分类
CategoryType = Literal["funding", "tech_news", "research", "general"]

def classify_topic(topic: str) -> CategoryType:
    """
    使用 LLM 判断主题属于哪一类

    Args:
        topic: 用户输入的主题

    Returns:
        分类结果："funding" | "tech_news" | "research" | "general"
    """

    # 1. 输入验证
    if not topic or not isinstance(topic, str):
        logger.error("输入主题为空或不是字符串")
        raise ValueError("主题必须是非空字符串")

    # 2. 构建Prompt
    prompt = f"""
你是一个主题分类专家。请将以下主题分类到这4个类别之一：

分类定义：
1. funding - 投融资类
   关键词：融资、投资、上市、估值、资本
   
2. tech_news - 技术资讯类
   关键词：GitHub、开源项目、技术博客、产品发布
   
3. research - 学术研究类
   关键词：论文、arXiv、研究、算法
   
4. general - 其他/综合类
   不属于以上任何类别

示例：
- "OpenAI 完成新一轮融资" → funding
- "GitHub Trending 上的 AI 项目" → tech_news  
- "Transformer 最新论文" → research

现在请分类："{topic}"

重要：只输出一个单词（funding/tech_news/research/general），不要有任何其他内容！
"""

    # 3. 调用 call_llm
    result = call_llm(prompt, temperature=0.1, max_tokens=10)
    
    if not result:
        logger.error("分类失败")
        raise RuntimeError("无法分类主题")
    


    # 4. 解析结果（方案C - 组合）
    result_lower = result.strip().lower()

    # 尝试1: 正则精确匹配
    match = re.search(r'\b(funding|tech_news|research|general)\b', result_lower)

    if match:
        category = match.group(1)
        logger.info(f"主题分类完成（精确匹配）：{category}")
        return category

    # 尝试2: 关键词包含检查
    if "funding" in result_lower or "投融资" in result_lower:
        category = "funding"
    elif "tech" in result_lower or "github" in result_lower:
        category = "tech_news"
    elif "research" in result_lower or "论文" in result_lower:
        category = "research"
    else:
        logger.warning(f"无法识别分类，使用默认 general。LLM返回：{result}")  # ← 加这行
        category = "general"

    logger.info(f"主题分类完成（关键词匹配）：{category}")
    return category

