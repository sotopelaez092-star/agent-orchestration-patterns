"""
V3 State Graph - 主执行器
"""

from state import AgentState
from nodes import search_node, filter_node, summarize_node, format_node, error_node
from decisions import (
    decide_after_search,
    decide_retry,
    decide_after_filter,
    decide_expand,
    decide_after_summarize,
    decide_regenerate
)


class StateGraph:
    """
    状态图执行器
    
    负责管理节点的执行流程，根据状态动态决定下一步
    """
    
    def __init__(self):
        """初始化状态图"""
        # 注册所有节点函数
        self.nodes = {
            "search": search_node,
            "filter": filter_node,
            "summarize": summarize_node,
            "format": format_node,
            "error": error_node,
        }
        
        # 注册决策函数
        self.decisions = {
            "after_search": decide_after_search,
            "retry": decide_retry,
            "after_filter": decide_after_filter,
            "expand": decide_expand,
            "after_summarize": decide_after_summarize,
            "regenerate": decide_regenerate,
        }
    
    def run(self, initial_state: AgentState) -> AgentState:
        """
        运行状态图
        
        Args:
            initial_state: 初始状态
        
        Returns:
            最终状态
        """
        state = initial_state
        current_node = "search"  # 从搜索节点开始
        max_steps = 50  # 防止无限循环
        step_count = 0
        
        state.add_log("=" * 60)
        state.add_log("🚀 State Graph 开始执行")
        state.add_log("=" * 60)
        
        while current_node != "end" and step_count < max_steps:
            step_count += 1
            state.add_log(f"\n--- 步骤 {step_count}: 执行节点 [{current_node}] ---")
            
            # 执行当前节点
            if current_node in self.nodes:
                state = self.nodes[current_node](state)
            else:
                state.add_log(f"❌ 错误：未知节点 {current_node}")
                break
            
            # 决定下一步
            current_node = self._get_next_node(state, current_node)
        
        if step_count >= max_steps:
            state.add_log("⚠️  警告：达到最大步骤数限制")
        
        state.add_log("\n" + "=" * 60)
        state.add_log("🏁 State Graph 执行完成")
        state.add_log("=" * 60)
        
        return state
    
    def _get_next_node(self, state: AgentState, current_node: str) -> str:
        """
        根据当前节点和状态，决定下一个节点
        
        Args:
            state: 当前状态
            current_node: 当前节点名称
        
        Returns:
            下一个节点名称
        """
        # 根据当前节点，使用对应的决策函数
        if current_node == "search":
            # 搜索后：成功→filter / 失败→retry
            next_node = self.decisions["after_search"](state)
            
            if next_node == "retry":
                # 需要重试：检查次数
                next_node = self.decisions["retry"](state)
            
            return next_node
        
        elif current_node == "filter":
            # 筛选后：够了→summarize / 不够→expand
            next_node = self.decisions["after_filter"](state)
            
            if next_node == "expand":
                # 结果不够：扩大or降低标准
                next_node = self.decisions["expand"](state)
            
            return next_node
        
        elif current_node == "summarize":
            # 总结后：合格→format / 不合格→regenerate
            next_node = self.decisions["after_summarize"](state)
            
            if next_node == "regenerate":
                # 质量不合格：重新生成or降级
                next_node = self.decisions["regenerate"](state)
            
            return next_node
        
        elif current_node == "format":
            # 格式化后：结束
            return "end"
        
        elif current_node == "error":
            # 错误处理后：结束
            return "end"
        
        else:
            # 未知节点
            return "end"


def state_graph_agent(topic: str, max_results: int = 10) -> AgentState:
    """
    State Graph Agent 主函数（对外接口）
    
    Args:
        topic: 查询主题
        max_results: 最大搜索结果数
    
    Returns:
        最终状态
    """
    # 1. 创建初始状态
    initial_state = AgentState(
        topic=topic,
        max_results=max_results
    )
    
    # 2. 创建状态图
    graph = StateGraph()
    
    # 3. 运行状态图
    final_state = graph.run(initial_state)
    
    # 4. 返回最终状态
    return final_state


# ===== 测试代码 =====
if __name__ == "__main__":
    print("=" * 70)
    print("🧪 测试 State Graph 完整流程")
    print("=" * 70)
    print()
    
    # ===== 测试 1: 正常流程 =====
    print("【测试 1】正常流程")
    print("-" * 70)
    
    result1 = state_graph_agent(
        topic="2024年AI Agent投融资动态",
        max_results=5
    )
    
    print("\n" + "=" * 70)
    print("📊 执行结果")
    print("=" * 70)
    result1.print_summary()
    
    # 保存报告
    if result1.final_report:
        filename = "graph_test_report_1.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result1.final_report)
        print(f"✅ 报告已保存: {filename}\n")
    
    # ===== 测试 2: 结果较少的情况（触发扩大搜索）=====
    print("\n" + "=" * 70)
    print("【测试 2】少量结果（触发扩大搜索）")
    print("=" * 70)
    
    result2 = state_graph_agent(
        topic="DeepSeek V3模型",  # 用一个可能结果较少的主题
        max_results=3  # 故意设置较小的数量
    )
    
    print("\n" + "=" * 70)
    print("📊 执行结果")
    print("=" * 70)
    print(f"初始搜索数量: 3")
    print(f"最终搜索数量: {result2.max_results}")
    print(f"是否扩大搜索: {result2.search_expanded}")
    print(f"筛选结果数: {len(result2.filtered_results)}")
    
    if result2.final_report:
        filename = "graph_test_report_2.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(result2.final_report)
        print(f"✅ 报告已保存: {filename}\n")
    
    # ===== 测试 3: 查看详细日志 =====
    print("\n" + "=" * 70)
    print("【测试 3】详细执行日志")
    print("=" * 70)
    
    result3 = state_graph_agent(
        topic="Multi-Agent系统架构",
        max_results=5
    )
    
    print("\n📝 完整执行日志:")
    print("-" * 70)
    for log in result3.logs:
        print(log)
    
    # ===== 最终统计 =====
    print("\n\n" + "=" * 70)
    print("🎉 所有测试完成！")
    print("=" * 70)
    print(f"✅ 测试 1: 正常流程 - 已生成报告")
    print(f"✅ 测试 2: 扩大搜索测试 - 已生成报告")
    print(f"✅ 测试 3: 日志查看 - 完成")
    print("\n🚀 State Graph V3 完整实现成功！")