# Naive RAG实现指南

> 本文档面向熟悉RAG基本流程的开发者。如果您对RAG概念不了解，请先阅读 [RAG - 检索增强生成技术介绍](you_know_rag.md)。

## 为什么选择SAGE构建RAG？

SAGE流处理框架为RAG系统提供了强大的技术基础：

- **统一的数据流处理**：支持批处理和流式处理两种模式
- **丰富的RAG组件库**：提供检索器、生成器、提示词等预制组件
- **灵活的服务集成**：支持内存服务、向量数据库等服务注册
- **模块化设计**：可灵活组合不同的处理算子

## Naive RAG Pipeline示例

我们将通过 SAGE 中预定义的算子向您展示一个完整的 Naive RAG 查询处理流水线的创建：

```python
from sage.core.api.local_environment import LocalEnvironment
from sage.libs.io_utils.source import FileSource
from sage.libs.io_utils.sink import TerminalSink
from sage.libs.rag.retriever import DenseRetriever
from sage.libs.rag.promptor import QAPromptor
from sage.libs.rag.generator import OpenAIGenerator
from sage.common.utils.config.loader import load_config

def naive_rag_pipeline():
    """创建Naive RAG处理管道"""
    env = LocalEnvironment("naive_rag")
    
    # 加载配置
    config = load_config("examples/config/config.yaml")
    
    # 构建RAG处理流程
    (env
        .from_source(FileSource, config["source"])
        .map(DenseRetriever, config["retriever"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    
    # 提交并运行
    env.submit()
    
    # 等待处理完成
    import time
    time.sleep(10)
    env.close()

if __name__ == '__main__':
    naive_rag_pipeline()
```

在完成了基础的 Naive RAG Pipeline 构建后，接下来我们需要准备离线知识库，以便为查询提供可检索的信息支持。以下是知识库构建的关键步骤与示例代码：

## 基于Chroma的知识库构建

### 1. 构建向量索引

使用SAGE提供的Chroma索引构建工具：

```python
"""
使用Chroma构建向量索引的示例
"""
import os
from sage.libs.rag.retriever import ChromaRetriever
from sage.middleware.utils.embedding.embedding_api import apply_embedding_model
from sage.common.utils.config.loader import load_config

def build_chroma_index():
    """构建Chroma向量索引"""
    
    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config_qa_chroma.yaml")
    config = load_config(config_path)
    
    # 初始化嵌入模型
    embedding_model = apply_embedding_model("default")
    
    # 准备知识数据
    knowledge_data = [
        "机器学习是人工智能的一个分支，通过算法让计算机从数据中自动学习模式。",
        "深度学习使用多层神经网络来模拟人脑的学习过程，特别擅长处理图像和语音。",
        "自然语言处理是人工智能的重要应用领域，涉及文本理解、生成和翻译等任务。",
        "强化学习通过与环境交互来学习最优策略，在游戏和机器人控制中应用广泛。",
        "计算机视觉使机器能够理解和处理视觉信息，包括图像识别、目标检测等。"
    ]
    
    # 使用ChromaRetriever构建索引
    retriever = ChromaRetriever(config["retriever"])
    
    # 向索引中添加文档
    for i, text in enumerate(knowledge_data):
        retriever.add_document(
            document_id=f"doc_{i}",
            text=text,
            metadata={"source": "knowledge_base", "topic": "AI/ML"}
        )
    
    print("✅ Chroma知识库构建完成")
    return retriever

if __name__ == "__main__":
    build_chroma_index()
```

### 2. RAG查询处理

基于构建的知识库进行查询：

```python
"""
使用Chroma进行RAG查询的完整示例
"""
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.batch_function import BatchFunction
from sage.libs.rag.retriever import ChromaRetriever
from sage.libs.rag.promptor import QAPromptor
from sage.libs.rag.generator import OpenAIGenerator
from sage.libs.io_utils.sink import TerminalSink

class QueryBatch(BatchFunction):
    """查询批处理数据源"""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.queries = [
            "什么是机器学习？",
            "深度学习有什么特点？",
            "自然语言处理的应用有哪些？",
            "强化学习如何工作？"
        ]
        self.counter = 0

    def execute(self):
        if self.counter >= len(self.queries):
            return None
        
        query = self.queries[self.counter]
        self.counter += 1
        return query

def chroma_rag_pipeline():
    """使用Chroma的RAG管道"""
    env = LocalEnvironment("chroma_rag")
    
    # 配置
    config = {
        "source": {"data_path": "examples/data/sample/question.txt"},
        "retriever": {
            "platform": "local",
            "chroma": {
                "collection_name": "knowledge_base",
                "persist_directory": "./chroma_db",
                "top_k": 3
            }
        },
        "promptor": {"platform": "local"},
        "generator": {
            "vllm": {
                "api_key": "your-api-key",
                "method": "openai",
                "model_name": "gpt-3.5-turbo",
                "base_url": "https://api.openai.com/v1"
            }
        },
        "sink": {"platform": "local"}
    }
    
    (env
        .from_batch(QueryBatch, config["source"])
        .map(ChromaRetriever, config["retriever"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    
    env.submit(autostop=True)

if __name__ == "__main__":
    chroma_rag_pipeline()
```

## 基于Milvus的分布式RAG

### 1. Milvus索引构建

```python
"""
使用Milvus构建分布式向量索引
"""
from sage.libs.rag.retriever import MilvusRetriever
from sage.middleware.utils.embedding.embedding_api import apply_embedding_model

def build_milvus_index():
    """构建Milvus向量索引"""
    
    config = {
        "retriever": {
            "platform": "local",
            "milvus": {
                "host": "localhost",
                "port": 19530,
                "collection_name": "knowledge_collection",
                "dimension": 384,
                "top_k": 5,
                "metric_type": "L2"
            }
        }
    }
    
    # 初始化Milvus检索器
    retriever = MilvusRetriever(config["retriever"])
    
    # 准备文档数据
    documents = [
        {"id": 1, "text": "Python是一种高级编程语言，语法简洁易学。", "metadata": {"category": "programming"}},
        {"id": 2, "text": "机器学习是AI的核心技术之一。", "metadata": {"category": "ai"}},
        {"id": 3, "text": "Docker容器化技术简化了应用部署。", "metadata": {"category": "devops"}},
    ]
    
    # 批量插入文档
    retriever.bulk_insert(documents)
    
    print("✅ Milvus知识库构建完成")

if __name__ == "__main__":
    build_milvus_index()
```

### 2. 分布式RAG管道

```python
"""
基于Milvus的分布式RAG管道
"""
from sage.core.api.remote_environment import RemoteEnvironment
from sage.libs.io_utils.source import FileSource
from sage.libs.rag.retriever import MilvusRetriever
from sage.libs.rag.promptor import QAPromptor
from sage.libs.rag.generator import OpenAIGenerator
from sage.libs.io_utils.sink import TerminalSink

def distributed_rag_pipeline():
    """分布式RAG管道"""
    # 连接到远程JobManager
    env = RemoteEnvironment(
        name="distributed_rag",
        host="127.0.0.1",
        port=19001
    )
    
    config = {
        "source": {"data_path": "examples/data/sample/question.txt"},
        "retriever": {
            "platform": "local",
            "milvus": {
                "host": "milvus-server",
                "port": 19530,
                "collection_name": "knowledge_collection",
                "top_k": 3
            }
        },
        "promptor": {"platform": "local"},
        "generator": {
            "vllm": {
                "api_key": "your-api-key",
                "method": "openai",
                "model_name": "gpt-3.5-turbo",
                "base_url": "http://llm-server:8000/v1"
            }
        },
        "sink": {"platform": "local"}
    }
    
    (env
        .from_source(FileSource, config["source"])
        .map(MilvusRetriever, config["retriever"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    
    env.submit()

if __name__ == "__main__":
    distributed_rag_pipeline()
```

## 流式RAG查询处理

### 1. 实时查询处理流水线

SAGE支持构建流式RAG系统，可以实时处理用户查询：

```python
"""
流式RAG查询处理示例
"""
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.source_function import SourceFunction
from sage.core.api.function.map_function import MapFunction
from sage.core.api.function.sink_function import SinkFunction
import time

class StreamingQuerySource(SourceFunction):
    """模拟实时查询流"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.test_queries = [
            "什么是深度学习？",
            "Python有什么特点？", 
            "Docker如何使用？",
            "机器学习的应用场景？"
        ]
        self.counter = 0

    def execute(self):
        if self.counter >= len(self.test_queries):
            self.counter = 0  # 循环查询
        
        query_data = {
            "query": self.test_queries[self.counter],
            "query_id": self.counter + 1,
            "timestamp": time.time()
        }
        self.counter += 1
        return query_data

class KnowledgeRetriever(MapFunction):
    """知识检索算子"""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.topk = config.get("topk", 3)

    def execute(self, data):
        query = data.get("query", "")
        
        # 模拟检索过程
        retrieved_docs = [
            f"相关文档1：关于'{query}'的基础知识",
            f"相关文档2：'{query}'的实际应用",
            f"相关文档3：'{query}'的进阶内容"
        ]
        
        data["retrieved_knowledge"] = retrieved_docs
        return data

class StreamingRAGSink(SinkFunction):
    """流式RAG结果输出"""
    def execute(self, data):
        print(f"\n🔍 查询 {data.get('query_id', 'N/A')}: {data.get('query', 'N/A')}")
        
        if "answer" in data:
            print(f"🤖 回答: {data['answer']}")
        
        if "retrieved_knowledge" in data:
            print(f"📖 检索到 {len(data['retrieved_knowledge'])} 条相关知识")
        
        print("─" * 50)
        return data

def streaming_rag_pipeline():
    """创建流式RAG处理环境"""
    env = LocalEnvironment("streaming_rag")
    
    config = {
        "retriever": {"topk": 3},
        "promptor": {"platform": "local"},
        "generator": {
            "vllm": {
                "api_key": "your-api-key",
                "method": "openai", 
                "model_name": "gpt-3.5-turbo",
                "base_url": "https://api.openai.com/v1"
            }
        }
    }
    
    # 构建流水线
    (env
        .from_source(StreamingQuerySource)
        .map(KnowledgeRetriever, config["retriever"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(StreamingRAGSink)
    )
    
    try:
        print("🚀 启动流式RAG系统...")
        env.submit()
        
        # 运行一段时间
        import time
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("\n⏹️ 停止流式RAG系统")
    finally:
        env.close()

if __name__ == "__main__":
    streaming_rag_pipeline()
```

## 系统特性与优势

### 核心组件特性
- **灵活的检索器**：支持Chroma、Milvus等多种向量数据库
- **智能提示词生成**：自动组合查询和检索上下文
- **多模型生成器**：支持OpenAI、vLLM等多种生成模型
- **流式处理能力**：支持实时和批量两种处理模式

### 性能优势
- **高效检索**：毫秒级向量相似度搜索
- **弹性扩展**：支持分布式部署和负载均衡
- **容错处理**：完善的错误处理和重试机制
- **监控观测**：全链路处理状态可观测

## 配置示例

### 完整配置文件

```yaml
pipeline:
  name: "naive-rag-pipeline"
  description: "基础RAG问答管道"

source:
  data_path: "examples/data/sample/question.txt"
  platform: "local"

retriever:
  platform: "local"
  # Chroma配置
  chroma:
    collection_name: "knowledge_base"
    persist_directory: "./chroma_db"
    top_k: 3
    
  # 或者Milvus配置
  milvus:
    host: "localhost"
    port: 19530
    collection_name: "knowledge_collection"
    dimension: 384
    top_k: 5
    metric_type: "L2"

promptor:
  platform: "local"
  template_type: "qa"  # 或 "summarization"

generator:
  vllm:
    api_key: "your-api-key"
    method: "openai"
    model_name: "gpt-3.5-turbo"
    base_url: "https://api.openai.com/v1"
    temperature: 0.7
    max_tokens: 1000

sink:
  platform: "local"
```

## 扩展方向

1. **高级检索技术**：
   - 混合检索（密集+稀疏）
   - 重排序（Reranking）
   - 查询扩展和改写

2. **提示词工程**：
   - 动态提示词模板
   - 上下文长度优化
   - 多轮对话支持

3. **生成质量优化**：
   - 答案质量评估
   - 引用和溯源
   - 幻觉检测和缓解

4. **系统性能优化**：
   - 缓存机制
   - 批量处理
   - 异步并发

## 最佳实践

### 1. 知识库质量
- 确保文档内容的准确性和时效性
- 合理的文档分块策略
- 丰富的元数据标注

### 2. 检索优化
- 选择合适的embedding模型
- 调优检索参数（top_k、阈值等）
- 实施检索结果过滤和排序

### 3. 生成优化
- 设计有效的提示词模板
- 调节模型参数（temperature、top_p等）
- 实施输出格式控制

### 4. 系统监控
- 检索精度监控
- 生成质量评估
- 系统性能指标追踪

## 快速开始

1. **环境准备**：
   ```bash
   # 安装SAGE
   pip install sage-framework
   
   # 启动向量数据库（选择其一）
   docker run -p 19530:19530 milvusdb/milvus:latest  # Milvus
   # 或者直接使用Chroma（无需额外安装）
   ```

2. **构建知识库**：
   ```bash
   python examples/rag/build_chroma_index.py
   # 或
   python examples/rag/build_milvus_index.py
   ```

3. **运行RAG管道**：
   ```bash
   python examples/rag/qa_dense_retrieval_chroma.py
   # 或
   python examples/rag/qa_dense_retrieval_milvus.py
   ```

4. **自定义扩展**：
   - 根据需求修改配置文件
   - 自定义检索和生成组件
   - 集成业务特定的数据源

---

*通过SAGE构建的RAG系统具备生产级的稳定性和扩展性，是企业级智能问答应用的理想选择。*
