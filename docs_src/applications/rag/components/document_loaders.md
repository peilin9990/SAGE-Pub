# RAG文档加载器使用说明

本文档介绍了`sage.libs.rag.document_loaders`模块中文档加载器的使用方法。该模块提供了用于加载和预处理各种格式文档的工具，是RAG（检索增强生成）系统的基础组件。

当前版本提供了`TextLoader`类，支持基本的文本文件加载功能，并为扩展其他格式奠定了基础。

## TextLoader - 文本文件加载器

### 概述

`TextLoader`是一个简单而实用的文本文件加载器，能够：
- 加载任意编码的文本文件
- 自动生成文档元数据
- 返回标准化的文档对象格式
- 支持错误处理和异常管理

### 类定义

```python
class TextLoader:
    def __init__(self, filepath: str, encoding: str = "utf-8", chunk_separator: str = None)
    def load(self) -> Dict
```

### 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `filepath` | str | 必需 | 要加载的文本文件路径 |
| `encoding` | str | "utf-8" | 文件编码格式 |
| `chunk_separator` | str | None | 预留参数，用于未来分块功能 |

### 基本使用

#### 简单文本加载

```python
from sage.libs.rag.document_loaders import TextLoader

# 基本用法
loader = TextLoader('data/sample.txt')
document = loader.load()

print("文档内容:", document["content"][:100] + "...")
print("文档元数据:", document["metadata"])
```

#### 指定编码格式

```python
# 加载不同编码的文件
loaders = {
    'utf8': TextLoader('data/utf8_file.txt', encoding='utf-8'),
    'gbk': TextLoader('data/gbk_file.txt', encoding='gbk'),
    'latin1': TextLoader('data/latin1_file.txt', encoding='latin-1')
}

documents = {}
for name, loader in loaders.items():
    try:
        documents[name] = loader.load()
        print(f"✓ 成功加载 {name} 编码文件")
    except UnicodeDecodeError:
        print(f"✗ {name} 编码解析失败")
```

### 返回格式

`load()`方法返回一个标准化的文档字典：

```python
{
    "content": "文件的完整文本内容",
    "metadata": {
        "source": "文件路径"
    }
}
```
