"""
V3 State Graph - 状态类定义
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class AgentState:
    """
    Agent 状态类 - 完整版
    
    这个类存储了 Agent 执行过程中的所有状态信息，
    每个节点都可以读取和修改这个状态。
    """
    
    # ===== 用户输入 =====
    topic: str                          # 用户查询的主题
    max_results: int = 10              # 最大搜索结果数
    
    # ===== 当前状态 =====
    current_step: str = "start"        # 当前所在的节点名称
    
    # ===== 搜索阶段 =====
    search_results: List[Dict[str, Any]] = field(default_factory=list)  # 搜索结果
    search_status: str = "pending"     # 搜索状态: pending/success/failed
    search_retry_count: int = 0        # 搜索重试次数
    search_expanded: bool = False      # 是否已扩大搜索范围
    
    # ===== 筛选阶段 =====
    filtered_results: List[Dict[str, Any]] = field(default_factory=list)  # 筛选后的结果
    filter_threshold: float = 0.7      # 筛选阈值（0-1，越高越严格）
    filter_lowered: bool = False       # 是否已降低筛选标准
    
    # ===== 总结阶段 =====
    summary: str = ""                  # LLM生成的摘要
    summary_retry_count: int = 0       # 摘要重试次数
    quality_score: float = 0.0         # 质量评分（0-1）
    
    # ===== 最终输出 =====
    final_report: str = ""             # 格式化后的Markdown报告
    
    # ===== 错误处理 =====
    error: Optional[str] = None        # 错误信息
    
    # ===== 日志 =====
    logs: List[str] = field(default_factory=list)  # 操作日志列表
    
    def add_log(self, message: str) -> None:
        """
        添加日志
        
        Args:
            message: 日志内容
        """
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.logs.append(log_entry)
        print(log_entry)
    
    # ===== 辅助方法：判断条件 =====
    
    def is_search_retry_limit_reached(self) -> bool:
        """检查搜索重试是否达到上限（3次）"""
        return self.search_retry_count >= 3
    
    def is_summary_retry_limit_reached(self) -> bool:
        """检查摘要重试是否达到上限（2次）"""
        return self.summary_retry_count >= 2
    
    def has_enough_filtered_results(self, min_count: int = 3) -> bool:
        """
        检查筛选结果是否足够
        
        Args:
            min_count: 最小结果数，默认3条
        """
        return len(self.filtered_results) >= min_count
    
    def is_quality_acceptable(self, min_score: float = 0.7) -> bool:
        """
        检查摘要质量是否合格
        
        Args:
            min_score: 最低质量分数，默认0.7
        """
        return self.quality_score >= min_score
    
    # ===== 辅助方法：状态管理 =====
    
    def increment_search_retry(self) -> None:
        """增加搜索重试次数"""
        self.search_retry_count += 1
        self.add_log(f"搜索重试 {self.search_retry_count}/3")
    
    def increment_summary_retry(self) -> None:
        """增加摘要重试次数"""
        self.summary_retry_count += 1
        self.add_log(f"摘要重新生成 {self.summary_retry_count}/2")
    
    def expand_search(self) -> None:
        """扩大搜索范围"""
        self.max_results *= 2
        self.search_expanded = True
        self.add_log(f"扩大搜索范围至 {self.max_results} 条")
    
    def lower_filter_threshold(self) -> None:
        """降低筛选标准"""
        self.filter_threshold *= 0.8
        self.filter_lowered = True
        self.add_log(f"降低筛选阈值至 {self.filter_threshold:.2f}")
    
    def set_error(self, error_message: str) -> None:
        """
        设置错误信息
        
        Args:
            error_message: 错误描述
        """
        self.error = error_message
        self.add_log(f"❌ 错误: {error_message}")
    
    # ===== 辅助方法：状态摘要 =====
    
    def get_summary(self) -> Dict[str, Any]:
        """
        获取状态摘要（用于调试和监控）
        
        Returns:
            包含关键状态信息的字典
        """
        return {
            "topic": self.topic,
            "current_step": self.current_step,
            "search_status": self.search_status,
            "search_retry_count": self.search_retry_count,
            "search_results_count": len(self.search_results),
            "filtered_results_count": len(self.filtered_results),
            "summary_length": len(self.summary),
            "quality_score": self.quality_score,
            "has_error": self.error is not None,
        }
    
    def print_summary(self) -> None:
        """打印状态摘要"""
        print("\n" + "="*50)
        print("📊 当前状态摘要")
        print("="*50)
        summary = self.get_summary()
        for key, value in summary.items():
            print(f"{key:.<30} {value}")
        print("="*50 + "\n")


# 测试代码
if __name__ == "__main__":
    print("=== 测试 AgentState（完整版）===\n")
    
    # 1. 创建状态
    state = AgentState(topic="AI Agent 最新资讯", max_results=10)
    state.add_log("初始化状态")
    
    # 2. 模拟搜索
    state.current_step = "search"
    state.search_results = [
        {"title": "新闻1", "url": "url1", "snippet": "内容1"},
        {"title": "新闻2", "url": "url2", "snippet": "内容2"},
    ]
    state.search_status = "success"
    state.add_log("搜索完成，获取2条结果")
    
    # 3. 测试重试机制
    print("\n--- 测试搜索重试 ---")
    print(f"重试次数: {state.search_retry_count}")
    print(f"是否达到上限: {state.is_search_retry_limit_reached()}")
    
    state.increment_search_retry()
    state.increment_search_retry()
    state.increment_search_retry()
    print(f"重试次数: {state.search_retry_count}")
    print(f"是否达到上限: {state.is_search_retry_limit_reached()}")
    
    # 4. 测试筛选
    print("\n--- 测试筛选结果 ---")
    state.filtered_results = [{"title": "相关1"}, {"title": "相关2"}]
    print(f"筛选结果数: {len(state.filtered_results)}")
    print(f"结果是否足够: {state.has_enough_filtered_results()}")
    
    # 5. 测试扩大搜索
    print("\n--- 测试扩大搜索 ---")
    print(f"扩大前: max_results={state.max_results}")
    state.expand_search()
    print(f"扩大后: max_results={state.max_results}")
    
    # 6. 测试质量检查
    print("\n--- 测试质量检查 ---")
    state.quality_score = 0.85
    print(f"质量分数: {state.quality_score}")
    print(f"是否合格: {state.is_quality_acceptable()}")
    
    # 7. 测试错误处理
    print("\n--- 测试错误处理 ---")
    state.set_error("网络连接失败")
    print(f"错误信息: {state.error}")
    
    # 8. 打印最终摘要
    state.print_summary()
    
    # 9. 显示所有日志
    print("\n📝 完整日志：")
    for log in state.logs:
        print(log)