# 中间件服务快速入门

本文档介绍如何使用 SAGE 中间件服务，包括内存服务、向量数据库服务等核心组件的使用方法。

---

## 🎯 核心概念

SAGE 中间件层提供了一套完整的服务体系，用于支撑上层应用的数据存储、检索和处理需求：

- **内存服务（Memory Service）**：提供统一的记忆管理和编排
- **向量数据库服务（VDB Service）**：高效的向量存储和检索
- **键值存储服务（KV Service）**：快速的键值对存储
- **图数据库服务（Graph Service）**：知识图谱和关系数据管理

---

## 🚀 内存服务使用示例

### 在环境中注册服务

```python
from sage.core.api.local_environment import LocalEnvironment
from sage.middleware.services.memory import MemoryService

def memory_service_factory():
    """内存服务工厂函数"""
    service = MemoryService()
    # 可选：在此初始化集合和配置
    return service

# 创建环境并注册服务
env = LocalEnvironment("memory_service_demo")
env.register_service("memory_service", memory_service_factory)
```

### 在Function中使用服务

```python
from sage.core.api.function.map_function import MapFunction

class ConversationMemory(MapFunction):
    """对话记忆处理器"""
    def execute(self, data):
        session_id = data.get("session_id", "default")
        content = data.get("content", "")
        
        # 模拟向量（实际应用中使用真实embedding）
        import random
        vector = [random.random() for _ in range(384)]

        # 通过call_service访问内存服务
        memory_service = self.call_service["memory_service"]
        
        # 存储记忆
        memory_id = memory_service.store_memory(
            content=content,
            vector=vector,
            session_id=session_id,
            memory_type="conversation",
            metadata={"source": "user_input", "timestamp": "2024-01-01"}
        )

        # 检索相关记忆
        related_memories = memory_service.search_memories(
            query_vector=vector,
            session_id=session_id,
            limit=5
        )
        
        return {
            "memory_id": memory_id,
            "related_memories": related_memories,
            "original_data": data
        }
```

### 完整的处理流水线

```python
from sage.core.api.function.batch_function import BatchFunction

class ConversationBatch(BatchFunction):
    """对话数据源"""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.conversations = [
            {"session_id": "user_001", "content": "你好，我想了解机器学习"},
            {"session_id": "user_001", "content": "深度学习和机器学习有什么区别？"},
            {"session_id": "user_002", "content": "Python编程有什么特点？"},
            {"session_id": "user_001", "content": "谢谢你的解答"}
        ]
        self.counter = 0
    
    def execute(self):
        if self.counter >= len(self.conversations):
            return None
        conv = self.conversations[self.counter]
        self.counter += 1
        return conv

def memory_pipeline_example():
    """内存服务流水线示例"""
    env = LocalEnvironment("memory_pipeline")
    
    # 注册内存服务
    env.register_service("memory_service", MemoryService)
    
    # 构建处理流水线
    (env
        .from_batch(ConversationBatch, {})
        .map(ConversationMemory)
        .sink(lambda data: print(f"✅ 处理完成: 存储记忆 {data['memory_id']}, 找到 {len(data['related_memories'])} 条相关记忆"))
    )
    
    env.submit(autostop=True)
    print("📊 内存服务测试完成")

if __name__ == "__main__":
    memory_pipeline_example()
```

---

## 🗄️ NeuroMem 服务使用

### 基础 NeuroMem 操作

```python
"""
NeuroMem 长期记忆服务示例
演示如何使用 NeuroMem 进行向量存储和检索
"""
from sage.middleware.services.neuromem.memory_service import MemoryService as NeuroMemService
from sage.middleware.utils.embedding.embedding_api import apply_embedding_model

def neuromem_basic_example():
    """NeuroMem 基础使用示例"""
    
    # 创建NeuroMem服务
    neuromem_service = NeuroMemService()
    
    # 初始化嵌入模型
    embedding_model = apply_embedding_model("default")
    
    # 创建集合
    collection = neuromem_service.manager.create_collection(
        name="test_knowledge",
        backend_type="VDB",
        description="测试知识库",
        embedding_model=embedding_model,
        dim=embedding_model.get_dim()
    )
    
    # 添加元数据字段
    collection.add_metadata_field("category")
    collection.add_metadata_field("source")
    
    # 插入数据
    documents = [
        {"text": "Python是一种解释型编程语言", "metadata": {"category": "programming", "source": "tutorial"}},
        {"text": "机器学习是人工智能的子领域", "metadata": {"category": "ai", "source": "textbook"}},
        {"text": "深度学习使用神经网络进行学习", "metadata": {"category": "ai", "source": "paper"}},
    ]
    
    for doc in documents:
        collection.insert(doc["text"], doc["metadata"])
    
    # 创建索引
    collection.create_index("global_index")
    collection.create_index("ai_index", metadata_filter_func=lambda m: m.get("category") == "ai")
    
    # 检索测试
    results = collection.retrieve("什么是机器学习？", topk=2, index_name="ai_index")
    
    print("🔍 检索结果:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.get('text', 'N/A')}")
        print(f"     相似度: {result.get('similarity', 'N/A'):.3f}")
    
    # 持久化存储
    neuromem_service.manager.store_collection()
    print(f"💾 数据已保存到: {neuromem_service.manager.data_dir}")

if __name__ == "__main__":
    neuromem_basic_example()
```

### 在流水线中使用 NeuroMem

```python
from sage.core.api.function.map_function import MapFunction
from sage.core.api.function.batch_function import BatchFunction

class NeuroMemProcessor(MapFunction):
    """NeuroMem处理器"""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.collection_name = config.get("collection_name", "knowledge_base")
    
    def execute(self, data):
        # 获取NeuroMem服务
        neuromem_service = self.call_service["neuromem_service"]
        
        # 根据操作类型处理
        if data.get("operation") == "insert":
            # 插入数据
            result = neuromem_service.insert_data(
                collection_name=self.collection_name,
                text=data["text"],
                metadata=data.get("metadata", {})
            )
            print(f"📝 插入数据: {data['text'][:30]}...")
        
        elif data.get("operation") == "retrieve":
            # 检索数据
            results = neuromem_service.retrieve_data(
                collection_name=self.collection_name,
                query_text=data["text"],
                topk=data.get("topk", 3)
            )
            data["results"] = results.get("results", []) if results.get("status") == "success" else []
            print(f"🔍 检索查询: {data['text']}")
            print(f"   找到 {len(data['results'])} 条结果")
        
        return data

def neuromem_pipeline_example():
    """NeuroMem流水线示例"""
    env = LocalEnvironment("neuromem_pipeline")
    
    # 注册NeuroMem服务
    def neuromem_service_factory():
        from sage.middleware.services.neuromem.memory_service import MemoryService
        return MemoryService()
    
    env.register_service("neuromem_service", neuromem_service_factory)
    
    # 测试数据
    class NeuroMemBatch(BatchFunction):
        def __init__(self, config, **kwargs):
            super().__init__(**kwargs)
            self.operations = [
                {"operation": "insert", "text": "Python是一种编程语言", "metadata": {"type": "definition"}},
                {"operation": "insert", "text": "机器学习用于数据分析", "metadata": {"type": "definition"}},
                {"operation": "retrieve", "text": "编程语言有哪些？", "topk": 2},
                {"operation": "retrieve", "text": "什么是机器学习？", "topk": 2}
            ]
            self.counter = 0
        
        def execute(self):
            if self.counter >= len(self.operations):
                return None
            op = self.operations[self.counter]
            self.counter += 1
            return op
    
    config = {"processor": {"collection_name": "test_collection"}}
    
    (env
        .from_batch(NeuroMemBatch, {})
        .map(NeuroMemProcessor, config["processor"])
        .sink(lambda data: print(f"✅ 操作完成: {data['operation']}"))
    )
    
    env.submit(autostop=True)

if __name__ == "__main__":
    neuromem_pipeline_example()
```

---

## 🔧 高级配置和最佳实践

### 工厂模式注册服务

```python
from sage.middleware.services.memory import create_memory_service_factory

def advanced_service_registration():
    """高级服务注册示例"""
    env = LocalEnvironment("advanced_services")
    
    # 使用工厂函数注册Memory服务
    memory_factory = create_memory_service_factory(
        service_name="memory_service",
        kv_service_name="kv_service",
        vdb_service_name="vdb_service",
        default_vector_dimension=384,
        enable_knowledge_graph=True
    )
    
    env.register_service_factory("memory_service", memory_factory)
    
    print("✅ 高级服务注册完成")

if __name__ == "__main__":
    advanced_service_registration()
```

### 错误处理和监控

```python
class RobustMemoryProcessor(MapFunction):
    """带错误处理的内存处理器"""
    def execute(self, data):
        try:
            memory_service = self.call_service["memory_service"]
            
            # 模拟向量
            import random
            vector = [random.random() for _ in range(384)]
            
            # 执行内存操作
            result = memory_service.store_memory(
                content=data.get("content", ""),
                vector=vector,
                metadata=data.get("metadata", {})
            )
            
            data["memory_id"] = result
            return data
            
        except Exception as e:
            self.logger.error(f"内存操作失败: {e}")
            data["error"] = str(e)
            return data
```

### 配置文件示例

```yaml
# service_config.yaml
memory_service:
  kv_service_name: "kv_service"
  vdb_service_name: "vdb_service"
  graph_service_name: "graph_service"
  default_vector_dimension: 384
  max_search_results: 50
  enable_caching: true
  enable_knowledge_graph: true

neuromem_service:
  data_dir: "./neuromem_data"
  collection_config:
    default_embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
    default_dimension: 384
    index_type: "HNSW"
```

---

## 📊 性能优化建议

### 1. 批量操作
- 避免在循环中频繁调用服务
- 使用批量接口进行大量数据操作
- 合理控制批次大小

### 2. 向量维度优化
```python
# 根据需求选择合适的向量维度
embedding_model = apply_embedding_model("default", dimension=256)  # 更小的维度提升性能
```

### 3. 索引策略
```python
# 创建针对性索引提升检索性能
collection.create_index(
    "filtered_index",
    metadata_filter_func=lambda m: m.get("type") == "important"
)
```

---

## 🚀 快速开始步骤

1. **选择服务**：根据应用需求选择合适的中间件服务
2. **注册服务**：在环境中注册所需服务
3. **实现处理器**：在Function中使用 `self.call_service` 访问服务
4. **构建流水线**：组合数据源、处理器和输出
5. **运行测试**：验证服务功能是否正常

### 核心要点

- 使用 `env.register_service(name, factory_function)` 注册服务
- 工厂函数在服务首次使用时被调用，返回服务实例
- 在 Function 中通过 `self.call_service[service_name]` 访问服务
- 服务在整个环境生命周期中保持单例

---

*SAGE中间件服务为数据密集型应用提供了强大的基础设施支持，是构建智能应用的核心组件。*
