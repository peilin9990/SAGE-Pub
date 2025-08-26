# RAG提示词生成模块使用说明

本文档介绍了`sage.libs.rag.promptor`模块中各种提示词生成器的使用方法。该模块提供了专门用于RAG（检索增强生成）系统的提示词模板和生成器。

## 概述

该模块包含三个主要的提示词生成器类：
1. **QAPromptor** - 问答式提示词生成器
2. **SummarizationPromptor** - 摘要式提示词生成器  
3. **QueryProfilerPromptor** - 查询分析提示词生成器

所有类都继承自`MapFunction`基类，支持链式调用和管道处理。

## 提示词模板

### 内置模板

#### QA问答模板
```jinja2
Instruction:
You are an intelligent assistant with access to a knowledge base. Answer the question below with reference to the provided context.
Only give me the answer and do not output any other words.
{%- if external_corpus %}
Relevant corpus for the current question:
{{ external_corpus }}
{%- endif %}
```

#### 摘要模板
```jinja2
Instruction:
You are an intelligent assistant. Summarize the content provided below in a concise and clear manner.
Only provide the summary and do not include any additional information.
{%- if external_corpus %}
Content to summarize:
{{ external_corpus }}
{%- endif %}
```

#### 查询分析模板
用于分析查询复杂度、是否需要多文档推理等特性的模板。

## 详细使用方法

### 1. QAPromptor - 问答提示词生成器

这是最核心的提示词生成器，用于生成问答式对话的系统提示词和用户提示词。

#### 基本使用

```python
from sage.libs.rag.promptor import QAPromptor

# 基本配置
config = {}

# 初始化生成器
qa_promptor = QAPromptor(config)

# 方式1：查询 + 外部语料库
data = ("什么是人工智能？", ["人工智能是计算机科学的一个分支", "AI可以模拟人类智能"])
result = qa_promptor.execute(data)

# 方式2：仅查询
data = "什么是人工智能？"
result = qa_promptor.execute(data)
```

#### 自定义模板配置

```python
# 使用自定义模板
custom_config = {
    'template': '''你是一个专业的AI助手。基于以下背景信息回答问题：
{%- if external_corpus %}
背景信息：
{{ external_corpus }}
{%- endif %}
请提供准确、简洁的答案。'''
}

qa_promptor = QAPromptor(custom_config)
```

#### 启用数据分析功能

```python
# 启用提示词数据记录和分析
qa_promptor = QAPromptor(config, enable_profile=True)

# 数据会自动保存到 .sage_states/promptor_data/ 目录
# 文件格式：promptor_data_{timestamp}.json
```

#### 输出格式

```python
# 返回格式：[query, prompt]
[
    "什么是人工智能？",
    [
        {
            "role": "system",
            "content": "You are an intelligent assistant with access to a knowledge base..."
        },
        {
            "role": "user", 
            "content": "Question: 什么是人工智能？"
        }
    ]
]
```

### 2. SummarizationPromptor - 摘要提示词生成器

专门用于生成文本摘要任务的提示词。

#### 基本使用

```python
from sage.libs.rag.promptor import SummarizationPromptor

# 初始化
config = {}
sum_promptor = SummarizationPromptor(config)

# 输入：(查询, 要摘要的文本列表)
data = (
    "请总结以下内容",
    [
        "人工智能是计算机科学的一个重要分支...",
        "机器学习是人工智能的核心技术之一...",
        "深度学习近年来取得了突破性进展..."
    ]
)

result = sum_promptor.execute(data)
```

#### 输出格式

```python
# 返回摘要提示词列表
[
    {
        "role": "system",
        "content": "You are an intelligent assistant. Summarize the content provided below..."
    },
    {
        "role": "user",
        "content": "Question: 请总结以下内容"
    }
]
```

### 3. QueryProfilerPromptor - 查询分析器

用于分析查询的复杂度和特征，帮助优化RAG管道。

#### 基本使用

```python
from sage.libs.rag.promptor import QueryProfilerPromptor

# 配置元数据
config = {
    "metadata": "The dataset consists of multiple chunks of information from Fortune 500 companies",
    "chunk_size": 1024
}

profiler = QueryProfilerPromptor(config)

# 分析查询
query = "特朗普是如何赚到第一个100万美元的？"
result = profiler.execute(query)
```

#### 期望的分析结果

```json
{
  "need_joint_reasoning": true,
  "complexity": "High",
  "need_summarization": true, 
  "summarization_length": 150,
  "n_info_items": 3
}
```

## 完整使用示例

### RAG问答流水线

```python
from sage.libs.rag.promptor import QAPromptor, QueryProfilerPromptor

# 1. 初始化组件
config = {}
qa_promptor = QAPromptor(config, enable_profile=True)
profiler = QueryProfilerPromptor({
    "metadata": "企业财务报告数据库",
    "chunk_size": 1024
})

# 2. 查询分析
query = "苹果公司2023年Q4的营收情况如何？"
profile_result = profiler.execute(query)
print("查询分析结果:", profile_result)

# 3. 检索相关文档（模拟）
retrieved_docs = [
    "苹果公司2023年第四季度营收达到895亿美元...",
    "相比2022年同期，苹果Q4营收增长了2.1%...",
    "iPhone销售额在Q4占总营收的52%..."
]

# 4. 生成问答提示词
qa_data = (query, retrieved_docs)
qa_result = qa_promptor.execute(qa_data)

print("生成的提示词:")
for msg in qa_result[1]:
    print(f"{msg['role']}: {msg['content'][:100]}...")
```

### 摘要生成流水线

```python
from sage.libs.rag.promptor import SummarizationPromptor

# 初始化摘要生成器
sum_promptor = SummarizationPromptor({})

# 长文本摘要
long_documents = [
    "2023年人工智能领域取得了重大突破，ChatGPT的发布标志着大语言模型时代的到来...",
    "各大科技公司纷纷投入AI研发，Google发布了Bard，百度推出了文心一言...",
    "AI技术在各行各业都有应用，从医疗诊断到自动驾驶，从金融风控到教育辅导..."
]

sum_data = ("总结2023年AI发展", long_documents)
sum_result = sum_promptor.execute(sum_data)

print("摘要提示词:", sum_result[0]['content'])
```

### 多模式组合使用

```python
class RAGPipeline:
    def __init__(self):
        self.qa_promptor = QAPromptor({}, enable_profile=True)
        self.sum_promptor = SummarizationPromptor({})
        self.profiler = QueryProfilerPromptor({
            "metadata": "综合知识库",
            "chunk_size": 1024
        })
    
    def process_query(self, query, documents, use_summarization=False):
        # 1. 分析查询特征
        profile = self.profiler.execute(query)
        
        # 2. 根据分析结果决定是否需要摘要
        if use_summarization or self._need_summarization(profile):
            # 先生成摘要
            sum_prompt = self.sum_promptor.execute((
                f"请摘要以下与'{query}'相关的内容", 
                documents
            ))
            # 这里可以调用LLM获取摘要结果
            summarized_docs = ["摘要后的内容..."]  # 模拟摘要结果
            final_docs = summarized_docs
        else:
            final_docs = documents
        
        # 3. 生成最终的QA提示词
        qa_prompt = self.qa_promptor.execute((query, final_docs))
        
        return {
            'profile': profile,
            'final_prompt': qa_prompt,
            'used_summarization': use_summarization
        }
    
    def _need_summarization(self, profile):
        # 根据profile结果判断是否需要摘要
        return profile[0].get('content', {}).get('need_summarization', False)

# 使用示例
pipeline = RAGPipeline()
result = pipeline.process_query(
    "什么是量子计算？",
    ["量子计算相关文档1", "量子计算相关文档2"],
    use_summarization=True
)
```

## 配置选项

### QAPromptor配置

```python
config = {
    # 自定义提示词模板
    'template': '''自定义的Jinja2模板内容''',
    
    # 其他配置项...
}

# enable_profile参数控制是否启用数据记录
qa_promptor = QAPromptor(config, enable_profile=True)
```

### QueryProfilerPromptor配置

```python
config = {
    'metadata': '数据集描述信息',
    'chunk_size': 1024,  # 分块大小
    # 其他元数据...
}
```