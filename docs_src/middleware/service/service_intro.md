# SAGE Middleware 服务层概览

服务层是 SAGE Middleware 的核心组件，提供预定义的微服务，通过编排各种组件形成完整的服务逻辑，向上层应用提供统一的服务接口。服务层采用微服务架构设计，支持独立部署、扩展和管理。

## 服务分层模型

```mermaid
flowchart TB
  subgraph App[应用层 (Function & Operator)]
  end

  subgraph Orchestration[服务编排层]
    MemorySvc[Memory Service]
    Future1[Future Services]
    Future2[Future Services]
  end

  subgraph Foundation[基础服务层]
    KV[KV Service]
    VDB[VDB Service]
    Graph[Graph Service]
    NeuroMem[NeuroMem Service]
  end

  subgraph Components[组件层]
    Engines[Storage Engines & Processing Units]
  end

  App --> Orchestration --> Foundation --> Components
```

## 服务类型

- 基础服务（Foundation Services）：KV/VDB/Graph 等
- 编排服务（Orchestration Services）：例如 Memory Service
- 专用服务（Specialized Services）：如 NeuroMem Service

## 服务通信与调用（与仓库接口一致）

- 在 BaseFunction/BaseService 中，通过 self.call_service["service_name"].method(...) 调用同步服务
- 通过 self.call_service_async["service_name"].method(...) 发起异步调用（返回 future）

更多示例，请参考“服务快速入门”。
