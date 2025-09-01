# 有界流处理 (Limited Streaming)

> 处理固定大小的数据集，适合离线批量分析和一次性计算任务。

有界流处理模拟真实世界中的 **批量数据分析** 场景，如日志分析、报表生成、数据迁移等。它强调完整性和确定性，是构建可靠数据处理系统的基础模式。

## 技术架构

```mermaid
graph LR
    A[BatchFunction] --> B[map/filter/flatmap]
    B --> C[stateful operator]
    C --> D[sink]
    D --> E[自动结束]
```

---

## 示例1：WordCount 批处理

WordCount（词频统计）是大数据处理领域的经典示例，它通过统计文本中每个单词出现的次数，展示了完整的数据处理流程：数据读取、清洗、转换、聚合和输出。

在批处理模式下，WordCount处理固定的文本数据集，非常适合离线分析、报告生成和数据挖掘等场景。

### 数据源定义

以下示例来自 [`examples/tutorials/core-api/wordcount_batch_example.py`](https://github.com/intellistream/SAGE/blob/main/examples/tutorials/core-api/wordcount_batch_example.py)：

```python
from sage.core.api.function.batch_function import BatchFunction

class TextDataBatch(BatchFunction):
    """文本数据批处理源 - 提供固定的文本数据集"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sentences = [
            "hello world sage framework",
            "this is a streaming data processing example",
            "lambda functions make the code much cleaner",
            "word count is a classic big data example",
            "sage provides powerful stream processing capabilities"
        ]
        self.counter = 0

    def execute(self):
        """返回下一个句子，如果没有更多句子则返回None"""
        if self.counter >= len(self.sentences):
            return None  # 返回None表示批处理完成

        sentence = self.sentences[self.counter]
        self.counter += 1
        return sentence
```

### 批处理管道

```python
from sage.core.api.local_environment import LocalEnvironment
from collections import Counter

def main():
    """运行有界流WordCount示例"""
    # 创建本地环境
    env = LocalEnvironment("batch_wordcount")
    
    # 设置日志级别为WARNING以减少输出噪音
    env.set_console_log_level("WARNING")

    # 全局词汇计数器
    word_counts = Counter()
    total_processed = 0

    def update_word_count(words_with_count):
        """更新全局词汇计数"""
        nonlocal word_counts, total_processed
        word, count = words_with_count
        word_counts[word] += count
        total_processed += count
        return words_with_count

    # 构建批处理管道
    result = (env
        .from_batch(TextDataBatch)                        # 批数据源

        # 数据清洗和预处理
        .map(lambda sentence: sentence.lower())           # 转小写
        .map(lambda sentence: sentence.strip())           # 去除首尾空白
        .filter(lambda sentence: len(sentence) > 0)       # 过滤空字符串

        # 分词处理
        .flatmap(lambda sentence: sentence.split())       # 按空格分词
        .filter(lambda word: len(word) > 2)               # 过滤长度小于3的词
        .map(lambda word: word.replace(",", "").replace(".", ""))  # 去除标点

        # 词汇统计
        .map(lambda word: (word, 1))                      # 转换为(word, count)格式
        .map(update_word_count)                           # 更新计数器
        .sink(lambda x: None)                            # 添加sink确保数据流完整
    )

    print("🚀 Starting Batch WordCount Example")

    try:
        # 提交并运行批处理作业
        env.submit()
        import time
        time.sleep(2)  # wait for batch processing to complete

        # 打印最终统计结果
        print("\n📊 Final Word Count Results:")
        print("=" * 60)
        for word, count in word_counts.most_common():
            print(f"{word:20}: {count:3d}")
        print("=" * 60)
        print(f"Total words processed: {total_processed}")

    except Exception as e:
        print(f"❌ 批处理执行失败: {str(e)}")
    finally:
        env.close()

if __name__ == "__main__":
    main()
```

### 使用Lambda函数的简化实现

对于简单的处理逻辑，可以直接使用lambda函数：

```python
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.batch_function import BatchFunction

class SimpleBatch(BatchFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data = ["hello world", "sage framework", "batch processing"]
        self.counter = 0
    
    def execute(self):
        if self.counter >= len(self.data):
            return None
        text = self.data[self.counter]
        self.counter += 1
        return text

def simple_pipeline():
    env = LocalEnvironment("simple_batch")
    
    (env
        .from_batch(SimpleBatch)
        .map(lambda x: x.upper())           # 转大写
        .map(lambda x: f"Processed: {x}")   # 添加前缀
        .sink(lambda x: print(x))           # 打印结果
    )
    
    env.submit(autostop=True)
```

### 关键技术特点

#### 1. **批量状态累积**
```python
word_counts = Counter()  # 全局词频计数器
total_processed = 0      # 处理总数计数器
```

- 使用 `nonlocal` 关键字访问外部作用域变量
- `Counter` 对象自动处理词频统计
- 所有数据处理完成后才输出最终结果

#### 2. **确定性处理流程**
```python
.from_batch(TextDataBatch)  # 固定数据集
.sink(lambda x: None)       # 必须添加sink触发执行
```

- 与无界流不同，批处理有明确的开始和结束
- 数据源返回 `None` 时自动结束处理
- 必须使用 `.sink()` 确保管道完整执行

---

## 示例2：RAG问答批处理

在第一个WordCount示例展示了基础的文本处理和统计功能后，我们进入一个更复杂的应用场景：基于检索增强生成（RAG）的问答系统。

这个示例演示了如何使用SAGE框架构建智能问答管道，包括问题批量处理、知识检索、提示词生成和大模型回答等关键组件的协作。

### 技术架构

```mermaid
graph LR
    A[问题文件] --> B[QABatch]
    B --> C[BiologyRetriever]
    C --> D[知识库检索]
    D --> E[QAPromptor]
    E --> F[OpenAIGenerator]
    F --> G[TerminalSink]
    
    H[MemoryService] --> D
    I[配置文件] --> C
    I --> E
    I --> F
```

### RAG批处理数据源

```python
from sage.core.api.function.batch_function import BatchFunction

class QABatch(BatchFunction):
    """QA批处理数据源：从配置文件中读取数据文件并逐行返回"""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.data_path = config["data_path"]
        self.counter = 0
        self.questions = []
        self._load_questions()

    def _load_questions(self):
        """从文件加载问题"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as file:
                self.questions = [line.strip() for line in file.readlines() if line.strip()]
        except Exception as e:
            print(f"Error loading file {self.data_path}: {e}")
            self.questions = [
                "什么是机器学习？",
                "深度学习有什么应用？",
                "如何开始学习Python？"
            ]

    def execute(self):
        """返回下一个问题，如果没有更多问题则返回None"""
        if self.counter >= len(self.questions):
            return None  # 返回None表示批处理完成

        question = self.questions[self.counter]
        self.counter += 1
        return question
```

### RAG批处理管道

```python
from sage.core.api.local_environment import LocalEnvironment
from sage.libs.rag.generator import OpenAIGenerator
from sage.libs.rag.promptor import QAPromptor
from sage.libs.io_utils.sink import TerminalSink
from sage.common.utils.config.loader import load_config

def rag_batch_pipeline():
    """创建并运行RAG批处理管道"""
    env = LocalEnvironment("rag_batch")

    # 配置
    config = {
        "source": {
            "data_path": "[examples/data/sample/question.txt](https://github.com/intellistream/SAGE/blob/main/examples/data/sample/question.txt)"
        },
        "promptor": {
            "platform": "local"
        },
        "generator": {
            "vllm": {
                "api_key": "your-api-key",
                "method": "openai",
                "model_name": "gpt-3.5-turbo",
                "base_url": "https://api.openai.com/v1",
                "temperature": 0.7
            }
        },
        "sink": {
            "platform": "local"
        }
    }

    # 构建数据处理流程
    (env
        .from_batch(QABatch, config["source"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )

    env.submit(autostop=True)
    print("RAG批处理完成")

if __name__ == "__main__":
    rag_batch_pipeline()
```

---

## 代码关键细节解析

前面展示了两个不同复杂度的批处理示例，现在我们深入分析实现这些功能的关键技术细节。

#### 1. 状态管理机制
```python
def update_word_count(words_with_count):
    nonlocal word_counts, total_processed  # 关键：访问外部作用域变量
    word, count = words_with_count
    word_counts[word] += count              # Counter对象自动处理键不存在的情况
    total_processed += count
    return words_with_count                 # 重要：必须返回数据继续流转
```

设计要点：

- `nonlocal` 声明允许修改外部作用域的变量
- `Counter()` 对象在键不存在时自动初始化为0
- 函数必须返回数据以保持流式处理的连续性

#### 2. 数据源生命周期
```python
def execute(self):
    if self.counter >= len(self.questions):
        return None  # 这是唯一的结束信号
    # ...处理逻辑
```

重要约定：返回 `None` 是告诉 SAGE 框架批处理已完成的**唯一方式**，任何其他返回值都会被视为有效数据。

#### 3. 服务注册机制
```python
env.register_service("memory_service", memory_service_factory)
```

框架特性：
- SAGE支持服务注册，实现组件间的依赖注入
- `self.call_service["memory_service"]` 可访问注册的服务
- memory_service_factory负责创建和配置知识库连接

---

## 小结

有界流处理通过 **固定数据源** 、 **明确结束信号** 和 **状态累积** 机制，实现 **可复现** 、 **自动结束** 的批量数据处理流程。

关键特点：

- **确定性**：相同输入产生相同输出，便于调试和测试
- **完整性**：确保所有数据都被处理，不会遗漏
- **自动结束**：数据源返回 `None` 时管道自动停止
- **状态聚合**：支持跨数据项的状态累积和最终结果汇总
- **服务集成**：支持复杂的依赖注入和组件协作

适用场景：数据分析、报表生成、模型训练、批量数据处理、批量RAG问答等需要处理完整数据集的场景。
