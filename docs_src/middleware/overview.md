# SAGE Middleware 概览

SAGE Middleware 是一个模块化、高性能的中间件层，为SAGE推理框架提供核心基础设施支持。它采用分层架构设计，提供向量增强、流数据处理、神经记忆管理与复杂数据处理能力，兼顾效果、效率和效能。

## 架构概述

SAGE Middleware 采用四层架构设计：

```
┌─────────────────────────────────────────────────────────────┐
│                        应用层 (App)                          │
├─────────────────────────────────────────────────────────────┤
│                     SAGE Middleware                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                    API层                                │ │
│  │  ┌─────────────────┐    ┌─────────────────────────────┐ │ │
│  │  │   抽象服务接口   │    │       计算接口              │ │ │
│  │  │ (Service API)   │    │    (Compute API)           │ │ │
│  │  └─────────────────┘    └─────────────────────────────┘ │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                   服务层                                 │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ │
│  │  │ Memory      │ │   SAGE-DB   │ │      其他服务       │ │ │
│  │  │ Service     │ │   Service   │ │    (扩展中...)      │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                   组件层                                 │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ │
│  │  │   SAGE-DB   │ │  NeuroMem   │ │     向量引擎        │ │ │
│  │  │  (非结构化   │ │ (长期记忆)  │ │   (处理中...)       │ │ │
│  │  │    数据库)   │ │             │ │                     │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │                   硬件层                                 │ │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │ │
│  │  │ GPU 加速    │ │ CXL 内存    │ │    硬件亲和计算     │ │ │
│  │  │ (向量计算)  │ │   后端      │ │       后端          │ │ │
│  │  └─────────────┘ └─────────────┘ └─────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│                        内核层 (Kernel)                       │
└─────────────────────────────────────────────────────────────┘
```

## 核心特性

### 🔌 模块化设计
- **服务解耦**: 每个服务都是独立的微服务，基于 BaseService 实现
- **灵活组合**: 服务可以独立部署、测试和扩展
- **统一接口**: 通过标准化 API 接口进行服务交互

### ⚡ 高性能处理
- **异步通信**: 基于 SAGE 内核的高性能队列机制
- **并发处理**: 支持多线程和分布式处理
- **资源优化**: 智能资源分配和硬件加速

### 🧠 智能记忆
- **多模态存储**: 支持键值、向量、图等多种数据结构
- **记忆编排**: 高级记忆管理和智能检索
- **长期记忆**: 持久化神经记忆存储

### 🌐 分布式支持
- **Ray 集成**: 原生支持 Ray 分布式计算
- **服务发现**: 自动服务注册和发现
- **负载均衡**: 智能负载分配和故障恢复

## 设计理念

### 1. 抽象与实现分离
Middleware 层提供两种类型的 API：
- **抽象服务接口**: 类似 `map_function`，用户必须继承才能自定义服务
- **计算接口**: 如 SAGE Flow，提供可编程的计算接口

### 2. 服务编排模式
采用微服务架构，通过服务编排实现复杂功能：
- **基础服务**: KV、VDB、Graph 等提供底层存储能力
- **编排服务**: Memory Service 等协调基础服务提供高级功能

### 3. 硬件亲和优化
不同组件针对特定硬件进行优化：
- **GPU 加速**: 向量相似度计算优化
- **CXL 内存**: 大容量内存后端支持
- **专用后端**: 为不同硬件提供最优计算后端

## 核心组件

### API 层
- **Service API**: 抽象服务接口定义 (`middleware/api/service_api.md`)
- **Compute API**: 计算接口规范 (开发中)

### 服务层
- **Memory Service**: 记忆编排服务 (`middleware/service/memory/memory_service.md`)
- **SAGE-DB Service**: 数据库服务 (开发中)
- **其他服务**: 可扩展的服务生态

### 组件层
- **SAGE-DB**: 高性能非结构化数据库 (`middleware/components/sage_db.md`)
- **NeuroMem**: 长期记忆存储组件 (`middleware/components/neuromem.md`)
- **SAGE-Flow**: 向量处理引擎 (开发中)

### 硬件层
- **GPU 加速**: 向量计算硬件加速 (`middleware/hardware/gpu_acceleration.md`)
- **CXL 内存**: 大容量内存后端 (开发中)

## 使用场景

### 🔍 智能检索系统
```python
# 使用 Memory Service 进行语义检索
memory_service = env.get_service("memory_service")
results = memory_service.search_memories(
    query="人工智能的发展历史",
    top_k=10
)
```

### 💾 大规模数据存储
```python
# 使用 SAGE-DB 进行高性能存储
sage_db = env.get_service("sage_db_service")
sage_db.index_documents(documents, index_type="HNSW")
```

### 🧠 长期记忆管理
```python
# 使用 NeuroMem 进行记忆管理
neuromem = env.get_service("neuromem_service")
neuromem.store_memory(content, metadata, session_id)
```

## 开发指南

### 服务开发
所有服务必须继承 `BaseService` 类：

```python
from sage.core.api.service.base_service import BaseService

class CustomService(BaseService):
    def _start_service_instance(self):
        # 服务启动逻辑
        pass

    def _stop_service_instance(self):
        # 服务停止逻辑
        pass
```

### 服务注册
在 SAGE 环境中注册服务：

```python
from sage.core.api.local_environment import LocalEnvironment

env = LocalEnvironment("my_app")
env.register_service("custom_service", CustomService, config)
```

### 服务调用
在 Function 中调用服务：

```python
from sage.core.api.function.base_function import BaseFunction

class MyFunction(BaseFunction):
    def process(self, data):
        result = self.call_service["custom_service"].method(data)
        return result
```

## 性能优势

### 🚀 高效通信
- 队列机制比 HTTP 调用提升 **3-5x** 性能
- 内存共享减少数据拷贝开销

### 📊 并发处理
- 支持服务并发处理多个请求
- 智能负载均衡和资源调度

### 🔧 硬件优化
- GPU 加速向量计算提升 **10-100x** 性能
- 专用硬件后端优化特定工作负载

## 监控与运维

### 服务健康检查
```python
# 检查服务状态
health = env.check_service_health("memory_service")
print(f"Service status: {health.status}")
```

### 性能监控
```python
# 获取服务指标
metrics = env.get_service_metrics("memory_service")
print(f"Request count: {metrics.request_count}")
print(f"Average latency: {metrics.avg_latency}ms")
```

## 最佳实践

1. **服务设计**: 保持服务职责单一，接口稳定
2. **错误处理**: 实现完善的错误处理和重试机制
3. **性能优化**: 合理使用缓存和批处理
4. **监控告警**: 建立全面的监控体系
5. **文档维护**: 保持 API 文档与代码同步

SAGE Middleware 为构建现代化的 AI 推理系统提供了强大而灵活的基础设施，助力开发者快速构建高性能、可扩展的智能应用。