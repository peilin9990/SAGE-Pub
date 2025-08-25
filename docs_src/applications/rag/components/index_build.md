# SAGE 本地向量索引使用指南

本指南以Chroma向量数据库为例介绍如何在 SAGE 系统中创建和查询本地向量索引，实现高效的知识检索。


## 1. 数据加载与分块

使用 `TextLoader` 加载原始文本，`CharacterSplitter` 按指定分隔符（如段落 `\n\n`）进行分块。

```python
from sage.libs.rag.document_loaders import TextLoader
from sage.libs.rag.chunk import CharacterSplitter

loader = TextLoader('data/qa_knowledge_base.txt')
document = loader.load()

splitter = CharacterSplitter({"separator": "\n\n"})
chunks = splitter.execute(document)

chunk_docs = [
    {"content": chunk, "metadata": {"chunk": idx+1, "source": "data/qa_knowledge_base.txt"}}
    for idx, chunk in enumerate(chunks)
]
```

## 2. 构建向量索引

使用 SentenceTransformer 生成嵌入，写入 ChromaDB 本地数据库。

```python
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
client = chromadb.PersistentClient(path="./chroma_qa_database")
collection = client.create_collection(
    name="qa_knowledge_base",
    metadata={"index_type": "flat"}  # 可选: "flat", "hnsw"
)

texts = [c["content"] for c in chunk_docs]
embeddings = model.encode(texts).tolist()
ids = [f"chunk_{i}" for i in range(len(chunk_docs))]
metadatas = [c["metadata"] for c in chunk_docs]

collection.add(
    embeddings=embeddings,
    documents=texts,
    metadatas=metadatas,
    ids=ids
)
```

## 3. 相似度检索

通过自然语言查询，自动生成嵌入并检索最相关的文本块。

```python
query = "什么是ChromaDB"
query_embedding = model.encode([query]).tolist()
results = collection.query(query_embeddings=query_embedding, n_results=3)

for i, doc in enumerate(results['documents'][0]):
    print(f"{i+1}. {doc[:100]}...")
```

## 4. 索引类型说明

- 默认索引类型为 `"flat"`，支持 `"hnsw"` 等高性能索引，可在 `create_collection` 时通过 `metadata` 参数设置。
- 示例：`collection = client.create_collection(name=..., metadata={"index_type": "hnsw"})`

---
