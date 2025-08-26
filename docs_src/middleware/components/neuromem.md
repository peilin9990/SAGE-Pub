# Neuromem（长期记忆组件）

Neuromem 是长期记忆（Long-term Memory）的组件实现，Memory Service 即由 Neuromem 对外提供服务封装。业务侧统一通过 Service API 调用 memory_service 完成写入与检索，无需直接依赖 Neuromem 的内部实现。

- 代码位置（组件/服务）：packages/sage-middleware/src/sage/middleware/services/memory/ 与其子模块
- 与服务的关系：Memory Service = Neuromem 的服务化封装；Function 中通过 self.call_service["memory_service"] 调用

本页包含：
- 服务示例（如何在 Function 中调用由 Neuromem 提供的 Memory Service）
- 组件设计（Neuromem 的核心分层与关键子模块）
- 部分组件层 API（按模块粒度与稳定调用面汇总）

---

## 一、服务示例（面向使用者）

在环境里注册 Memory Service（由工厂函数返回服务实例），然后在 Function 中进行存取与检索。示例接口与调用风格与仓库保持一致。

```python
# 环境侧：注册服务（可按需在工厂内初始化集合等）
from sage.core.api.local_environment import LocalEnvironment
from sage.middleware.services.memory import MemoryService  # 以仓库 README 示例为准

def memory_service_factory():
    service = MemoryService()
    # 可选：初始化集合（示例出现在仓库 README）
    # service.create_collection(
    #     name="qa_collection",
    #     backend_type="VDB",
    #     description="QA pipeline memory"
    # )
    return service

env = LocalEnvironment("neuromem_demo")
env.register_service("memory_service", memory_service_factory)
```

```python
# Function 侧：通过 Service API 访问 Memory Service
from sage.core.api.function.base_function import BaseFunction

class ConversationMemory(BaseFunction):
    def execute(self, data):
        session_id = data.get("session_id", "default")
        content = data.get("content", "")
        vector = data.get("vector")

        # 1) 写入长期记忆（由 Neuromem 组件承载）
        memory_id = self.call_service["memory_service"].store_memory(
            content=content,
            vector=vector,
            session_id=session_id,
            memory_type="conversation",
            metadata={"source": "user_input"}
        )

        # 2) 相似检索（方法名以实现为准，示例与仓库示例一致）
        # 注意：参数命名在不同实现中可能为 top_k 或 limit
        results = self.call_service["memory_service"].search_memories(
            query_vector=vector,
            session_id=session_id,
            limit=5
        )

        return {"memory_id": memory_id, "related": results}
```

要点：
- Function/Service 中统一使用 self.call_service / self.call_service_async 访问
- Memory Service 对接向量（VDB）、KV、Graph 等后端，Function 无需关心内部细节

---

## 二、组件设计（Neuromem 内部分层与职责）

Neuromem 采用“编排服务 + 基础集合 + 引擎/后端”的分层方式实现，支持在服务层提供稳定能力，同时允许组件层按需替换底层后端。

```mermaid
flowchart TB
  App[调用方：Function/Service]
  MS[Memory Service（服务封装）]
  subgraph Neuromem[Neuromem 组件]
    MM[MemoryManager\n(核心管理/路由)]
    subgraph Collections[Memory Collection 层]
      BC[base_collection.py\n（基础抽象）]
      KVC[kv_collection.py]
      VDBC[vdb_collection.py]
      GC[graph_collection.py]
    end
    subgraph Engines[引擎/后端适配]
      MD[storage_engine/metadata_storage.py]
      GI[search_engine/graph_index/]
      HI[search_engine/hybrid_index/]
      KV[kv（在对应服务中实现）]
      VDB[vdb（在对应服务中实现）]
    end
  end
  Stores[实际后端：KV / VDB / Graph 等]

  App --> MS --> Neuromem
  Neuromem --> Stores

  MM --> Collections
  Collections --> Engines
```

- MemoryManager（memory_manager.py）
  - 统一管理写入/检索的流程编排，将请求路由到对应集合/后端
- Memory Collection 层（memory_collection/）
  - base_collection.py：集合抽象基类
  - kv_collection.py / vdb_collection.py / graph_collection.py：面向不同后端的集合实现
- 引擎/后端适配（storage_engine/ 与 search_engine/）
  - metadata_storage.py：元数据存储
  - graph_index/、hybrid_index/：图与混合检索相关索引
  - 与 KV/VDB 的落地引擎迁移到了各自服务模块（遵循单一职责）
    - 在 Memory Service 中仅保留“编排与抽象”
    - KV/VDB 具体存储与索引在 kv/vdb 服务中实现

---

## 三、部分组件层 API（按模块粒度汇总）

说明：
- 下列为稳定“面向组件”的职责/接口面向，尽量避免硬编码具体签名；以仓库实际实现为准
- 对上统一通过 Memory Service 的服务接口（store_memory/search_memories 等）

1) Memory Service（服务层，对上暴露）
- 常用方法（依据仓库示例）
  - store_memory(content, vector, session_id, memory_type, metadata)
  - search_memories(query_vector, session_id, limit/top_k, filters)
  - retrieve_memories(...)（如实现提供）
- 作用：将 Neuromem 的能力服务化，屏蔽 KV/VDB/Graph 的细节

2) MemoryManager（组件核心）
- 职责：解析写入/检索请求，将其分发到合适的 Collection 与后端
- 行为：维护集合/索引/元数据一致性；聚合后端结果

3) Collections（memory_collection/）
- base_collection.py：集合抽象（提供集合级能力的统一接口）
- kv_collection.py / vdb_collection.py / graph_collection.py：不同后端集合的适配器
- 典型行为：集合创建/加载、集合内对象/向量读写、索引/检索委托

4) Engines（storage_engine/ 与 search_engine/）
- metadata_storage.py：元数据读写
- graph_index/、hybrid_index/：图与混合检索索引能力
- 与 KV/VDB 的具体存储/检索引擎在各自服务模块维护

---

## 四、实践建议

- 编程模型：只在 Function/Service 中调用 memory_service；组件内部细节交由 Neuromem 处理
- 性能：大批量写入/检索时优先使用批接口（若实现提供）；避免在 execute 中过细粒度频繁阻塞
- 可测试性：可在环境内注册 Mock 服务，利用相同 Service API 验证业务逻辑