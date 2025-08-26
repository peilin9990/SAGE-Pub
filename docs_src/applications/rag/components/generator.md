# SAGE 使用生成器（LLM）指南
本指南介绍如何在 SAGE 系统中使用 生成器（LLM）算子生成回答。

## 1. OpenAIGenerator

`OpenAIGenerator` 支持调用 OpenAI/VLLM/DashScope 等兼容端点，典型配置如下：

```python
sub_conf = config["generator"]["vllm"]
gen = OpenAIGenerator(sub_conf)
```

配置示例：
```json
{
  "method":     "openai",
  "model_name": "gpt-4o-mini",
  "base_url":   "http://localhost:8000/v1",
  "api_key":    "xxx",
  "seed":       42
}
```

调用方式：
```python
user_query, generated_text = gen.execute([user_query, prompt])
```
- 输入支持 `[user_query, prompt]` 或 `[prompt]`，返回 `(user_query, generated_text)`。
- 支持 `enable_profile=True`，自动保存生成记录到本地，便于追踪和分析。

#### 进阶功能
- 支持多端点扩展，可根据 `method` 字段切换不同模型服务。
- 支持自定义数据存储路径和持久化生成记录。

## 2. HFGenerator

`HFGenerator` 用于调用 HuggingFace 本地模型，配置简单：

```python
sub_conf = {"model_name": "your-hf-model"}
gen = HFGenerator(sub_conf)
user_query, generated_text = gen.execute([user_query, prompt])
```

- 支持传递额外参数（如 temperature, max_tokens 等）到模型生成接口。
- 适合本地部署、无外网依赖场景。