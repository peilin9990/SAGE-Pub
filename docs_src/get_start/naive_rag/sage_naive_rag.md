# Naive RAG实现指南

> 本文档面向熟悉RAG基本流程的开发者。如果您对RAG概念不了解，请先阅读 [RAG - 检索增强生成技术介绍](you_know_rag.md)。

## 为什么选择SAGE构建RAG？

SAGE流处理框架为RAG系统提供了强大的技术基础：

- **统一的内存服务**：提供高效的向量存储和检索
- **流式处理能力**：支持实时数据摄入和查询处理
- **模块化设计**：可灵活组合不同的处理算子
- **服务化架构**：便于系统集成和扩展

## Naive RAG Pipeline示例

我们将通过 SAGE Lib 中预定义的算子向您展示一个完整的 Naive RAG 查询处理流水线的创建：

```python
from sage.core.api.local_environment import LocalEnvironment
from sage.service.memory.memory_service import MemoryService
from sage.apps.lib.io.source import QuerySource
from sage.apps.lib.rag.retriever import DenseRetriever
from sage.apps.lib.rag.promptor import QAPromptor
from sage.apps.lib.rag.generator import OpenAIGenerator
from sage.apps.lib.io.sink import TerminalSink

def naive_rag_example():
    env = LocalEnvironment()
    # 请求使用知识库服务
    env.register_service("memory_service", MemoryService())
    # 创建 Naive RAG Pipeline 
    env.from_source(QuerySource).map(DenseRetriever).map(QAPromptor).map(OpenAIGenerator).sink(AnswerSink)
    env.submit()
```

在完成了基础的 Naive RAG Pipeline 构建后，接下来我们需要准备离线知识库，以便为查询提供可检索的信息支持。以下是知识库构建的关键步骤与示例代码：

## 离线知识库构建

### 1. 基础知识库创建

使用SAGE Memory Service创建知识库：

```python
from sage.service.memory.memory_service import MemoryService
from sage.utils.embedding_methods.embedding_api import apply_embedding_model

def create_knowledge_base():
    # 初始化服务
    embedding_model = apply_embedding_model("default")
    memory_service = MemoryService()
    
    # 创建知识库集合
    collection_result = memory_service.create_collection(
        name="rag_knowledge",
        backend_type="VDB",
        description="RAG知识库",
        embedding_model=embedding_model,
        dim=embedding_model.get_dim()
    )
    
    # 批量插入知识
    knowledge_data = [
        "机器学习是人工智能的一个分支，通过算法让计算机从数据中自动学习模式。",
        "深度学习使用多层神经网络来模拟人脑的学习过程，特别擅长处理图像和语音。",
        # ... 更多知识条目
    ]
    
    for i, text in enumerate(knowledge_data):
        memory_service.insert_data(
            collection_name="rag_knowledge",
            text=text,
            metadata={
                "id": i + 1,
                "topic": "AI/ML",
                "type": "knowledge",
                "source": "manual"
            }
        )
    
    # 创建检索索引
    memory_service.create_index(
        collection_name="rag_knowledge",
        index_name="knowledge_index",
        description="知识检索索引"
    )
    
    # 持久化存储
    memory_service.store()
    print("✅ 知识库构建完成")
```

### 2. 运行示例

```bash
# 构建知识库
python app/memory_app/mem_offline_write.py

# 测试检索效果
python app/memory_app/mem_offline_write_test.py
```

## 流式RAG查询处理

### 1. 实时查询处理流水线

SAGE支持构建流式RAG系统，可以实时处理用户查询：

```python
class StreamingRAGSource(BatchFunction):
    """模拟实时查询流"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_queries = [
            "什么是深度学习？",
            "监督学习是怎么工作的？", 
            "Transformer有什么特点？",
            "强化学习的核心机制是什么？"
        ]
        self.counter = 0

    def execute(self):
        if self.counter >= len(self.test_queries):
            return None
        
        query_data = {
            "query": self.test_queries[self.counter],
            "query_id": self.counter + 1,
            "timestamp": time.time()
        }
        self.counter += 1
        return query_data

class KnowledgeRetriever(MapFunction):
    """知识检索算子"""
    def execute(self, data):
        result = self.call_service["memory_service"].retrieve_data(
            collection_name="rag_knowledge",
            query_text=data['query'],
            topk=2,
            index_name="knowledge_index",
            with_metadata=True
        )
        
        if result['status'] == 'success':
            data['retrieved_knowledge'] = result['results']
        else:
            data['retrieved_knowledge'] = []
        
        return data

class RAGResultSink(SinkFunction):
    """结果展示算子"""
    def execute(self, data):
        print(f"\n🔍 查询 {data['query_id']}: {data['query']}")
        
        if data['retrieved_knowledge']:
            print(f"📖 检索到 {len(data['retrieved_knowledge'])} 条相关知识:")
            for i, knowledge in enumerate(data['retrieved_knowledge'], 1):
                print(f"  {i}. {knowledge.get('text', 'N/A')}")
        else:
            print("❌ 未检索到相关知识")
        
        return data
```

### 2. 创建流式处理环境

```python
def create_streaming_rag():
    env = LocalEnvironment()
    
    # 注册Memory Service
    def memory_service_factory():
        memory_service = MemoryService()
        # 连接现有知识库
        return memory_service
    
    env.register_service("memory_service", memory_service_factory)
    
    # 构建流水线
    env.from_source(StreamingRAGSource).map(KnowledgeRetriever).sink(RAGResultSink)
    env.submit()
```

## 系统特性

### 内存服务优势
- **高效向量存储**：支持大规模向量数据存储
- **快速相似度检索**：毫秒级检索响应
- **元数据过滤**：支持基于条件的精确检索
- **持久化存储**：数据可靠持久化到磁盘

### 流处理能力
- **实时处理**：支持实时查询流处理
- **弹性扩展**：可根据负载动态调整
- **故障恢复**：提供完善的错误处理机制
- **监控观测**：全链路处理状态可观测

## 扩展方向

1. **Prompt工程**：优化上下文组装和prompt模板
2. **LLM集成**：接入各种大语言模型API
3. **结果优化**：添加答案质量评估和优化
4. **多模态支持**：扩展到图像、音频等多模态检索

## 快速开始

1. 克隆项目并安装依赖
2. 运行 `python app/memory_app/mem_offline_write.py` 构建知识库
3. 运行 `python app/memory_app/mem_offline_write_test.py` 测试检索效果
4. 根据需要扩展prompt和generation功能

---

*通过SAGE构建的RAG系统具备生产级的稳定性和扩展性，是企业级RAG应用的理想选择。*
