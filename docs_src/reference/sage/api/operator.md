### DenseRetriever

`DenseRetriever` 是一个基于向量检索的算子，它主要通过 **LTM（Long-Term Memory）** 进行信息检索。它继承自 `MapFunction`。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 包含了检索器的配置信息。
    * `config["ltm"]` (`bool` 或 `dict`): 如果为 `True` 或一个字典，表示启用 LTM 检索。如果是一个字典，它将作为 `ltm_config` 用于 LTM 检索的详细配置。
* **`**kwargs`**: 传递给基类 `MapFunction` 的额外参数。

#### 执行方法 (`execute`)

`execute` 方法执行实际的检索操作。

* **`data`** (`str`): 输入的查询字符串。
    * 如果 `data` 是一个元组，并且不为空，则取元组的第一个元素作为查询字符串。
* **返回** (`Tuple[str, List[str]]`): 一个包含原始查询字符串和检索到的块列表的元组。
    * **`input_query`** (`str`): 原始的输入查询。
    * **`chunks`** (`List[str]`): 从 LTM 中检索到的文本块列表。


---
### BM25sRetriever

`BM25sRetriever` 是一个基于 **BM25s 算法**的检索算子。它也继承自 `MapFunction`。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 包含了检索器的配置信息。
    * `config["bm25s_collection"]` (`str`): 必需参数，指定用于 BM25s 检索的集合名称。
    * `config["bm25s_config"]` (`dict`, 可选): BM25s 检索的额外配置参数，默认为空字典。
* **`**kwargs`**: 传递给基类 `MapFunction` 的额外参数。

#### 执行方法 (`execute`)

`execute` 方法执行实际的 BM25s 检索操作。

* **`data`** (`str`): 输入的查询字符串。
* **返回** (`Tuple[str, List[str]]`): 一个包含原始查询字符串和检索到的块列表的元组。
    * **`input_query`** (`str`): 原始的输入查询。
    * **`chunks`** (`List[str]`): 从 BM25s 中检索到的文本块列表。

本部分将继续介绍 `sage_libs.rag` 文件夹下定义的算子，这些算子主要用于检索增强生成（RAG）流程中的提示词工程环节。

---
### QAPromptor

`QAPromptor` 是一个提示词生成算子，它根据用户查询和外部语料库生成问答（QA）风格的提示词。它继承自 `MapFunction`，旨在为问答模型准备必要的提示词结构。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 包含提示词生成器配置信息的字典（例如，模型详情等）。
* **`**kwargs`**: 传递给基类 `MapFunction` 的额外参数。

#### 属性

* **`config`** (`dict`): 存储用于初始化提示词生成器的配置。
* **`prompt_template`** (`jinja2.Template`): 用于生成系统提示词的模板，通常包含上下文或指令。默认使用 `QA_prompt_template`。

#### 执行方法 (`execute`)

`execute` 方法生成 ChatGPT 风格的提示词（包含 `system` 和 `user` 两条消息）。

* **`data`**: 输入数据，支持以下两种格式：
    * `Tuple[str, Union[List[str], str]]`: 元组，第一个元素是查询字符串 (`query`)，第二个元素是外部语料库，可以是字符串列表或单个字符串。
    * `str`: 单个查询字符串 (`query`)。
* **返回** (`list`): 一个列表，包含：
    * 原始查询字符串。
    * 一个包含 `system` 和 `user` 消息的提示词列表。
        * `system_prompt` (`dict`): 包含 `role` (固定为 "system") 和 `content`。如果提供了外部语料库，内容将基于 `prompt_template` 渲染；否则，将使用默认的通用系统提示。
        * `user_prompt` (`dict`): 包含 `role` (固定为 "user") 和 `content` (格式为 "Question: {query}")。

---
### SummarizationPromptor

`SummarizationPromptor` 是一个提示词生成算子，它根据用户查询和外部语料库生成摘要风格的提示词。它继承自 `MapFunction`。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 包含提示词生成器配置信息的字典（例如，模型详情等）。

#### 属性

* **`config`** (`dict`): 存储用于初始化提示词生成器的配置。
* **`prompt_template`** (`jinja2.Template`): 用于生成系统提示词的模板，通常包含上下文或指令。默认使用 `summarization_prompt_template`。

#### 执行方法 (`execute`)

`execute` 方法为输入的查询和外部语料库生成摘要风格的提示词。

* **`data`**: 输入数据，预期为一个元组 `(query, external_corpus_list)`，其中：
    * `query` (`str`): 用户查询字符串。
    * `external_corpus_list` (`List[str]`): 外部语料库的字符串列表。
* **返回** (`list`): 一个包含两个提示词的列表：
    * `system_prompt` (`dict`): 一个基于模板和外部语料库数据的系统提示词。
    * `user_prompt` (`dict`): 一个包含待摘要问题的用户提示词。

---
### OpenAIGenerator

`OpenAIGenerator` 是一个生成器算子，用于与指定的 OpenAI 模型接口，根据输入数据生成响应。它继承自 `GeneratorFunction`。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 包含生成器配置的字典，包括：
    * `method` (`str`): 生成模型的方法（例如，"openai"）。
    * `model_name` (`str`): 要使用的 OpenAI 模型名称。
    * `base_url` (`str`): OpenAI API 的基础 URL。
    * `api_key` (`str`): OpenAI API 密钥，如果未提供，则尝试从环境变量 `ALIBABA_API_KEY` 获取。
* **`local_remote`**: 当前代码中未使用，可能是预留参数。
* **`**kwargs`**: 传递给基类 `GeneratorFunction` 的额外参数。

#### 属性

* **`config`** (`dict`): 生成器的配置信息。
* **`model`**: 通过 `apply_generator_model` 函数初始化的生成模型实例。
* **`num`** (`int`): 内部计数器，用于记录执行次数。

#### 执行方法 (`execute`)

`execute` 方法使用配置的模型根据输入数据生成响应。

* **`data`** (`list`): 输入数据列表。
    * 列表的第一个元素（如果存在）被视为用户查询 (`user_query`)。
    * 列表的第二个元素（如果存在）或整个列表（如果只有一个元素）被视为传递给模型的 `prompt`。
* **`**kwargs`**: 传递给模型生成方法的额外参数（例如 `temperature`、`max_tokens` 等）。
* **返回** (`Tuple[str, str]`): 一个元组，包含原始用户查询和模型生成的响应。
    * **`user_query`** (`str`): 原始的输入查询。
    * **`response`** (`str`): 模型生成的响应。

---
### OpenAIGeneratorWithHistory

`OpenAIGeneratorWithHistory` 是一个具有全局对话记忆的 OpenAI 生成器。它继承自 `StatefulFunction`，这意味着它能够维护并持久化对话历史。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 包含生成器配置的字典，与 `OpenAIGenerator` 类似，并额外支持：
    * `max_history_turns` (`int`, 可选): 要保留的最大对话轮次（用户和助手各算一轮），默认为 5。
* **`**kwargs`**: 传递给基类 `StatefulFunction` 的额外参数。

#### 属性

* **`config`** (`dict`): 生成器的配置信息。
* **`model`**: 通过 `apply_generator_model` 函数初始化的生成模型实例。
* **`dialogue_history`** (`List[str]`): 全局对话历史，按对话轮次记录字符串（每个元素是一个角色-内容字典）。
* **`history_turns`** (`int`): 要保留的最大对话轮次。
* **`num`** (`int`): 内部计数器，用于记录执行次数。

#### 执行方法 (`execute`)

`execute` 方法执行响应生成，并管理对话历史。

* **`data`** (`List`): 输入数据，预期格式为 `[user_query, prompt_dict]`。
    * `user_query` (`str`): 原始用户查询。
    * `prompt_dict` (`list`): 包含新对话轮次（通常是用户和系统消息）的字典列表。
* **`**kwargs`**: 传递给模型生成方法的额外参数。
* **返回** (`Tuple[str, str]`): 一个元组，包含原始用户查询和模型生成的响应。

#### 功能描述

`OpenAIGeneratorWithHistory` 的核心功能是在 `OpenAIGenerator` 的基础上增加了对话历史管理和状态持久化。它在每次执行时，会从 `dialogue_history` 中获取最近的对话轮次，并将其与当前的用户/系统提示词合并，形成完整的 `full_prompt` 发送给模型。模型生成响应后，该响应会被添加到对话历史中。为了保持历史的长度，它只会保留最近 N 轮的对话。此外，该算子会在每次 `execute` 后自动保存其状态（`dialogue_history`），确保对话的连续性。

#### 状态管理

* **`dialogue_history`**: 作为内部状态，用于记录对话的完整历史。
* **`load_function_state`**: 在初始化时加载函数状态，实现延迟恢复。
* **`save_function_state`**: 在每次 `execute` 后自动保存函数状态，并在 `save_state` 方法中手动触发。

---
### HFGenerator

`HFGenerator` 是一个生成器算子，用于与 Hugging Face 模型接口，根据输入数据生成响应。它继承自 `MapFunction`。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 包含生成器配置的字典，包括：
    * `method` (`str`): 生成模型的方法（例如，"huggingface"）。
    * `model_name` (`str`): 要使用的 Hugging Face 模型名称。
* **`**kwargs`**: 传递给基类 `MapFunction` 的额外参数。

#### 属性

* **`config`** (`dict`): 生成器的配置信息。
* **`model`**: 通过 `apply_generator_model` 函数初始化的生成模型实例。

#### 执行方法 (`execute`)

`execute` 方法使用配置的 Hugging Face 模型根据输入数据生成响应。

* **`data`** (`list`): 输入数据列表。
    * 列表的第一个元素（如果存在）被视为用户查询 (`user_query`)。
    * 列表的第二个元素（如果存在）或整个列表（如果只有一个元素）被视为传递给模型的 `prompt`。
* **`**kwargs`**: 传递给模型生成方法的额外参数（例如 `temperature`、`max_tokens` 等）。
* **返回** (`Tuple[str, str]`): 一个元组，包含原始用户查询和模型生成的响应。

---
### F1Evaluate

`F1Evaluate` 是一个用于计算 F1 分数的评估算子，它通过比较预测文本和参考文本的词语重叠来衡量它们的相似性。它继承自 `MapFunction`。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 配置字典（当前算子未使用特定配置）。
* **`**kwargs`**: 传递给基类 `MapFunction` 的额外参数。

#### 内部方法

* **`_get_tokens(self, text)`**:
    * **功能**: 将输入文本转换为小写并按空格分割成词语列表（tokens）。
    * **参数**: `text` (`str`) - 输入文本。
    * **返回**: `list[str]` - 小写词语列表。
* **`_f1_score(self, prediction, reference)`**:
    * **功能**: 计算预测文本和参考文本之间的 F1 分数。F1 分数是精确率和召回率的调和平均值，用于衡量文本相似度。
    * **参数**:
        * `prediction` (`str`) - 模型生成的预测文本。
        * `reference` (`str`) - 参考标准文本。
    * **返回**: `float` - 计算出的 F1 分数。

#### 执行方法 (`execute`)

`execute` 方法计算给定预测和参考文本的 F1 分数并打印结果。

* **`data`** (`tuple[str, str]`): 一个包含两个字符串的元组，第一个是参考文本，第二个是预测文本。
    * `reference` (`str`): 参考标准文本。
    * `prediction` (`str`): 模型生成的预测文本。
* **返回**: 无。打印 F1 分数到控制台。



---
### BertRecallEvaluate

`BertRecallEvaluate` 是一个基于 BERT 模型的召回率评估算子，它使用 BERT 嵌入的余弦相似度来衡量生成文本与参考文本之间的语义相似性。它继承自 `MapFunction`。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 配置字典（当前算子未使用特定配置）。
* **`**kwargs`**: 传递给基类 `MapFunction` 的额外参数。

#### 属性

* **`model`**: 加载的 `bert-base-uncased` 预训练模型。
* **`tokenizer`**: 加载的 `bert-base-uncased` 分词器。

#### 内部方法

* **`bert_recall(self, reference, generated)`**:
    * **功能**: 计算参考文本和生成文本之间基于 BERT 嵌入的余弦相似度。
    * **参数**:
        * `reference` (`str`) - 参考标准文本。
        * `generated` (`str`) - 模型生成的文本。
    * **返回**: `float` - 计算出的 BERT 召回分数（余弦相似度）。如果生成文本为空，则返回 0.0。

#### 执行方法 (`execute`)

`execute` 方法计算给定参考文本和生成文本的 BERT 召回分数并打印结果。

* **`data`** (`tuple[str, str]`): 一个包含两个字符串的元组，第一个是参考文本，第二个是生成文本。
    * `reference` (`str`): 参考标准文本。
    * `generated` (`str`): 模型生成的文本。
* **返回**: 无。打印 BERT 召回分数到控制台。


---
### RougeLEvaluate

`RougeLEvaluate` 是一个用于计算 ROUGE-L 分数的评估算子，它主要通过最长公共子序列（LCS）来衡量生成文本与参考文本之间的相似性，通常用于摘要和机器翻译的评估。它继承自 `MapFunction`。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 配置字典（当前算子未使用特定配置）。
* **`**kwargs`**: 传递给基类 `MapFunction` 的额外参数。

#### 属性

* **`rouge`**: `rouge` 库的 `Rouge` 实例。

#### 内部方法

* **`rouge_l(self, reference, generated)`**:
    * **功能**: 计算生成文本和参考文本之间的 ROUGE-L F1 分数。
    * **参数**:
        * `reference` (`str`) - 参考标准文本。
        * `generated` (`str`) - 模型生成的文本。
    * **返回**: `float` - 计算出的 ROUGE-L F1 分数。如果生成文本为空，则返回 0.0。

#### 执行方法 (`execute`)

`execute` 方法计算给定参考文本和生成文本的 ROUGE-L 分数并打印结果。

* **`data`** (`tuple[str, str]`): 一个包含两个字符串的元组，第一个是参考文本，第二个是生成文本。
    * `reference` (`str`): 参考标准文本。
    * `generated` (`str`): 模型生成的文本。
* **返回**: 无。打印 ROUGE-L 分数到控制台。

---
### BRSEvaluate

`BRSEvaluate` 是一个复合评估算子，它结合了 BERT 召回率和 ROUGE-L 分数来提供一个综合的评估指标（BRS）。它继承自 `MapFunction`。

#### 初始化参数 (`__init__`)

* **`config`** (`dict`): 配置字典。此配置会传递给内部的 `BertRecallEvaluate` 和 `RougeLEvaluate` 实例。
* **`**kwargs`**: 传递给基类 `MapFunction` 的额外参数。

#### 属性

* **`bert_recall_evaluate`**: `BertRecallEvaluate` 的实例。
* **`rouge_l_evaluate`**: `RougeLEvaluate` 的实例。

#### 内部方法

* **`BRS(self, reference, generated)`**:
    * **功能**: 计算生成文本和参考文本的 BRS 分数。BRS 分数是 BERT 召回率和 ROUGE-L 分数的调和平均值。
    * **参数**:
        * `reference` (`str`) - 参考标准文本。
        * `generated` (`str`) - 模型生成的文本。
    * **返回**: `float` - 计算出的 BRS 分数。如果任一子分数（BERT 召回或 ROUGE-L）为 0，则返回 0。

#### 执行方法 (`execute`)

`execute` 方法计算给定参考文本和生成文本的 BRS 分数并打印结果。

* **`data`** (`tuple[str, str]`): 一个包含两个字符串的元组，第一个是参考文本，第二个是生成文本。
    * `reference` (`str`): 参考标准文本。
    * `generated` (`str`): 模型生成的文本。
* **返回**: 无。打印 BRS 分数到控制台。
