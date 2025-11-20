"""
V3 State Graph - 决策函数
"""

from state import AgentState
import time


def decide_after_search(state: AgentState) -> str:
    """
    搜索后的决策：判断搜索是否成功
    
    Args:
        state: 当前状态
    
    Returns:
        下一步节点名称：
        - "filter": 搜索成功，进入筛选
        - "retry": 搜索失败，需要重试
    """
    if state.search_status == "success":
        state.add_log("✅ 决策：搜索成功 → 进入筛选")
        return "filter"
    else:
        state.add_log("❌ 决策：搜索失败 → 检查重试次数")
        return "retry"


def decide_retry(state: AgentState) -> str:
    """
    重试决策：判断是否达到重试上限
    
    Args:
        state: 当前状态
    
    Returns:
        下一步节点名称：
        - "search": 继续重试搜索
        - "error": 达到上限，进入错误处理
    """
    if state.is_search_retry_limit_reached():
        state.add_log("❌ 决策：已达重试上限(3次) → 进入错误处理")
        return "error"
    else:
        state.add_log(f"🔄 决策：重试 {state.search_retry_count}/3 → 等待后重试")
        state.increment_search_retry()
        return "search"


def decide_after_filter(state: AgentState) -> str:
    """
    筛选后的决策：判断结果是否足够
    
    Args:
        state: 当前状态
    
    Returns:
        下一步节点名称：
        - "summarize": 结果足够(≥3条)，进入总结
        - "expand": 结果不够，需要扩大搜索
    """
    if state.has_enough_filtered_results(min_count=3):
        state.add_log(f"✅ 决策：筛选结果充足({len(state.filtered_results)}条) → 进入总结")
        return "summarize"
    else:
        state.add_log(f"⚠️  决策：筛选结果不足({len(state.filtered_results)}条) → 检查扩大策略")
        return "expand"


def decide_expand(state: AgentState) -> str:
    """
    扩大搜索决策：判断是否已经扩大过
    
    Args:
        state: 当前状态
    
    Returns:
        下一步节点名称：
        - "expand_search": 未扩大，扩大搜索范围
        - "lower_threshold": 已扩大，降低筛选标准
    """
    if not state.search_expanded:
        state.add_log("🔍 决策：未扩大过 → 扩大搜索范围")
        state.expand_search()
        return "search"  # 扩大后重新搜索
    else:
        state.add_log("📉 决策：已扩大过 → 降低筛选标准")
        state.lower_filter_threshold()
        return "filter"  # 降低标准后重新筛选


def decide_after_summarize(state: AgentState) -> str:
    """
    总结后的决策：判断质量是否合格
    
    Args:
        state: 当前状态
    
    Returns:
        下一步节点名称：
        - "format": 质量合格，进入格式化
        - "regenerate": 质量不合格，检查重新生成
    """
    if state.is_quality_acceptable(min_score=0.7):
        state.add_log(f"✅ 决策：质量合格({state.quality_score:.2f}) → 进入格式化")
        return "format"
    else:
        state.add_log(f"⚠️  决策：质量不合格({state.quality_score:.2f}) → 检查重新生成")
        return "regenerate"


def decide_regenerate(state: AgentState) -> str:
    """
    重新生成决策：判断是否达到重新生成上限
    
    Args:
        state: 当前状态
    
    Returns:
        下一步节点名称：
        - "summarize": 继续重新生成
        - "format": 达到上限，使用当前版本
    """
    if state.is_summary_retry_limit_reached():
        state.add_log("⚠️  决策：已达重新生成上限(2次) → 使用当前版本")
        return "format"  # 虽然质量不够，但也只能用了
    else:
        state.add_log(f"🔄 决策：重新生成 {state.summary_retry_count}/2 → 优化Prompt重试")
        state.increment_summary_retry()
        return "summarize"


# ===== 测试代码 =====
if __name__ == "__main__":
    print("=== 测试 Decision 函数 ===\n")
    
    # ===== 测试 1: decide_after_search =====
    print("=" * 60)
    print("测试 1: decide_after_search")
    print("=" * 60)
    
    state1 = AgentState(topic="测试", max_results=5)
    
    # 情况1：搜索成功
    state1.search_status = "success"
    next_step = decide_after_search(state1)
    print(f"搜索成功 → 下一步: {next_step}")
    
    # 情况2：搜索失败
    state1.search_status = "failed"
    next_step = decide_after_search(state1)
    print(f"搜索失败 → 下一步: {next_step}")
    
    # ===== 测试 2: decide_retry =====
    print("\n" + "=" * 60)
    print("测试 2: decide_retry")
    print("=" * 60)
    
    state2 = AgentState(topic="测试", max_results=5)
    
    # 重试3次
    for i in range(4):
        print(f"\n第 {i+1} 次判断:")
        next_step = decide_retry(state2)
        print(f"重试次数: {state2.search_retry_count}/3 → 下一步: {next_step}")
        if next_step == "error":
            break
    
    # ===== 测试 3: decide_after_filter =====
    print("\n" + "=" * 60)
    print("测试 3: decide_after_filter")
    print("=" * 60)
    
    state3 = AgentState(topic="测试", max_results=5)
    
    # 情况1：结果充足
    state3.filtered_results = [{"title": f"结果{i}"} for i in range(5)]
    next_step = decide_after_filter(state3)
    print(f"5条结果 → 下一步: {next_step}")
    
    # 情况2：结果不足
    state3.filtered_results = [{"title": "结果1"}]
    next_step = decide_after_filter(state3)
    print(f"1条结果 → 下一步: {next_step}")
    
    # ===== 测试 4: decide_expand =====
    print("\n" + "=" * 60)
    print("测试 4: decide_expand")
    print("=" * 60)
    
    state4 = AgentState(topic="测试", max_results=10)
    
    # 第1次：未扩大
    print(f"初始 max_results: {state4.max_results}")
    next_step = decide_expand(state4)
    print(f"第1次扩大 → max_results: {state4.max_results}, 下一步: {next_step}")
    
    # 第2次：已扩大
    next_step = decide_expand(state4)
    print(f"第2次扩大 → threshold: {state4.filter_threshold:.2f}, 下一步: {next_step}")
    
    # ===== 测试 5: decide_after_summarize =====
    print("\n" + "=" * 60)
    print("测试 5: decide_after_summarize")
    print("=" * 60)
    
    state5 = AgentState(topic="测试", max_results=5)
    
    # 情况1：质量合格
    state5.quality_score = 0.85
    next_step = decide_after_summarize(state5)
    print(f"质量 0.85 → 下一步: {next_step}")
    
    # 情况2：质量不合格
    state5.quality_score = 0.5
    next_step = decide_after_summarize(state5)
    print(f"质量 0.50 → 下一步: {next_step}")
    
    # ===== 测试 6: decide_regenerate =====
    print("\n" + "=" * 60)
    print("测试 6: decide_regenerate")
    print("=" * 60)
    
    state6 = AgentState(topic="测试", max_results=5)
    
    # 重新生成2次
    for i in range(3):
        print(f"\n第 {i+1} 次判断:")
        next_step = decide_regenerate(state6)
        print(f"重新生成次数: {state6.summary_retry_count}/2 → 下一步: {next_step}")
        if next_step == "format":
            break
    
    # ===== 完成 =====
    print("\n\n" + "=" * 60)
    print("✅ 所有决策函数测试完成！")
    print("=" * 60)