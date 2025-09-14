# Profile 组件设计文档

!!! note "定位"
    **Profile** 是 Agent 的“身份卡片”，定义了它的 **角色、目标、任务、背景** 等信息。  
    它是整个 Agent 框架的 **认知入口**，所有推理、规划、行动都基于 Profile 提供的上下文。

---

## 1. 设计目标

- **标准化身份**：为 Agent 提供统一的“自我定义”接口。
- **灵活配置**：支持最小化配置（仅 name + role），也支持扩展（goals、tasks、backstory、language）。
- **可渲染提示词**：能够生成系统提示（system prompt），直接交给 LLM 使用。
- **可扩展性**：方便未来添加新字段（如 persona、capabilities、constraints）。

---

## 2. 数据模型

```python title="profile.py"
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class BaseProfile:
    name: str
    role: str
    goals: List[str] = field(default_factory=list)
    tasks: List[str] = field(default_factory=list)
    backstory: Optional[str] = None
    language: str = "en"

    def render_system_prompt(self) -> str:
        prompt = f"You are {self.name}, acting as {self.role}.\n"
        if self.goals:
            prompt += f"Your goals: {', '.join(self.goals)}.\n"
        if self.tasks:
            prompt += f"Current tasks: {', '.join(self.tasks)}.\n"
        if self.backstory:
            prompt += f"Background: {self.backstory}\n"
        prompt += f"Reply in {self.language}."
        return prompt
```

!!! tip "最小示例"
    ```python
    profile = BaseProfile(
        name="ResearchAgent",
        role="AI Research Assistant"
    )
    print(profile.render_system_prompt())
    ```

---

## 3. 字段说明

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `name` | str | ✅ | Agent 的名称（唯一标识）。 |
| `role` | str | ✅ | Agent 的角色（如 "planner", "analyst", "developer"）。 |
| `goals` | List[str] | ❌ | 长期目标列表。 |
| `tasks` | List[str] | ❌ | 当前正在执行的任务。 |
| `backstory` | str | ❌ | 人格背景/故事描述。 |
| `language` | str | ❌ | 输出语言（默认 `"en"`）。 |

---

## 4. 渲染结果示例

=== "最小配置"
```text
You are ResearchAgent, acting as AI Research Assistant.
Reply in en.
```

=== "完整配置"
```text
You are ResearchAnalyst, acting as planner.
Your goals: analyze literature, summarize insights.
Current tasks: find recent LLM agent survey, generate structured summary.
Background: You were trained as a research assistant focusing on NLP and multi-agent systems.
Reply in zh.
```
