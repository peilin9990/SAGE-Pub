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
RAG系统采用两阶段架构设计：1）知识库构建阶段；2）查询处理阶段。
1）知识库构建阶段：考虑到知识库构建阶段中创建与存储索引需要消耗大量资源与时间，SAGE提供了离线和在线两种知识库构建方式，以供用户依据自身知识库大小，选择合适的知识库构建方式。

2）查询处理阶段：用户提供流式数据，输入到基于SAGE搭建的pipline中，通过检索器和生成器等组件，得到最终输出。

```
[离线阶段/在线阶段] 知识库构建
 文档加载  → 文本分块 →  向量编码 →  索引存储
    ↓           ↓          ↓          ↓
TextLoader → Chunker → Embedding → VectorDB

[在线阶段] 查询处理  
  用户查询   →  向量检索 → 上下文组合 → 答案生成
     ↓            ↓          ↓           ↓
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


## 数据准备与索引构建

### 知识库数据格式
#### 知识库输入文件格式 (knowledge_corpus.txt)
SAGE通过输入.txt文件格式构建知识库，简要示例如下。
```python
"""
ChromaDB是一个开源的向量数据库，专门为AI应用设计。

SAGE是一个现代化的RAG框架，提供了完整的检索增强生成解决方案。

向量检索技术通过计算查询向量与文档向量的相似度来找到最相关的内容。

自然语言处理是人工智能的重要分支，专注于让计算机理解和生成人类语言。
"""
```

#### 知识库查询数据格式 (qa_dataset.jsonl)
SAGE通过输入.jsonl文件格式模拟流式输入，简要示例如下。
```python
{"query": "什么是ChromaDB？", "expected_answer": "开源向量数据库"}
{"query": "SAGE框架有什么特点？", "expected_answer": "现代化RAG解决方案"}
{"query": "向量检索的工作原理是什么？", "expected_answer": "计算向量相似度"}
```

## RAG系统两阶段执行流程

RAG系统的运行分为两个独立且必需的阶段：**索引构建阶段**和**查询处理阶段**。必须先完成索引构建，才能执行查询处理。

### ⚠️ 重要提醒
在运行任何RAG查询之前，**必须先构建向量索引**。索引构建是一次性的离线或在线过程，完成后可以支持多次查询。

```
第一步：索引构建   →   第二步：查询处理
     ↓                    ↓
构建向量数据库     →   执行RAG流水线
```

## 阶段一：索引构建

### 索引构建的必要性

向量索引是RAG系统的基础设施，类似于传统数据库的索引。没有预先构建的索引，检索器将无法找到相关文档。

**索引构建过程**：
1. 加载原始知识文档；
2. 将文档分割成适合检索的小块；
3. 使用嵌入模型将文本块转换为向量；
4. 将向量存储到向量数据库中；
5. 建立高效的相似度搜索索引。


### 离线索引构建实现

离线索引构建不依赖流水线，需要独立执行索引构建流程。此方法尤其适用于数据量较大的情况下构建知识库。具体示例如下：

```python
def build_knowledge_index(config: dict) -> None:
    """
    阶段一：构建知识库向量索引（离线过程）
    
    该函数必须在RAG查询之前运行，用于构建可检索的向量索引
    
    Args:
        config: 包含knowledge_file和retriever配置的字典
    """
    print("=== 开始索引构建阶段 ===")
    
    # 1. 加载原始文档
    print("步骤1: 加载原始文档...")
    loader = TextLoader(config["retriever"]["chroma"]["knowledge_file"])
    document = loader.load()
    print(f"✓ 文档加载完成，内容长度: {len(document['content']):,} 字符")
    
    # 2. 文档分块处理
    print("步骤2: 文档分块处理...")
    splitter = CharacterSplitter({
        "separator": "\n\n",        # 按段落分割
        "chunk_size": 800,          # 块大小
        "overlap": 100              # 重叠大小
    })
    chunks = splitter.execute(document)
    print(f"✓ 文档分块完成，共生成 {len(chunks)} 个文档块")
    
    # 3. 构建向量索引
    print("步骤3: 构建向量索引...")
    print("  - 初始化嵌入模型...")
    print("  - 生成文档向量...")
    print("  - 建立索引结构...")
    
    # 初始化检索器会自动触发索引构建过程
    retriever = ChromaRetriever(config["retriever"])
    print("✓ 向量索引构建完成")
    
    # 4. 验证索引质量
    print("步骤4: 验证索引质量...")
    test_queries = [
        "什么是向量数据库？",
        "SAGE框架的特点",
        "如何使用ChromaDB"
    ]
    
    for i, test_query in enumerate(test_queries, 1):
        test_results = retriever.execute(test_query)
        if test_results['results']:
            print(f"✓ 测试查询{i}: '{test_query}' - 找到 {len(test_results['results'])} 个相关文档")
            print(f"  最佳匹配: {test_results['results'][0][:80]}...")
        else:
            print(f"⚠️ 测试查询{i}: '{test_query}' - 未找到相关文档")
    
    print("=== 索引构建阶段完成 ===")
    print(f"索引存储位置: {config['retriever']['chroma']['persist_path']}")
    print("现在可以执行RAG查询流水线了！\n")

# 执行索引构建（必须首先运行）
print("开始RAG系统部署...")
print("注意：首次运行时需要构建索引，这可能需要几分钟时间")
build_knowledge_index(rag_config)
```

### 在线索引构建实现

在线索引构建方法需要依赖RAG流水线，在配置文件中加入“knowledge_file: "./examples/data/qa_knowledge_base.txt"”字段，声明需要在RAG流水线中自动加载文件并创建数据库。如果未加上述字段，则说明流水线需要从数据库中加载离线知识库，如果未找到离线数据库，则返回空值。

## 阶段二：查询处理（在线过程）

### 查询处理流程说明

在向量索引构建完成后，就可以启动RAG查询处理流水线。该阶段处理用户的实际查询请求，生成最终答案。

**查询处理过程**：
1. 接收用户查询或批量查询数据
2. 在向量数据库中检索相关文档
3. 将查询和检索结果组装成提示词
4. 调用生成模型产生最终答案
5. 输出结构化的回答结果

### RAG流水线实现

```python
def execute_rag_pipeline(config: dict) -> None:
    """
    阶段二：执行RAG查询处理流水线（在线过程）
    
    前提条件：必须已完成向量索引构建
    
    Args:
        config: 完整的RAG系统配置
    """
    print("=== 开始RAG查询处理阶段 ===")
    
    # 验证索引是否存在
    if not check_index_status(config):
        print("❌ 错误：未发现向量索引！")
        print("请先运行 build_knowledge_index() 构建索引")
        return
    
    print("✓ 索引验证通过，启动RAG流水线...")
    
    # 创建本地执行环境
    env = LocalEnvironment()
    
    # 构建处理流水线
    pipeline = (
        env
        .from_batch(JSONLBatch, config["source"])           # 数据源：用户查询
        .map(ChromaRetriever, config["retriever"])           # 检索：向量相似度搜索
        .map(QAPromptor, config["promptor"])                 # 提示：上下文组装
        .map(OpenAIGenerator, config["generator"]["vllm"])   # 生成：LLM答案生成
        .sink(TerminalSink, config["sink"])                  # 输出：结果展示
    )
    
    print("RAG流水线配置完成，开始处理查询...")
    
    # 提交执行
    env.submit()
    
    # 等待处理完成
    print("正在处理查询，请等待...")
    time.sleep(10)
    
    # 清理资源
    env.close()
    
    print("=== RAG查询处理完成 ===")
```

## 系统配置与运行

### 完整系统配置示例

```python
# 完整的RAG系统配置
rag_config = {
    # 数据源配置
    "source": {
        "file_path": "data/qa_dataset.jsonl",     # 查询数据集路径
        "batch_size": 32,                        # 批处理大小
        "shuffle": False                         # 是否随机打乱
    },
    
    # 检索器配置
    "retriever": {
        "dimension": 384,                        # 向量维度
        "top_k": 5,                             # 检索文档数量
        "embedding": {
            "method": "default",
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        },
        "chroma": {
            "persist_path": "./vector_database",     # 向量数据库路径
            "collection_name": "knowledge_base",     # 集合名称
            "knowledge_file": "data/knowledge_corpus.txt"  # 知识库文件
        }
    },
    
    # 提示词配置
    "promptor": {
        "template_type": "qa",                   # 问答模板类型
        "include_context": True,                 # 包含检索上下文
        "max_context_length": 2000              # 最大上下文长度
    },
    
    # 生成器配置
    "generator": {
        "vllm": {
            "method": "openai",                  # 生成方法
            "model_name": "gpt-4o-mini",        # 模型名称
            "base_url": "http://localhost:8000/v1",  # API服务地址
            "api_key": "your-api-key",          # API密钥
            "temperature": 0.7,                  # 生成温度
            "max_tokens": 512,                   # 最大生成token数
            "seed": 42                          # 随机种子
        }
    },
    
    # 输出配置
    "sink": {
        "format": "json",                       # 输出格式
        "show_metadata": True,                  # 显示元数据
        "save_to_file": "results/rag_output.jsonl"  # 保存文件路径
    }
}
```

### YAML配置文件格式

对于生产环境，推荐使用YAML配置文件：

```yaml
# config_rag_system.yaml
source:
  file_path: "data/qa_dataset.jsonl"
  batch_size: 32
  shuffle: false

retriever:
  dimension: 384
  top_k: 5
  embedding:
    method: "default"
    model: "sentence-transformers/all-MiniLM-L6-v2"
  chroma:
    persist_path: "./vector_database"
    collection_name: "knowledge_base"
    knowledge_file: "data/knowledge_corpus.txt"

promptor:
  template_type: "qa"
  include_context: true
  max_context_length: 2000

generator:
  vllm:
    method: "openai"
    model_name: "gpt-4o-mini"
    base_url: "http://localhost:8000/v1"
    api_key: "${OPENAI_API_KEY}"  # 使用环境变量
    temperature: 0.7
    max_tokens: 512
    seed: 42

sink:
  format: "json"
  show_metadata: true
  save_to_file: "results/rag_output.jsonl"
```

```python
# 加载YAML配置的工具函数
import yaml
import os

def load_config_from_yaml(config_path: str) -> dict:
    """从YAML文件加载配置，支持环境变量替换"""
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_str = f.read()
    
    # 替换环境变量
    config_str = os.path.expandvars(config_str)
    
    # 解析YAML
    config = yaml.safe_load(config_str)
    
    return config

# 使用YAML配置
rag_config = load_config_from_yaml("config_rag_system.yaml")
```

## 高级功能扩展

### 使用重排序器提升精度

可以在检索和提示词生成之间加入重排序器，进一步提升检索精度：

```python
def execute_rag_with_reranker(config: dict) -> None:
    """
    带重排序器的RAG流水线
    """
    print("=== 启动带重排序器的RAG流水线 ===")
    
    env = LocalEnvironment()
    pipeline = (
        env
        .from_batch(JSONLBatch, config["source"])
        .map(ChromaRetriever, config["retriever"])
        .map(BGEReranker, config["reranker"])      # 添加重排序器
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    
    env.submit()
    time.sleep(10)
    env.close()

# 重排序器配置
reranker_config = {
    "model_name": "BAAI/bge-reranker-v2-m3",
    "topk": 3,
    "device": "cuda"  # 如果有GPU
}

# 将重排序器配置添加到主配置中
rag_config["reranker"] = reranker_config
```

### 使用HuggingFace本地模型

对于需要完全本地部署的场景，可以使用HuggingFace模型：

```python
def execute_rag_with_hf_model(config: dict) -> None:
    """
    使用HuggingFace本地模型的RAG流水线
    """
    print("=== 启动本地模型RAG流水线 ===")
    
    env = LocalEnvironment()
    pipeline = (
        env
        .from_batch(JSONLBatch, config["source"])
        .map(ChromaRetriever, config["retriever"])
        .map(BGEReranker, config["reranker"])
        .map(QAPromptor, config["promptor"])
        .map(HFGenerator, config["generator"]["hf"])    # 使用HF生成器
        .sink(TerminalSink, config["sink"])
    )
    
    env.submit()
    time.sleep(10)
    env.close()

# HuggingFace生成器配置
hf_config = {
    "model_name": "microsoft/DialoGPT-medium",
    "device": "cuda",
    "temperature": 0.8,
    "max_new_tokens": 256
}

# 添加HF配置
rag_config["generator"]["hf"] = hf_config
```

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

## 使用Refiner文档优化器

Refiner是基于LongRefiner技术的文档优化组件，能够智能压缩检索文档，在保持语义完整性的同时显著减少上下文长度。

核心流程如下，增加了LongRefinerAdapter算子：

```python
from sage.libs.rag.refiner import LongRefinerAdapter

def pipeline_with_refiner(config: dict) -> None:
    env = LocalEnvironment()
    (
        env
        .from_batch(JSONLBatch, config["source"])
        .map(ChromaRetriever, config["retriever"])
        .map(LongRefinerAdapter, config["refiner"])  # 添加文档优化
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    env.submit()
    time.sleep(10)
    env.close()
```

配置示例：

```python
refiner_config = {
    "refiner": {
        "model_name": "long-refiner-base",
        "compression_ratio": 0.2,          # 压缩比例
        "enable_cache": True,              # 启用缓存
        "max_input_length": 8192
    }
}
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

## 使用Milvus向量库进行向量检索
SAGE提供了基于Milvus向量库的稠密向量检索和稀疏向量检索算子，可以先执行离线向量知识库构建，创建知识库，然后执行RAG流水线，调用创建的知识库，对其中的知识进行查询。

### 基于Milvus向量库的稠密向量检索
#### 离线稠密向量知识库构建
基于Milvus的稠密向量数据库构建示例如下：
```python
import os
import sys
from sage.libs.rag.chunk import CharacterSplitter
from sage.libs.rag.document_loaders import TextLoader
from sage.libs.rag.retriever import MilvusDenseRetriever
import yaml
from sage.common.utils.config.loader import load_config

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def load_knowledge_to_milvus(config):
    """
    加载知识库到 Milvus
    """
    knowledge_file = config.get('preload_knowledge_file')
    persistence_path = config.get('milvus_dense').get('persistence_path')
    collection_name = config.get('milvus_dense').get('collection_name')

    print(f"=== 预加载知识库到 ChromaDB ===")
    print(f"文件: {knowledge_file} | DB: {persistence_path} | 集合: {collection_name}")

    loader = TextLoader(knowledge_file)
    document = loader.load()
    print(f"已加载文本，长度: {len(document['content'])}")

    splitter = CharacterSplitter({"separator": "\n\n"})
    chunks = splitter.execute(document)
    print(f"分块数: {len(chunks)}")
    
    print("初始化Milvus...")
    milvus_backend = MilvusDenseRetriever(config)
    milvus_backend.add_documents(chunks)
    print(f"✓ 已添加 {len(chunks)} 个文本块")
    print(f"✓ 数据库信息: {milvus_backend.get_collection_info()}")
    text_query = "什么是RAG？"
    results = milvus_backend.execute(text_query)
    print(f"检索结果: {results}")
    return True

if __name__ == "__main__":
    config_path = 'config_dense_milvus.yaml'
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
    
    config = load_config(config_path)
    result = load_knowledge_to_milvus(config["retriever"])
    if result:
        print("知识库已成功加载，可运行检索/问答脚本")
    else:
        print("知识库加载失败")
        sys.exit(1)

```

config_dense_milvus.yaml配置文件如下：
```yaml
retriever:
  preload_knowledge_file: "知识库文件路径（.txt）"

  # 通用参数
  dimension: 384            # 向量维度，应与 embedding 模型一致
  top_k: 2                 # 返回文档数量

  # 嵌入模型配置（用于对文档和查询编码）
  embedding:
    method: "hf"
    model: "sentence-transformers/all-MiniLM-L6-v2"

  # Milvus 后端（稠密检索）
  milvus_dense:
    # 本地 Milvus Lite（推荐用于快速试用）
    persistence_path: "./milvus_qa_dense.db"

    # 远程 Milvus（如需远程，请注释上面的 persistence_path，改为如下配置）
    # host: "127.0.0.1"
    # port: 19530
    # force_http: true

    collection_name: "qa_dense_collection"
    dim: 384
    metric_type: "COSINE"   # 只允许: IP / COSINE / L2
    search_type: "dense"     # 稠密检索

    # 可选项
    dense_insert_batch_size: 128
    # 知识文件（可选）：提供后将自动按段落读取并入库
    # knowledge_file: "./examples/data/qa_knowledge_base.txt"
```

#### 基于Milvus的稠密向量检索RAG流水线
```python
import os
from sage.core.api.local_environment import LocalEnvironment
from sage.libs.io_utils.batch import JSONLBatch
from sage.libs.io_utils.sink import TerminalSink
from sage.libs.rag.generator import OpenAIGenerator
from sage.libs.rag.promptor import QAPromptor
from sage.libs.rag.retriever import MilvusDenseRetriever
from sage.common.utils.config.loader import load_config
import yaml


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def pipeline_run():
    """    
    创建并运行 Milvus 专用 RAG 数据处理管道

    Args:
        config (dict): 包含各模块配置的配置字典。
    """

    print("=== 启动基于 Milvus 的 RAG 问答系统 ===")
    print("配置信息:")
    print(f"  - 源文件: {config['source']['data_path']}")
    print(f"  - 检索器: MilvusDenseRetriever (Milvus 专用)")
    print(f"  - 向量维度: {config['retriever']['dimension']}")
    print(f"  - Top-K: {config['retriever']['top_k']}")
    print(f"  - 集合名称: {config['retriever']['milvus_dense']['collection_name']}")
    print(f"  - 嵌入模型: {config['retriever']['embedding']['method']}")

    env = LocalEnvironment()
    # 构建数据处理流程
    # MilvusDenseRetriever 会在初始化时自动加载配置的知识库文件
    print("正在构建数据处理管道...")
    # 构建数据处理流程
    (env
        .from_source(JSONLBatch, config["source"])
        .map(MilvusDenseRetriever, config["retriever"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    print("正在提交并运行管道...")
    env.submit(autostop=True)
    env.close()
    print("=== RAG 问答系统运行完成 ===")


if __name__ == '__main__':
    config_path = './examples/config/config_dense_milvus.yaml'
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
    
    config = load_config(config_path)

    print(config)

    # 检查知识库文件（如果配置了）
    knowledge_file = config["retriever"]["milvus_dense"].get("knowledge_file")
    if knowledge_file:
        if not os.path.exists(knowledge_file):
            print(f"警告：知识库文件不存在: {knowledge_file}")
            print("请确保知识库文件存在于指定路径")
        else:
            print(f"找到知识库文件: {knowledge_file}")
    
    print("开始运行 Milvus 稠密向量检索管道...")
    pipeline_run() 
```
配置文件如下：
```yaml
source:
  data_path: "./queries.jsonl"   # 用户提供的流式问题，格式见首段描述
  platform: "local"

retriever:
  preload_knowledge_file: "知识库文件路径（.txt）"
  # 通用参数
  dimension: 384            # 向量维度，应与 embedding 模型一致
  top_k: 2                 # 返回文档数量

  # 嵌入模型配置（用于对文档和查询编码）
  embedding:
    method: "hf"
    model: "sentence-transformers/all-MiniLM-L6-v2"

  # Milvus 后端（稠密检索）
  milvus_dense:
    # 本地 Milvus Lite（推荐用于快速试用）
    persistence_path: "./milvus_qa_dense.db"

    # 远程 Milvus（如需远程，请注释上面的 persistence_path，改为如下配置）
    # host: "127.0.0.1"
    # port: 19530
    # force_http: true

    collection_name: "qa_dense_collection"
    dim: 384
    metric_type: "COSINE"   # 只允许: IP / COSINE / L2
    search_type: "dense"     # 稠密检索

    # 稠密向量导入数据库的批次数
    dense_insert_batch_size: 128
    # 知识文件（可选）：提供后将自动按段落读取并入库
    # knowledge_file: "./examples/data/qa_knowledge_base.txt"

promptor:
  template: |
    基于以下检索到的相关文档，回答用户问题：

    相关文档：
    {retrieved_documents}

    用户问题：{query}

    请提供准确、有用的回答：

generator:
  vllm:
    api_key: "your-own-api_key"
    method: "openai"
    model_name: "meta-llama/Llama-2-7b-chat-hf"
    base_url: "base_url"
    seed: 42

sink:
  enable_log: true
```
#### 离线稀疏向量知识库构建
基于Milvus的稀疏向量数据库构建示例如下：

```python
import os
import sys
from sage.libs.rag.chunk import CharacterSplitter
from sage.libs.rag.document_loaders import TextLoader
from sage.libs.rag.retriever import MilvusSparseRetriever
import yaml
from sage.common.utils.config.loader import load_config

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def load_knowledge_to_milvus(config):
    """
    加载知识库到 Milvus
    """
    knowledge_file = config.get('preload_knowledge_file')
    persistence_path = config.get('milvus_sparse').get('persistence_path')
    collection_name = config.get('milvus_sparse').get('collection_name')

    print(f"=== 预加载知识库到 Milvus ===")
    print(f"文件: {knowledge_file} | DB: {persistence_path} | 集合: {collection_name}")

    loader = TextLoader(knowledge_file)
    document = loader.load()
    print(f"已加载文本，长度: {len(document['content'])}")

    splitter = CharacterSplitter({"separator": "\n\n"})
    chunks = splitter.execute(document)
    print(f"分块数: {len(chunks)}")
    
    print("初始化Milvus...")
    milvus_backend = MilvusSparseRetriever(config)
    milvus_backend.add_documents(chunks)
    print(f"✓ 已添加 {len(chunks)} 个文本块")
    print(f"✓ 数据库信息: {milvus_backend.get_collection_info()}")
    text_query = "什么是RAG？"
    results = milvus_backend.execute(text_query)
    print(f"检索结果: {results}")
    return True

if __name__ == "__main__":
    config_path = 'config_sparse_milvus.yaml'
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
    
    config = load_config(config_path)
    result = load_knowledge_to_milvus(config["retriever"])
    if result:
        print("知识库已成功加载，可运行检索/问答脚本")
    else:
        print("知识库加载失败")
        sys.exit(1)
```

config_sparse_milvus.yaml配置文件如下：
```yaml
retriever:
  preload_knowledge_file: "./examples/data/qa_knowledge_base.txt"

  # 通用参数
  top_k: 3                 # 返回文档数量

  # Milvus 后端（稠密检索）
  milvus_sparse:
    # 本地 Milvus Lite（推荐用于快速试用）
    persistence_path: "./milvus_qa_sparse.db"

    # 远程 Milvus（如需远程，请注释上面的 persistence_path，改为如下配置）
    # host: "127.0.0.1"
    # port: 19530
    # force_http: true

    collection_name: "qa_sparse_collection"
    search_type: "sparse"     # 稀疏检索
```

#### 基于Milvus的稀疏向量检索RAG流水线
```python
import os
import time
from sage.core.api.local_environment import LocalEnvironment
from sage.libs.io_utils.batch import JSONLBatch
from sage.libs.io_utils.sink import TerminalSink
from sage.libs.rag.generator import OpenAIGenerator
from sage.libs.rag.promptor import QAPromptor
from sage.libs.rag.retriever import MilvusSparseRetriever
from sage.common.utils.config.loader import load_config
import yaml


def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

def pipeline_run():
    """    
    创建并运行 Milvus 专用 RAG 数据处理管道

    Args:
        config (dict): 包含各模块配置的配置字典。
    """

    print("=== 启动基于 Milvus 的 RAG 问答系统 ===")
    print("配置信息:")
    print(f"  - 源文件: {config['source']['data_path']}")
    print(f"  - 检索器: MilvusSparseRetriever (Milvus 专用)")
    print(f"  - Top-K: {config['retriever']['top_k']}")
    print(f"  - 集合名称: {config['retriever']['milvus_sparse']['collection_name']}")

    env = LocalEnvironment()
    # 构建数据处理流程
    # MilvusSparseRetriever 会在初始化时自动加载配置的知识库文件
    print("正在构建数据处理管道...")
    # 构建数据处理流程
    (env
        .from_source(JSONLBatch, config["source"])
        .map(MilvusSparseRetriever, config["retriever"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    print("正在提交并运行管道...")
    env.submit(autostop=True)
    env.close()
    print("=== RAG 问答系统运行完成 ===")


if __name__ == '__main__':
    config_path = './config_sparse_milvus.yaml'
    if not os.path.exists(config_path):
        print(f"配置文件不存在: {config_path}")
    
    config = load_config(config_path)

    print(config)

    # 检查知识库文件（如果配置了）
    knowledge_file = config["retriever"]["milvus_sparse"].get("knowledge_file")
    if knowledge_file:
        if not os.path.exists(knowledge_file):
            print(f"警告：知识库文件不存在: {knowledge_file}")
            print("请确保知识库文件存在于指定路径")
        else:
            print(f"找到知识库文件: {knowledge_file}")
    
    print("开始运行 Milvus 稠密向量检索管道...")
    pipeline_run() 
```
config_sparse_milvus.yaml配置文件如下：
```yaml
source:
  data_path: "./queries.jsonl"   # 用户提供的流式问题，格式见首段描述
  platform: "local"

retriever:
  preload_knowledge_file: "./知识库文件.txt"

  # 通用参数
  top_k: 3                 # 返回文档数量

  # Milvus 后端（稠密检索）
  milvus_sparse:
    # 本地 Milvus Lite（推荐用于快速试用）
    persistence_path: "./milvus_qa_sparse.db"

    # 远程 Milvus（如需远程，请注释上面的 persistence_path，改为如下配置）
    # host: "127.0.0.1"
    # port: 19530
    # force_http: true

    collection_name: "qa_sparse_collection"
    search_type: "sparse"     # 稀疏检索

    # # 知识文件（可选）：提供后将自动按段落读取并入库
    # knowledge_file: "./examples/data/qa_knowledge_base.txt"

promptor:
  template: |
    基于以下检索到的相关文档，回答用户问题：

    相关文档：
    {retrieved_documents}

    用户问题：{query}

    请提供准确、有用的回答：

generator:
  vllm:
    api_key: "your-own-api_key"
    method: "openai"
    model_name: "meta-llama/Llama-2-7b-chat-hf"
    base_url: "base_url"
    seed: 42

sink:
  enable_log: true

```

---

## 组件组合使用

### 完整流水线示例

```python
def full_pipeline_run(config: dict) -> None:
    """包含所有组件的完整RAG流水线"""
    env = LocalEnvironment()
    (
        env
        .from_batch(JSONLBatch, config["source"])
        .map(ChromaRetriever, config["retriever"])        # 检索
        .map(BGEReranker, config["reranker"])             # 重排序  
        .map(LongRefinerAdapter, config["refiner"])       # 文档优化
        .map(QAPromptor, config["promptor"])              # 提示组装
        .map(OpenAIGenerator, config["generator"]["vllm"]) # 答案生成
        .sink(TerminalSink, config["sink"])               # 结果输出
    )
    env.submit()
    time.sleep(10)
    env.close()
```



### 配置参考

更多配置示例和详细文档：

- [检索器配置](../components/retriever.md)
- [重排序器配置](../components/BGE_RERANKER_GUIDE.md)  
- [文档优化器配置](../components/refiner.md)
- [基础配置文件](../../config/config_qa_chroma.yaml)

---

**注意**：本示例展示了SAGE框架下RAG系统的完整实现。