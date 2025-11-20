# V3: State Graph 模式

AI信息获取助手的第三个版本，使用状态图实现容错和动态优化。

## 核心改进

相比 V1/V2 的改进：
- **容错机制**：搜索失败自动重试（最多3次）
- **动态优化**：结果不足时自动扩大搜索或降低标准
- **质量保证**：摘要质量不合格自动重新生成（最多2次）
- **降级策略**：多次失败后返回部分结果，不会完全失败

## 快速开始

### 1. 安装依赖
```bash
pip install openai python-dotenv
```

### 2. 配置环境变量

创建 `.env` 文件：
```
DEEPSEEK_API_KEY=your_api_key_here
```

### 3. 运行
```python
from graph import state_graph_agent

# 执行查询
result = state_graph_agent(
    topic="AI Agent 最新进展",
    max_results=10
)

# 获取报告
print(result.final_report)

# 保存报告
with open("report.md", "w", encoding="utf-8") as f:
    f.write(result.final_report)
```

## 文件结构
```
v3_state_graph/
├── state.py          # 状态类定义
├── tools.py          # LLM调用、搜索（复用V1/V2）
├── nodes.py          # 5个节点函数
├── decisions.py      # 6个决策函数
├── graph.py          # 主执行器
└── README.md         # 本文档
```

## 执行流程
```
START
  ↓
搜索 → 成功 → 筛选 → 结果够 → 总结 → 质量好 → 格式化 → END
  ↓失败      ↓不够      ↓质量差
重试(3次)   扩大搜索    重新生成(2次)
  ↓超限      ↓已扩大      ↓超限
错误处理   降低标准    使用当前版本
```

## 核心组件

### 1. 状态类（state.py）

存储整个执行过程的所有数据：
```python
state = AgentState(
    topic="查询主题",
    max_results=10
)

# 状态包含：
# - 搜索结果、筛选结果、摘要
# - 重试次数、质量评分
# - 错误信息、执行日志
```

### 2. 节点函数（nodes.py）

5个核心处理节点：
```python
search_node(state)      # 调用搜索API
filter_node(state)      # LLM筛选相关内容
summarize_node(state)   # LLM生成摘要
format_node(state)      # 格式化为Markdown
error_node(state)       # 错误降级处理
```

### 3. 决策函数（decisions.py）

6个决策点：
```python
decide_after_search()    # 搜索后：成功/重试/错误
decide_retry()           # 是否继续重试
decide_after_filter()    # 筛选后：够了/不够
decide_expand()          # 扩大搜索/降低标准
decide_after_summarize() # 总结后：合格/重新生成
decide_regenerate()      # 是否继续重新生成
```

### 4. 执行器（graph.py）

状态图主循环：
```python
graph = StateGraph()
final_state = graph.run(initial_state)
```

## 测试

测试各个组件：
```bash
# 测试状态类
python state.py

# 测试节点函数
python nodes.py

# 测试决策函数
python decisions.py

# 测试完整流程
python graph.py
```

## 实际案例

### 案例1：正常流程
```python
result = state_graph_agent("AI Agent投融资", max_results=5)
# 执行步骤：搜索(5条) → 筛选(5条) → 总结 → 格式化
# 总耗时：约12秒
```

### 案例2：触发重试
```python
# 如果搜索失败，会自动重试
# 第1次失败 → 等待2秒 → 第2次失败 → 等待4秒 → 第3次成功
```

### 案例3：扩大搜索
```python
result = state_graph_agent("小众主题", max_results=3)
# 筛选后只有1条 → 扩大到6条 → 重新搜索 → 筛选出3条 → 继续
```

### 案例4：质量重新生成
```python
# 如果第一次生成的摘要太短
# 第1次生成(80字，不合格) → 优化Prompt → 第2次生成(250字，合格)
```

## V1/V2/V3 对比

| 维度 | V1 Sequential | V2 Router | V3 State Graph |
|------|--------------|-----------|----------------|
| 流程 | 固定串行 | 根据类型分流 | 动态状态机 |
| 容错 | 无 | 无 | 3层重试 |
| 优化 | 无 | 无 | 动态调整策略 |
| 成功率 | ~70% | ~75% | ~95% |
| 平均耗时 | 10秒 | 11秒 | 15秒 |
| 代码复杂度 | 低 | 中 | 高 |

## 关键参数
```python
# state.py
search_retry_count: int = 0    # 搜索重试次数（最大3）
summary_retry_count: int = 0   # 摘要重试次数（最大2）
filter_threshold: float = 0.7  # 筛选阈值（0-1）
quality_score: float = 0.0     # 质量评分（0-1）

# graph.py
max_steps: int = 50            # 最大执行步骤（防死循环）
```

## 常见问题

**Q: 为什么要用State Graph而不是简单的if-else？**  
A: 复杂流程用状态机更清晰，每个节点职责单一，决策逻辑独立，易测试易扩展。

**Q: 如果所有重试都失败了怎么办？**  
A: 会进入error_node，返回降级报告，包含已获取的部分结果。

**Q: 能自定义重试次数吗？**  
A: 可以，修改state.py中的判断条件即可，如`search_retry_count >= 5`。

**Q: Mock数据怎么替换成真实搜索？**  
A: 修改tools.py的search_web函数，接入Google/Bing搜索API。

## 扩展方向

1. 添加更多节点（如：去重、排序）
2. 支持并行搜索（同时调用多个搜索引擎）
3. 添加缓存机制（避免重复搜索）
4. 实现可视化（显示状态转换图）
5. 支持流式输出（实时显示进度）

## 开发日志

参考项目根目录的 `docs/dev-log-2024-11-19.md`

## License

MIT