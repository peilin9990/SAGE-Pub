# BGE Reranker 组件使用说明

## 概述

Reranker 是 SAGE 框架中的重要组件，用于对检索到的文档进行重新排序，以提高检索增强生成（RAG）系统的准确性。该组件提供了两种不同的重排序实现：

1. **BGEReranker**: 基于 BAAI/bge-reranker-v2-m3 模型的传统重排序器
2. **LLMbased_Reranker**: 基于 BAAI/bge-reranker-v2-gemma 模型的 LLM 重排序器

## BGEReranker 使用方法

### 基本配置

```python
config = {
    "model_name": "BAAI/bge-reranker-v2-m3",
    "topk": 3,  # 或使用 "top_k"
    # 可选配置
    "device": "cuda"  # 或 "cpu"，默认自动检测
}
```

### 初始化和使用

```python
from sage.libs.rag.reranker import BGEReranker

# 初始化重排序器
reranker = BGEReranker(config)

# 准备输入数据
query = "什么是人工智能？"
documents = [
    "人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。",
    "机器学习是人工智能的一个子集，通过算法让计算机从数据中学习。",
    "深度学习使用神经网络来模拟人脑的工作方式。",
    "自然语言处理是人工智能的一个领域，专注于计算机与人类语言的交互。",
    "计算机视觉让机器能够识别和解释视觉信息。"
]

# 执行重排序
input_data = (query, documents)
result_query, reranked_docs = reranker.execute(input_data)

print(f"原始查询: {result_query}")
print("重排序后的文档:")
for i, doc in enumerate(reranked_docs, 1):
    print(f"{i}. {doc}")
```

### 输出示例

```
原始查询: 什么是人工智能？
重排序后的文档:
1. 人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。
2. 机器学习是人工智能的一个子集，通过算法让计算机从数据中学习。
3. 自然语言处理是人工智能的一个领域，专注于计算机与人类语言的交互。
```

## LLMbased_Reranker 使用方法

### 基本配置

```python
config = {
    "topk": 3
}
```

### 初始化和使用

```python
from sage.libs.rag.reranker import LLMbased_Reranker

# 初始化 LLM 重排序器
reranker = LLMbased_Reranker(config, model_name="BAAI/bge-reranker-v2-gemma")

# 使用方法与 BGEReranker 相同
query = "Python 中如何处理异常？"
documents = [
    "Python 使用 try-except 语句来处理异常。",
    "Java 中的异常处理使用 try-catch 块。",
    "在 Python 中，finally 块总是会执行。",
    "异常是程序运行时发生的错误。",
    "Python 提供了多种内置异常类型。"
]

input_data = (query, documents)
result_query, reranked_docs = reranker.execute(input_data)

print(f"查询: {result_query}")
print("LLM 重排序结果:")
for i, doc in enumerate(reranked_docs, 1):
    print(f"{i}. {doc}")
```
## 集成到 SAGE 管道中

```python
from sage.core.pipeline import Pipeline
from sage.libs.rag.reranker import BGEReranker

# 创建重排序组件
reranker_config = {
    "model_name": "BAAI/bge-reranker-v2-m3",
    "topk": 3
}
reranker = BGEReranker(reranker_config)

# 集成到管道中
pipeline = Pipeline()
pipeline.add_component("reranker", reranker)

# 运行管道
result = pipeline.run({"query": query, "documents": documents})
```