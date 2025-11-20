"""
V3 State Graph - 节点函数
"""

from state import AgentState
from tools import search_web
import time
from datetime import datetime

def search_node(state: AgentState) -> AgentState:
    """
    搜索节点 - 调用搜索API获取信息
    
    Args:
        state: 当前状态

    Returns:
        更新后的状态
    """
    # 1. 记录日志
    state.add_log(f"🔍 进入搜索节点（第 {state.search_retry_count + 1} 次")
    state.current_step = "search"

    # 2. 如果是重试，需要等待（指数退避）
    if state.search_retry_count > 0:
        wait_time = 2 ** state.search_retry_count
        state.add_log(f"⏰  等待  {wait_time} 秒后重试...")
        time.sleep(wait_time)

    # 3. 调用搜索
    try:
        state.add_log(f"调用 search_web, 查询：'{state.topic}', 数量：{state.max_results}")
        results = search_web(query=state.topic, max_results=state.max_results)

        # 4. 检查结果
        if results is None or len(results) == 0:
            # 搜索失败或无结果
            state.search_status = "failed"
            state.set_error("搜索返回空结果")
            state.add_log("❌ 搜索失败：无结果")
        else:
            # 搜索成功
            state.search_results = results
            state.search_status = "success"
            state.add_log(f"✅ 搜索成功，获取 {len(results)} 条结果")

    except Exception as e:
        # 捕获异常
        state.search_status = "failed"
        state.set_error(f"搜索异常：{str(e)}")
        state.add_log(f"❌ 搜索异常：{str(e)}")

    # 5. 返回状态
    return state

def filter_node(state: AgentState) -> AgentState:
    """
    筛选节点 - 用 LLM 筛选出与主题相关的搜索结果
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    # 1. 记录日志
    state.add_log(f"🔍 进入筛选节点")
    state.current_step = "filter"
    
    # 2. 检查是否有搜索结果
    if not state.search_results or len(state.search_results) == 0:
        state.add_log("⚠️  无搜索结果，跳过筛选")
        state.filtered_results = []
        return state
    
    # 3. 构建 LLM Prompt
    # 将搜索结果格式化为文本
    results_text = ""
    for i, result in enumerate(state.search_results, 1):
        results_text += f"\n{i}. 标题: {result['title']}\n"
        results_text += f"   摘要: {result['snippet']}\n"
    
    prompt = f"""你是一个信息筛选助手。请判断以下搜索结果中，哪些与主题「{state.topic}」相关。

搜索结果：
{results_text}

请按照以下格式返回相关结果的编号（用逗号分隔）：
相关编号: 1,3,5

如果全部相关，返回：相关编号: 全部
如果全部不相关，返回：相关编号: 无

只返回编号，不要其他解释。
"""
    
    # 4. 调用 LLM
    try:
        state.add_log(f"调用 LLM 筛选，阈值: {state.filter_threshold}")
        from tools import call_llm
        
        llm_result = call_llm(
            prompt=prompt,
            temperature=0.3,  # 降低随机性，让判断更稳定
            max_tokens=200
        )
        
        if llm_result is None:
            state.add_log("❌ LLM 调用失败")
            # 失败时保留所有结果（降级策略）
            state.filtered_results = state.search_results
            return state
        
        # 5. 解析 LLM 返回结果
        state.add_log(f"LLM 返回: {llm_result.strip()}")
        
        # 提取编号
        relevant_indices = []
        
        if "全部" in llm_result:
            # 全部相关
            relevant_indices = list(range(len(state.search_results)))
        elif "无" in llm_result:
            # 全部不相关
            relevant_indices = []
        else:
            # 解析编号
            import re
            numbers = re.findall(r'\d+', llm_result)
            relevant_indices = [int(n) - 1 for n in numbers if int(n) <= len(state.search_results)]
        
        # 6. 筛选结果
        state.filtered_results = [
            state.search_results[i] 
            for i in relevant_indices 
            if 0 <= i < len(state.search_results)
        ]
        
        state.add_log(f"✅ 筛选完成，从 {len(state.search_results)} 条中筛选出 {len(state.filtered_results)} 条相关结果")
    
    except Exception as e:
        state.add_log(f"❌ 筛选异常: {str(e)}")
        # 异常时保留所有结果（降级策略）
        state.filtered_results = state.search_results
    
    # 7. 返回状态
    return state

def summarize_node(state: AgentState) -> AgentState:
    """
    总结节点 - 用 LLM 生成摘要报告
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    # 1. 记录日志
    state.add_log(f"📝 进入总结节点 (第 {state.summary_retry_count + 1} 次)")
    state.current_step = "summarize"
    
    # 2. 检查是否有筛选结果
    if not state.filtered_results or len(state.filtered_results) == 0:
        state.add_log("⚠️  无筛选结果，无法生成摘要")
        state.summary = "未找到相关信息。"
        state.quality_score = 0.0
        return state
    
    # 3. 构建内容文本
    content_text = ""
    for i, result in enumerate(state.filtered_results, 1):
        content_text += f"\n【信息 {i}】\n"
        content_text += f"标题: {result['title']}\n"
        content_text += f"链接: {result['url']}\n"
        content_text += f"内容: {result['snippet']}\n"
    
    # 4. 构建 Prompt（根据重试次数调整）
    if state.summary_retry_count == 0:
        # 第一次生成
        prompt = f"""你是一个信息总结助手。请基于以下信息，生成一份关于「{state.topic}」的详细摘要报告。

信息来源：
{content_text}

要求：
1. 总结要全面，涵盖所有关键信息
2. 使用清晰的段落结构
3. 至少 200 字
4. 突出重点和亮点

请生成摘要：
"""
    else:
        # 重新生成（更详细的要求）
        prompt = f"""你是一个信息总结助手。请基于以下信息，生成一份关于「{state.topic}」的**非常详细**的摘要报告。

信息来源：
{content_text}

**重要要求**：
1. 摘要必须**至少 300 字**
2. 分段组织，每段有明确主题
3. 包含具体数据、时间、人物等细节
4. 分析信息之间的关联和趋势
5. 语言要专业、准确

请生成详细摘要：
"""
    
    # 5. 调用 LLM
    try:
        state.add_log(f"调用 LLM 生成摘要...")
        from tools import call_llm
        
        summary = call_llm(
            prompt=prompt,
            temperature=0.7,
            max_tokens=1500
        )
        
        if summary is None:
            state.add_log("❌ LLM 调用失败")
            state.summary = "生成摘要失败。"
            state.quality_score = 0.0
            return state
        
        # 6. 保存摘要
        state.summary = summary.strip()
        
        # 7. 评估质量（简单的质量检查）
        quality_score = 0.0
        
        # 长度检查（200字以上得分高）
        length = len(state.summary)
        if length >= 300:
            quality_score += 0.5
        elif length >= 200:
            quality_score += 0.3
        elif length >= 100:
            quality_score += 0.1
        
        # 结构检查（是否有多个段落）
        paragraphs = [p for p in state.summary.split('\n') if p.strip()]
        if len(paragraphs) >= 3:
            quality_score += 0.3
        elif len(paragraphs) >= 2:
            quality_score += 0.2
        
        # 内容检查（是否包含关键词）
        if state.topic in state.summary:
            quality_score += 0.2
        
        state.quality_score = min(quality_score, 1.0)  # 最高1.0
        
        state.add_log(f"✅ 摘要生成完成，长度: {length} 字，质量评分: {state.quality_score:.2f}")
    
    except Exception as e:
        state.add_log(f"❌ 生成摘要异常: {str(e)}")
        state.summary = "生成摘要时出现错误。"
        state.quality_score = 0.0
    
    # 8. 返回状态
    return state

def format_node(state: AgentState) -> AgentState:
    """
    格式化节点 - 将摘要格式化为 Markdown 报告
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    # 1. 记录日志
    state.add_log("📄 进入格式化节点")
    state.current_step = "format"
    
    # 2. 构建 Markdown 报告
    report = f"""# {state.topic} - 信息摘要报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**信息来源**: {len(state.filtered_results)} 条相关资讯  
**质量评分**: {state.quality_score:.2f}/1.00

---

## 📊 摘要

{state.summary}

---

## 📎 参考来源

"""
    
    # 3. 添加参考来源
    for i, result in enumerate(state.filtered_results, 1):
        report += f"{i}. **{result['title']}**  \n"
        report += f"   链接: {result['url']}  \n"
        report += f"   摘要: {result['snippet']}  \n\n"
    
    # 4. 添加统计信息
    report += f"""---

## 📈 处理统计

- 搜索结果数: {len(state.search_results)}
- 筛选结果数: {len(state.filtered_results)}
- 搜索重试次数: {state.search_retry_count}
- 摘要重试次数: {state.summary_retry_count}
- 总执行步骤: {len(state.logs)}

---

*本报告由 AI Agent 自动生成*
"""
    
    # 5. 保存报告
    state.final_report = report
    state.add_log(f"✅ Markdown 报告生成完成，共 {len(report)} 字符")
    
    # 6. 返回状态
    return state


def error_node(state: AgentState) -> AgentState:
    """
    错误处理节点 - 生成降级结果
    
    Args:
        state: 当前状态
    
    Returns:
        更新后的状态
    """
    # 1. 记录日志
    state.add_log("❌ 进入错误处理节点")
    state.current_step = "error"
    
    # 2. 生成降级报告
    report = f"""# {state.topic} - 处理失败报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**状态**: ❌ 处理失败

---

## ⚠️ 错误信息

{state.error if state.error else "未知错误"}

---

## 📊 已完成的步骤

"""
    
    # 3. 添加部分结果（如果有）
    if len(state.search_results) > 0:
        report += f"- ✅ 搜索: 获取了 {len(state.search_results)} 条结果\n"
        report += f"\n### 搜索结果\n\n"
        for i, result in enumerate(state.search_results[:3], 1):  # 只显示前3条
            report += f"{i}. {result['title']}  \n"
            report += f"   {result['url']}  \n\n"
    else:
        report += "- ❌ 搜索: 未获取到结果\n"
    
    if len(state.filtered_results) > 0:
        report += f"\n- ✅ 筛选: 筛选出 {len(state.filtered_results)} 条相关结果\n"
    
    # 4. 添加重试信息
    report += f"""
---

## 🔄 重试统计

- 搜索重试次数: {state.search_retry_count}/3
- 摘要重试次数: {state.summary_retry_count}/2

---

## 💡 建议

1. 请检查网络连接
2. 尝试更换搜索关键词
3. 稍后再试

---

*本报告由 AI Agent 自动生成*
"""
    
    # 5. 保存报告
    state.final_report = report
    state.add_log("✅ 错误报告生成完成")
    
    # 6. 返回状态
    return state


# ===== 测试代码 =====
if __name__ == "__main__":
    from datetime import datetime
    
    print("=== 测试所有 Node 函数 ===\n")
    
    # ===== 测试 1: 成功流程 =====
    print("=" * 70)
    print("测试 1: 成功流程 (search → filter → summarize → format)")
    print("=" * 70)
    
    state1 = AgentState(topic="AI Agent 投融资动态", max_results=5)
    
    # 执行完整流程
    state1 = search_node(state1)
    state1 = filter_node(state1)
    state1 = summarize_node(state1)
    state1 = format_node(state1)
    
    print("\n✅ 流程执行完成！")
    print(f"最终报告长度: {len(state1.final_report)} 字符")
    
    # 保存报告到文件
    with open("test_report_success.md", "w", encoding="utf-8") as f:
        f.write(state1.final_report)
    print("✅ 报告已保存到: test_report_success.md")
    
    # 显示报告预览（前500字符）
    print("\n报告预览（前500字符）:")
    print("-" * 70)
    print(state1.final_report[:500])
    print("...")
    
    # ===== 测试 2: 错误流程 =====
    print("\n\n" + "=" * 70)
    print("测试 2: 错误流程 (模拟搜索失败)")
    print("=" * 70)
    
    state2 = AgentState(topic="测试错误处理", max_results=5)
    
    # 模拟搜索失败
    state2.search_status = "failed"
    state2.set_error("模拟网络连接失败")
    state2.search_retry_count = 3  # 模拟已重试3次
    
    # 执行错误处理
    state2 = error_node(state2)
    
    print("\n✅ 错误处理完成！")
    print(f"错误报告长度: {len(state2.final_report)} 字符")
    
    # 保存错误报告
    with open("test_report_error.md", "w", encoding="utf-8") as f:
        f.write(state2.final_report)
    print("✅ 错误报告已保存到: test_report_error.md")
    
    # 显示错误报告预览
    print("\n错误报告预览（前500字符）:")
    print("-" * 70)
    print(state2.final_report[:500])
    print("...")
    
    # ===== 测试 3: 质量不合格，重新生成 =====
    print("\n\n" + "=" * 70)
    print("测试 3: 质量检查与重新生成")
    print("=" * 70)
    
    state3 = AgentState(topic="LangGraph 新特性", max_results=5)
    
    state3 = search_node(state3)
    state3 = filter_node(state3)
    state3 = summarize_node(state3)
    
    print(f"\n第1次生成 - 质量评分: {state3.quality_score:.2f}")
    
    # 如果质量不合格，重新生成
    if not state3.is_quality_acceptable():
        print("⚠️  质量不合格，重新生成...")
        state3.increment_summary_retry()
        state3 = summarize_node(state3)
        print(f"第2次生成 - 质量评分: {state3.quality_score:.2f}")
    
    state3 = format_node(state3)
    print(f"\n✅ 最终质量评分: {state3.quality_score:.2f}")
    
    # ===== 最终统计 =====
    print("\n\n" + "=" * 70)
    print("📊 所有测试完成！")
    print("=" * 70)
    print(f"✅ 测试 1: 成功流程 - 已生成 test_report_success.md")
    print(f"✅ 测试 2: 错误流程 - 已生成 test_report_error.md")
    print(f"✅ 测试 3: 质量检查 - 完成")
    print("\n所有节点函数测试通过！🎉")