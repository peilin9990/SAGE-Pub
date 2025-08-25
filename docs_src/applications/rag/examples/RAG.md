# 基于 ChromaDB 的 RAG 问答系统说明文档

Retrieval Augmented Generation（RAG）是一种结合检索与生成的智能问答技术，广泛应用于大模型驱动的知识问答、智能客服等场景。RAG 系统通常包含两个核心部分：

- **索引（Indexing）**：处理文档数据数据，构建可检索的知识库。
- **检索与生成（Retrieval & Generation）**：在线根据用户问题检索相关内容，并生成答案。

---

## 典型流程

### 1. 索引阶段

- 加载原始数据（如 jsonl 问答对）。
- 配置检索器参数（如向量维度、top-k、embedding 方法等）。
- 构建知识库索引（ChromaDB）。

### 2. 检索与生成阶段

- 用户输入问题。
- 检索器根据问题在知识库中检索相关内容。
- Promptor 构建生成模型输入。
- 生成模型输出答案。
- 结果输出。

---

## 代码讲解

核心流程如下：

```python
def pipeline_run(config: dict) -> None:
    print("=== 启动基于 ChromaDB 的 RAG 问答系统 ===")
    env = LocalEnvironment()
    (
        env
        .from_batch(JSONLBatch, config["source"])
        .map(ChromaRetriever, config["retriever"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    env.submit()
    time.sleep(10)
    env.close()
    print("=== RAG 问答系统运行完成 ===")
```

- `LocalEnvironment`：流程编排环境，负责各模块的串联与运行。
- `from_batch`：加载批量数据。
- `map`：依次映射检索、prompt 构建、生成等模块。
- `sink`：输出结果。

入口代码：

```python
if __name__ == '__main__':
    config_path = './examples/config/config_qa_chroma.yaml'
    config = load_config(config_path)
    pipeline_run(config)
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

