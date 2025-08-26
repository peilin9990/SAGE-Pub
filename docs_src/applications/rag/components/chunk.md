# RAG文本分块模块使用说明

本文档介绍了`sage.libs.rag.chunk`模块中文本分块器的使用方法。该模块提供了多种文本分块策略，用于将长文本分割成适合RAG（检索增强生成）系统处理的小块。

## 概述

文本分块是RAG系统中的关键预处理步骤，它将长文档分割成合适大小的块，以便：
- 提高检索效率
- 控制输入长度
- 保持语义连贯性
- 支持重叠处理

该模块包含两个主要的分块器类：
1. **CharacterSplitter** - 字符级分块器
2. **SentenceTransformersTokenTextSplitter** - 基于Transformer模型的Token分块器

## 分块器详细说明

### 1. CharacterSplitter - 字符级分块器

这是一个简单而灵活的分块器，支持字符级分割和自定义分隔符分割。

#### 特性
- 支持字符级别的精确分块
- 可配置重叠区域
- 支持自定义分隔符
- 轻量级，无需额外模型

#### 配置参数

```python
config = {
    "chunk_size": 512,      # 每块的字符数（默认512）
    "overlap": 128,         # 重叠字符数（默认128）
    "separator": None       # 自定义分隔符（可选）
}
```

#### 基本使用

```python
from sage.libs.rag.chunk import CharacterSplitter

# 初始化分块器
config = {
    "chunk_size": 500,
    "overlap": 100
}
splitter = CharacterSplitter(config)

# 准备文档数据
document = {
    "content": "这是一个很长的文档内容，需要被分割成多个小块以便处理。" * 20,
    "metadata": {"title": "示例文档", "author": "张三"}
}

# 执行分块
chunks = splitter.execute(document)
print(f"分块数量: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"块 {i+1}: {chunk[:50]}...")
```

#### 使用自定义分隔符

```python
# 按段落分割
config = {
    "separator": "\n\n"  # 使用双换行符作为分隔符
}
paragraph_splitter = CharacterSplitter(config)

document = {
    "content": "第一段内容。\n\n第二段内容。\n\n第三段内容。"
}
chunks = paragraph_splitter.execute(document)
# 结果：['第一段内容。', '第二段内容。', '第三段内容。']
```

```python
# 按句子分割
config = {
    "separator": "。"  # 使用句号作为分隔符
}
sentence_splitter = CharacterSplitter(config)

document = {
    "content": "这是第一句。这是第二句。这是第三句。"
}
chunks = sentence_splitter.execute(document)
# 结果：['这是第一句', '这是第二句', '这是第三句']
```

#### 重叠机制说明

```python
# 演示重叠机制
config = {
    "chunk_size": 10,  # 每块10个字符
    "overlap": 3       # 重叠3个字符
}
splitter = CharacterSplitter(config)

document = {"content": "0123456789ABCDEFGHIJ"}
chunks = splitter.execute(document)

# 输出结果：
# 块1: 0123456789 (0-9)
# 块2: 789ABCDEFG (7-16)  # 与块1重叠3个字符(789)
# 块3: EFGHIJ     (16-21) # 与块2重叠3个字符(EFG)
```

### 2. SentenceTransformersTokenTextSplitter - Token分块器

这是一个基于Transformer模型的高级分块器，使用模型的tokenizer进行精确的token级分割。

#### 特性
- 基于预训练模型的tokenizer
- 精确的token计数
- 保持模型兼容性
- 支持多种Transformer模型

#### 依赖要求

```bash
pip install sentence-transformers transformers torch
```

#### 配置参数

```python
config = {
    "chunk": {
        "model_name": "sentence-transformers/all-mpnet-base-v2",  # 模型名称
        "chunk_size": 512,      # 每块的token数（默认512）
        "chunk_overlap": 50     # 重叠token数（默认50）
    }
}
```

#### 基本使用

```python
from sage.libs.rag.chunk import SentenceTransformersTokenTextSplitter

# 配置
config = {
    "chunk": {
        "chunk_size": 128,
        "chunk_overlap": 20,
        "model_name": "sentence-transformers/all-mpnet-base-v2"
    }
}

# 初始化分块器（会自动下载模型）
splitter = SentenceTransformersTokenTextSplitter(config)

# 执行分块
text = "This is a long document that needs to be split into smaller chunks for processing. " * 10
chunks = splitter.execute(text)

print(f"原文长度: {len(text)} 字符")
print(f"分块数量: {len(chunks)}")
for i, chunk in enumerate(chunks):
    print(f"块 {i+1}: {chunk[:60]}...")
```

#### 支持的模型

```python
# 常用模型配置
models = {
    # 英文模型
    "all-mpnet-base-v2": "sentence-transformers/all-mpnet-base-v2",
    "all-MiniLM-L6-v2": "sentence-transformers/all-MiniLM-L6-v2",
    
    # 中文模型
    "paraphrase-multilingual": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    
    # BERT系列
    "bert-base": "bert-base-uncased",
    "bert-chinese": "bert-base-chinese"
}

# 使用中文模型
config = {
    "chunk": {
        "model_name": "bert-base-chinese",
        "chunk_size": 256,
        "chunk_overlap": 32
    }
}
```

#### Token级分块详解

```python
# 演示token级分块的精确性
config = {
    "chunk": {
        "chunk_size": 8,    # 每块8个token
        "chunk_overlap": 2, # 重叠2个token
        "model_name": "sentence-transformers/all-mpnet-base-v2"
    }
}

splitter = SentenceTransformersTokenTextSplitter(config)
text = "This is a test sentence to be split into smaller chunks."

chunks = splitter.execute(text)

# 可以看到详细的分块过程：
# Input IDs: [101, 2023, 2003, 1037, 3231, 6251, 2000, 2022, 3975, 2046, 3760, 9060, 1012, 102]
# Start Index: 0
# 块1: [CLS] This is a test sentence to [SEP]
# Start Index: 6  # 8-2=6 (chunk_size - overlap)
# 块2: sentence to be split into smaller
# ...
```

## 完整使用示例

### RAG文档处理流水线

```python
from sage.libs.rag.chunk import CharacterSplitter, SentenceTransformersTokenTextSplitter

class DocumentProcessor:
    def __init__(self, chunk_strategy="character"):
        if chunk_strategy == "character":
            self.splitter = CharacterSplitter({
                "chunk_size": 1000,
                "overlap": 200,
                "separator": None
            })
        elif chunk_strategy == "token":
            self.splitter = SentenceTransformersTokenTextSplitter({
                "chunk": {
                    "chunk_size": 512,
                    "chunk_overlap": 64,
                    "model_name": "sentence-transformers/all-mpnet-base-v2"
                }
            })
    
    def process_document(self, document):
        """处理单个文档"""
        if isinstance(document, dict):
            # CharacterSplitter格式
            chunks = self.splitter.execute(document)
            return [{
                "content": chunk,
                "metadata": document.get("metadata", {}),
                "chunk_id": i
            } for i, chunk in enumerate(chunks)]
        else:
            # SentenceTransformersTokenTextSplitter格式
            chunks = self.splitter.execute(document)
            return [{
                "content": chunk,
                "chunk_id": i
            } for i, chunk in enumerate(chunks)]
    
    def process_multiple_documents(self, documents):
        """处理多个文档"""
        all_chunks = []
        for doc_id, document in enumerate(documents):
            chunks = self.process_document(document)
            for chunk in chunks:
                chunk["document_id"] = doc_id
                all_chunks.append(chunk)
        return all_chunks

# 使用示例
processor = DocumentProcessor("character")

documents = [
    {
        "content": "第一篇文档的内容..." * 100,
        "metadata": {"title": "文档1", "category": "技术"}
    },
    {
        "content": "第二篇文档的内容..." * 150,
        "metadata": {"title": "文档2", "category": "科学"}
    }
]

all_chunks = processor.process_multiple_documents(documents)
print(f"总共生成了 {len(all_chunks)} 个文档块")
```

### 自适应分块策略

```python
class AdaptiveChunker:
    def __init__(self):
        self.char_splitter = CharacterSplitter({
            "chunk_size": 1000,
            "overlap": 100
        })
        
        self.token_splitter = SentenceTransformersTokenTextSplitter({
            "chunk": {
                "chunk_size": 256,
                "chunk_overlap": 32,
                "model_name": "sentence-transformers/all-MiniLM-L6-v2"
            }
        })
    
    def choose_strategy(self, text):
        """根据文本特征选择分块策略"""
        if len(text) < 1000:
            return "character"  # 短文本用字符分块
        elif any(lang in text for lang in ["中文", "日文", "한국어"]):
            return "character"  # 非英文用字符分块
        else:
            return "token"     # 长英文用token分块
    
    def adaptive_chunk(self, document):
        content = document.get("content", "") if isinstance(document, dict) else document
        strategy = self.choose_strategy(content)
        
        if strategy == "character":
            if isinstance(document, dict):
                return self.char_splitter.execute(document)
            else:
                doc_dict = {"content": document}
                return self.char_splitter.execute(doc_dict)
        else:
            if isinstance(document, dict):
                content = document["content"]
            else:
                content = document
            return self.token_splitter.execute(content)

# 使用自适应分块
chunker = AdaptiveChunker()

# 中文文档 - 使用字符分块
chinese_doc = {"content": "这是一篇中文文档" * 200}
chunks1 = chunker.adaptive_chunk(chinese_doc)

# 英文文档 - 使用token分块
english_text = "This is an English document " * 200
chunks2 = chunker.adaptive_chunk(english_text)
```

### 分块质量评估

```python
def evaluate_chunks(chunks, original_text):
    """评估分块质量"""
    stats = {
        "total_chunks": len(chunks),
        "avg_length": sum(len(chunk) for chunk in chunks) / len(chunks),
        "min_length": min(len(chunk) for chunk in chunks),
        "max_length": max(len(chunk) for chunk in chunks),
        "coverage": sum(len(chunk) for chunk in chunks) / len(original_text)
    }
    
    print("分块质量评估:")
    print(f"- 总块数: {stats['total_chunks']}")
    print(f"- 平均长度: {stats['avg_length']:.1f}")
    print(f"- 最短块: {stats['min_length']}")
    print(f"- 最长块: {stats['max_length']}")
    print(f"- 覆盖率: {stats['coverage']:.2%}")
    
    return stats

# 评估示例
text = "示例文本内容" * 1000
splitter = CharacterSplitter({"chunk_size": 200, "overlap": 50})
chunks = splitter.execute({"content": text})
evaluate_chunks(chunks, text)
```

## 配置建议

### 根据用途选择配置

#### 1. 问答系统
```python
# 短问答 - 精确匹配
qa_config = {
    "chunk_size": 256,
    "overlap": 32
}

# 长问答 - 更多上下文
long_qa_config = {
    "chunk_size": 512,
    "overlap": 64
}
```

#### 2. 摘要系统
```python
# 摘要 - 较大块保持完整性
summary_config = {
    "chunk_size": 1024,
    "overlap": 128
}
```

#### 3. 代码文档
```python
# 代码 - 按函数/类分割
code_config = {
    "separator": "\n\nclass ",  # 按类分割
    "chunk_size": 2000,
    "overlap": 0  # 代码通常不需要重叠
}
```

#### 4. 学术论文
```python
# 论文 - 按段落分割
paper_config = {
    "separator": "\n\n",  # 按段落分割
    "chunk_size": 800,
    "overlap": 100
}
```



