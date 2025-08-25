# SAGE 检索器使用指南

本指南介绍如何在 SAGE 系统中使用 ChromaDb 构建的Operator算子 ChromaRetriever 进行检索。

---

## 1. ChromaRetriever 向量检索

### 初始化检索器

```python
from sage.libs.rag.retriever import ChromaRetriever

config = {
    "dimension": 384,  # 向量维度
    "top_k": 5,        # 返回最相关文档数
    "embedding": {
        "method": "default",
        "model": "sentence-transformers/all-MiniLM-L6-v2"
    },
    "chroma": {
        "persist_path": "./chroma_qa_database",
        "collection_name": "qa_knowledge_base",
        "knowledge_file": "data/qa_knowledge_base.txt"
    }
}
retriever = ChromaRetriever(config)
```

### 添加文档到索引

```python
documents = [
    "ChromaDB是一个开源的向量数据库。",
    "SAGE支持多种检索方式，包括密集向量检索和BM25。"
]
doc_ids = ["doc1", "doc2"]
retriever.add_documents(documents, doc_ids)
```

### 执行检索

```python
query = "什么是ChromaDB？"
result = retriever.execute(query)
print(result["results"])
```

字典输入：

```python
query_dict = {"question": "SAGE有哪些检索方式？"}
result = retriever.execute(query_dict)
print(result["results"])
```

### 获取集合信息

```python
info = retriever.get_collection_info()
print(info)
```

### 索引保存与加载

```python
retriever.save_index("my_index_config.json")
retriever.load_index("my_index_config.json")
```

---