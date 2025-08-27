# RAG系统完整实现示例 (Complete RAG System Implementation)

本文档提供基于ChromaDB的RAG问答系统的完整实现示例。该示例展示了从数据准备到答案生成的端到端流程，是学习和理解RAG技术的最佳起点。

## 技术概述

### RAG系统简介
检索增强生成（Retrieval Augmented Generation, RAG）是一种结合检索和生成的AI技术架构，广泛应用于智能问答、知识管理和内容生成场景。

### 核心优势
- **知识实时性**：通过检索获取最新信息，避免训练数据时效性限制
- **答案可溯源**：每个答案都基于具体的知识来源，提供可验证性
- **资源效率**：无需重新训练大模型，通过检索机制扩展知识范围
- **领域适应性**：快速适配特定领域知识，支持垂直应用

## 系统架构

### 整体流程设计
RAG系统采用两阶段架构设计：

```
[离线阶段] 知识库构建
文档加载 → 文本分块 → 向量编码 → 索引存储
    ↓         ↓         ↓         ↓
TextLoader → Chunker → Embedding → VectorDB

[在线阶段] 查询处理  
用户查询 → 向量检索 → 上下文组装 → 答案生成
    ↓         ↓         ↓         ↓
QueryVector → Retriever → Promptor → Generator
```

### 核心组件说明

| 组件 | 功能 | 作用 |
|------|------|------|
| **数据加载器** | 文档读取和预处理 | 统一数据格式，处理多种文件类型 |
| **文本分块器** | 长文档切分 | 保持语义完整性，优化检索粒度 |
| **向量编码器** | 文本向量化 | 将文本转换为数值向量表示 |
| **向量数据库** | 索引存储和检索 | 高效的相似度搜索和管理 |
| **检索器** | 相关文档检索 | 根据查询找到最相关的文档块 |
| **提示词生成器** | 上下文组装 | 将查询和检索结果组织成提示 |
| **生成器** | 答案生成 | 基于上下文生成最终答案 |

## 完整实现代码

### 环境配置与依赖
```python
# 必要的库导入
import time
from sage.libs.environment import LocalEnvironment
from sage.libs.rag.document_loaders import TextLoader
from sage.libs.rag.chunk import CharacterSplitter
from sage.libs.rag.retriever import ChromaRetriever
from sage.libs.rag.promptor import QAPromptor
from sage.libs.rag.generator import OpenAIGenerator
from sage.libs.sink import TerminalSink
from sage.libs.source import JSONLBatch

# 配置文档
配置文件应包含以下部分：
- source: 数据源配置
- retriever: 检索器配置
- promptor: 提示词配置
- generator: 生成器配置
- sink: 输出配置
```

### 核心流水线实现
```python
def build_rag_pipeline(config: dict) -> None:
    """
    构建完整的RAG处理流水线
    
    Args:
        config: 系统配置字典，包含各组件的参数设置
    
    流程说明:
        1. 初始化本地环境管理器
        2. 加载批量数据源（JSONL格式）
        3. 依次应用检索、提示词生成、答案生成组件
        4. 输出结果到终端
    """
    # 创建本地执行环境
    env = LocalEnvironment()
    
    # 构建处理流水线
    pipeline = (
        env
        .from_batch(JSONLBatch, config["source"])           # 数据源：JSONL批量数据
        .map(ChromaRetriever, config["retriever"])           # 检索：向量相似度搜索
        .map(QAPromptor, config["promptor"])                 # 提示：上下文组装
        .map(OpenAIGenerator, config["generator"]["vllm"])   # 生成：LLM答案生成
        .sink(TerminalSink, config["sink"])                  # 输出：终端显示
    )
    
    # 提交执行
    env.submit()
    
    # 等待处理完成
    time.sleep(10)
    
    # 清理资源
    env.close()
    
    print("RAG流水线处理完成")
```

### 详细配置示例
```python
# 完整的系统配置
rag_config = {
    # 数据源配置
    "source": {
        "file_path": "data/qa_dataset.jsonl",
        "batch_size": 32,
        "shuffle": False
    },
    
    # 检索器配置
    "retriever": {
        "dimension": 384,                    # 向量维度
        "top_k": 5,                         # 检索数量
        "embedding": {
            "method": "default",
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        },
        "chroma": {
            "persist_path": "./vector_database",
            "collection_name": "knowledge_base",
            "knowledge_file": "data/knowledge_corpus.txt"
        }
    },
    
    # 提示词配置
    "promptor": {
        "template_type": "qa",              # 问答模板
        "include_context": True,            # 包含检索上下文
        "max_context_length": 2000          # 最大上下文长度
    },
    
    # 生成器配置
    "generator": {
        "vllm": {
            "method": "openai",
            "model_name": "gpt-4o-mini",
            "base_url": "http://localhost:8000/v1",
            "api_key": "your-api-key",
            "temperature": 0.7,
            "max_tokens": 512,
            "seed": 42
        }
    },
    
    # 输出配置
    "sink": {
        "format": "json",                   # 输出格式
        "show_metadata": True,              # 显示元数据
        "save_to_file": "results/rag_output.jsonl"
    }
}
```

## 数据准备与索引构建

### 知识库数据格式
```python
# 知识库文本文件格式 (knowledge_corpus.txt)
"""
ChromaDB是一个开源的向量数据库，专门为AI应用设计。

SAGE是一个现代化的RAG框架，提供了完整的检索增强生成解决方案。

向量检索技术通过计算查询向量与文档向量的相似度来找到最相关的内容。

自然语言处理是人工智能的重要分支，专注于让计算机理解和生成人类语言。
"""

# 查询数据格式 (qa_dataset.jsonl)
{"query": "什么是ChromaDB？", "expected_answer": "开源向量数据库"}
{"query": "SAGE框架有什么特点？", "expected_answer": "现代化RAG解决方案"}
{"query": "向量检索的工作原理是什么？", "expected_answer": "计算向量相似度"}
```

### 索引构建流程
```python
def build_knowledge_index(config: dict) -> None:
    """
    构建知识库向量索引
    
    该函数展示了如何从原始文档构建可检索的向量索引
    """
    # 1. 加载原始文档
    loader = TextLoader(config["knowledge_file"])
    document = loader.load()
    print(f"文档加载完成，内容长度: {len(document['content'])} 字符")
    
    # 2. 文档分块处理
    splitter = CharacterSplitter({
        "separator": "\n\n",        # 按段落分割
        "chunk_size": 800,          # 块大小
        "overlap": 100              # 重叠大小
    })
    chunks = splitter.execute(document)
    print(f"文档分块完成，共 {len(chunks)} 个文档块")
    
    # 3. 初始化检索器（自动构建索引）
    retriever = ChromaRetriever(config["retriever"])
    print("向量索引构建完成")
    
    # 4. 测试检索功能
    test_query = "什么是向量数据库？"
    test_results = retriever.execute(test_query)
    print(f"测试检索: {test_query}")
    print(f"检索结果: {test_results['results'][0][:100]}...")

# 执行索引构建
build_knowledge_index(rag_config)
```
---

## 配置说明

配置文件（如 `config_qa_chroma.yaml`）包含各模块参数：

- `source.data_path`：原始数据路径
- `retriever.dimension`：向量维度
- `retriever.top_k`：检索返回数量
- `retriever.chroma.collection_name`：ChromaDB 集合名
- `retriever.embedding.method`：嵌入模型方法
- `generator.vllm`：生成模型配置
- `sink`：输出配置

---

## 使用Rerank重排器

可以进一步使用Rerank进检索结果进行重排序，提高检索精度，这里以BGEReranker为例子进行说明。

核心流程如下，增加了BGEReranker算子：

```python
def pipeline_run(config: dict) -> None:
    env = LocalEnvironment()
    (
        env
        .from_batch(JSONLBatch, config["source"])
        .map(ChromaRetriever, config["retriever"])
        .map(BGEReranker, config["reranker"])  
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    env.submit()
    time.sleep(10)
    env.close()
```


## 使用huggingface model
除了调用 OpenAI/VLLM/DashScope 等远程端点，也可调用 HuggingFace 本地模型。

核心流程如下，替换了OpenAIGenerator算子：

```python
def pipeline_run(config: dict) -> None:
    env = LocalEnvironment()
    (
        env
        .from_batch(JSONLBatch, config["source"])
        .map(ChromaRetriever, config["retriever"])
        .map(BGEReranker, config["reranker"])  
        .map(QAPromptor, config["promptor"])
        .map(HFGenerator, config["generator"]["hf"])
        .sink(TerminalSink, config["sink"])
    )
    env.submit()
    time.sleep(10)
    env.close()
```