# LLM QA 快速入门

本文档介绍如何使用 SAGE 构建基于大语言模型的问答系统，包括不带检索的直接问答和集成检索功能的增强问答。

---

## 🎯 核心概念

LLM QA（大语言模型问答）是直接使用大语言模型进行问答的技术，无需外部知识库检索。适用于：

- 一般常识问答
- 编程辅助
- 文本创作
- 实时对话

---

## 🚀 不带检索的QA示例

### 终端交互式QA

这个示例展示如何构建一个终端交互式的问答系统：

```python
"""
终端交互式QA无界流处理
支持终端输入问题，使用大模型生成回答的无界流处理示例
"""
import time
from dotenv import load_dotenv
from sage.common.utils.logging.custom_logger import CustomLogger
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.map_function import MapFunction
from sage.core.api.function.sink_function import SinkFunction
from sage.core.api.function.source_function import SourceFunction
from sage.libs.rag.generator import OpenAIGenerator
from sage.libs.rag.promptor import QAPromptor
from sage.common.utils.config.loader import load_config


class TerminalInputSource(SourceFunction):
    """终端输入源函数"""
    def execute(self, data=None):
        try:
            print("🤔 请输入您的问题（按Ctrl+C退出）:")
            user_input = input(">>> ").strip()
            if user_input:
                return user_input
            return self.execute(data)
        except (EOFError, KeyboardInterrupt):
            raise


class QuestionProcessor(MapFunction):
    """问题处理器"""
    def execute(self, data):
        if not data or data.strip() == "":
            return None

        question = data.strip()
        return question


class AnswerFormatter(MapFunction):
    """回答格式化器"""
    def execute(self, data):
        if not data:
            return None

        # OpenAIGenerator返回的格式是 (user_query, generated_text)
        if isinstance(data, tuple) and len(data) >= 2:
            user_query = data[0]
            answer = data[1]
            return {
                "question": user_query if user_query else "N/A",
                "answer": answer,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            return {
                "question": "N/A",
                "answer": str(data),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }


class ConsoleSink(SinkFunction):
    """控制台输出"""
    def execute(self, data):
        if not data:
            return None

        if isinstance(data, dict):
            print(f"\n🤖 {data.get('answer', 'N/A')}\n")
        else:
            print(f"\n🤖 {data}\n")

        return data


def create_qa_pipeline():
    """创建QA处理管道"""
    import os
    # 加载配置
    load_dotenv(override=False)
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "config_source.yaml")
    config = load_config(config_path)

    # 创建本地环境
    env = LocalEnvironment()

    # 启动欢迎提示
    print("💬 QA助手已启动！输入问题后按回车")

    try:
        # 构建无界流处理管道
        (env
            .from_source(TerminalInputSource)
            .map(QuestionProcessor)
            .map(QAPromptor, config["promptor"])
            .map(OpenAIGenerator, config["generator"]["vllm"])
            .map(AnswerFormatter)
            .sink(ConsoleSink)
        )

        # 启动管道
        env.submit()

        # 保持程序运行
        print("程序运行中，按 Ctrl+C 退出...")
        import time
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n👋 感谢使用，再见！")
    finally:
        try:
            env.close()
        except:
            pass


if __name__ == "__main__":
    # 关闭调试日志
    CustomLogger.disable_global_console_debug()
    create_qa_pipeline()
```

### 批处理QA

处理预定义的问题列表：

```python
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.batch_function import BatchFunction
from sage.libs.rag.generator import OpenAIGenerator
from sage.libs.rag.promptor import QAPromptor
from sage.libs.io_utils.sink import TerminalSink

class QABatch(BatchFunction):
    """QA批处理数据源"""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.questions = [
            "什么是人工智能？",
            "Python有什么特点？",
            "如何学习机器学习？",
            "深度学习的应用领域有哪些？"
        ]
        self.counter = 0

    def execute(self):
        if self.counter >= len(self.questions):
            return None
        
        question = self.questions[self.counter]
        self.counter += 1
        return question

def batch_qa_pipeline():
    """批处理QA管道"""
    env = LocalEnvironment("batch_qa")
    
    config = {
        "promptor": {"platform": "local"},
        "generator": {
            "vllm": {
                "api_key": "your-api-key",
                "method": "openai",
                "model_name": "gpt-3.5-turbo",
                "base_url": "https://api.openai.com/v1"
            }
        },
        "sink": {"platform": "local"}
    }
    
    (env
        .from_batch(QABatch, config)
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )
    
    env.submit(autostop=True)

if __name__ == "__main__":
    batch_qa_pipeline()
```

---

## 🔧 配置选项

### 基础配置文件

创建 `config.yaml` 文件：

```yaml
pipeline:
  name: "llm-qa-pipeline"
  description: "LLM问答管道"

promptor:
  platform: "local"

generator:
  vllm:
    api_key: "your-api-key"
    method: "openai"
    model_name: "gpt-3.5-turbo"
    base_url: "https://api.openai.com/v1"
    temperature: 0.7
    max_tokens: 1000

sink:
  platform: "local"
```

### 环境变量配置

创建 `.env` 文件：

```env
# OpenAI API配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# 或者使用兼容的API
VLLM_API_KEY=your-vllm-api-key
VLLM_BASE_URL=http://localhost:8000/v1
```

---

## 🎨 自定义提示词

### 基础提示词模板

```python
from jinja2 import Template

# 自定义提示词模板
qa_template = Template("""
你是一个专业的AI助手，请基于以下上下文回答用户的问题。

{% if external_corpus %}
参考信息：
{{ external_corpus }}
{% endif %}

请提供准确、有用的回答。如果不确定答案，请诚实地说明。
""")

# 在QAPromptor中使用
config = {
    "promptor": {
        "platform": "local",
        "template": qa_template
    }
}
```

---

## 📊 性能优化

### 批量处理优化

```python
class OptimizedQABatch(BatchFunction):
    """优化的批处理QA"""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.batch_size = config.get("batch_size", 5)
        self.questions = self.load_questions(config["data_path"])
        self.current_batch = 0
        
    def execute(self):
        start_idx = self.current_batch * self.batch_size
        end_idx = start_idx + self.batch_size
        
        if start_idx >= len(self.questions):
            return None
            
        batch_questions = self.questions[start_idx:end_idx]
        self.current_batch += 1
        return batch_questions
```

### 异步处理

```python
import asyncio
from sage.core.api.function.map_function import MapFunction

class AsyncQAProcessor(MapFunction):
    """异步QA处理器"""
    async def async_execute(self, data):
        # 异步调用LLM API
        result = await self.async_llm_call(data)
        return result
    
    def execute(self, data):
        # 在同步上下文中运行异步代码
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.async_execute(data))
```

---

## 🔍 错误处理

### 健壮的错误处理

```python
class RobustQAProcessor(MapFunction):
    """带错误处理的QA处理器"""
    def execute(self, data):
        try:
            # 处理问题
            if not data or not data.strip():
                return {"error": "空问题", "question": data}
                
            # 调用LLM
            result = self.call_llm(data)
            return {"success": True, "question": data, "answer": result}
            
        except Exception as e:
            self.logger.error(f"QA处理错误: {e}")
            return {
                "error": str(e),
                "question": data,
                "answer": "抱歉，处理您的问题时出现了错误。"
            }
```

---

## 📈 监控和日志

### 性能监控

```python
import time
from collections import defaultdict

class QAMonitorSink(SinkFunction):
    """QA监控输出"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats = defaultdict(int)
        self.start_time = time.time()
    
    def execute(self, data):
        self.stats["total_questions"] += 1
        
        if isinstance(data, dict):
            if "error" in data:
                self.stats["errors"] += 1
            else:
                self.stats["success"] += 1
                
        # 每100个问题打印一次统计
        if self.stats["total_questions"] % 100 == 0:
            self.print_stats()
            
        return data
    
    def print_stats(self):
        elapsed = time.time() - self.start_time
        print(f"处理统计: {self.stats['total_questions']} 问题")
        print(f"成功率: {self.stats['success'] / self.stats['total_questions'] * 100:.1f}%")
        print(f"平均速度: {self.stats['total_questions'] / elapsed:.1f} 问题/秒")
```

---

## 🚀 快速开始

1. **安装依赖**：确保已安装 SAGE 和相关依赖
2. **配置API**：设置大语言模型的API密钥和地址
3. **运行示例**：选择合适的示例代码运行
4. **自定义扩展**：根据需求修改提示词和处理逻辑

---

*通过SAGE构建的LLM QA系统具备高度的灵活性和扩展性，是智能问答应用的理想选择。*
