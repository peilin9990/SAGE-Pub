# Memory 组件设计文档

!!! note "定位"
    **Memory** 是 Agent 的“记忆系统”，负责存储、检索和管理交互过程中的信息。它为 Agent 提供“短期工作记忆”、“长期语义记忆”和“情节记忆”的能力，支持上下文保持、跨会话关联和知识沉淀。

---

## 1. 设计目标

- **统一接口**：抽象出高级 API，屏蔽底层 KV / VDB / Graph 的差异。
- **多模存储**：同时支持键值存储、向量数据库、知识图谱。
- **可扩展性**：允许替换 ChromaDB、Milvus 等不同 VDB 实现。
- **增强检索**：结合语义相似度、元数据过滤、知识图谱上下文。
- **上下文记忆**：支持 session 级别的短期记忆，跨 session 的长期记忆。

---

## 2. 数据模型

```python title="memory/schema.py"
from typing import Literal, Dict, Any, Optional

# 记忆类别
MemoryKind = Literal["working", "episodic", "semantic"]

class MemoryRecord(Dict[str, Any]):
    id: str            # 记忆唯一ID
    content: str       # 文本内容
    vector: Optional[list[float]]
    kind: MemoryKind   # 记忆类型
    metadata: Dict[str, Any]
    timestamp: float
```

---

## 3. 核心接口

```python title="memory/service.py"
class MemoryService(BaseService):
    """
    记忆编排服务：统一管理 KV / VDB / Graph
    """

    def store_memory(self, content: str, vector: list[float], **kwargs) -> str:
        """存储一条记忆，返回 memory_id"""

    def search_memories(self, query_vector: list[float], **kwargs) -> list[MemoryRecord]:
        """基于向量检索相关记忆"""

    def get_memory(self, memory_id: str) -> Optional[MemoryRecord]:
        """获取指定记忆"""

    def delete_memory(self, memory_id: str) -> bool:
        """删除指定记忆"""

    def get_session_memories(self, session_id: str, **kwargs) -> dict:
        """获取某一会话下的全部记忆"""

    def stats(self) -> dict:
        """获取底层存储和服务的统计信息"""
```

---

## 4. 记忆存储类型

| 类型 | 描述 | 使用场景 |
|------|------|----------|
| `working` | 短期工作记忆 | 对话上下文、当前任务 | 
| `episodic` | 情节记忆 | 单次交互中的事件记录 | 
| `semantic` | 长期语义记忆 | 知识库、经验总结 | 

---

## 5. 典型流程

### 存储记忆
```python
memory_id = memory_service.store_memory(
    content="用户问了：什么是RAG？",
    vector=embed("什么是RAG？"),
    session_id="sess-123",
    memory_type="conversation",
    metadata={"source": "chat"},
    create_knowledge_graph=True,
)
```

### 检索记忆
```python
results = memory_service.search_memories(
    query_vector=embed("RAG系统架构"),
    session_id="sess-123",
    limit=5,
    similarity_threshold=0.2,
    include_graph_context=True,
)
```

### 获取会话记忆
```python
session_data = memory_service.get_session_memories(
    session_id="sess-123",
    memory_type="conversation",
    limit=20,
    include_graph_analysis=True,
)
```

---

## 6. 与 Agent 的关系

!!! tip "用法"
    - 在 **Planner** 生成计划时，可从 Memory 中检索相关上下文。
    - 在 **Action** 执行完工具调用后，可以将结果写入 Memory。
    - 在 **Profile** 中的 goals、tasks 也可以通过 Memory 进行持久化。

---

## 7. 扩展方向

- **跨模态记忆**：支持图像/音频 embedding 存储。
- **时间衰减机制**：对旧记忆设置权重衰减。
- **层级记忆**：结合 STM（短时）、LTM（长时）、DCM（决策）架构。
- **RAG 集成**：直接把 Memory 作为 RAG 检索器的数据源。