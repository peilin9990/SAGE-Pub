# 快速入门

本节将引导你在几分钟内完成 SAGE 系统的最小化运行，了解核心模块的调用方式和执行流程。我们提供两种推荐的入门方式：

- 使用批处理模式构建简单的数据处理流水线
- 使用流式处理模式构建实时数据处理系统

---

## ✅ 前提要求

!!! note "环境要求"
    在执行示例前，请确保已完成基本安装（参考 [安装指南](install.md)），并激活相应的 Python/Conda 环境。

---

## 🚀 Hello World 示例

### 批处理模式

以下示例来自 [`examples/tutorials/hello_world.py`](https://github.com/intellistream/SAGE/blob/main/examples/tutorials/hello_world.py)：

```python
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.sink_function import SinkFunction
from sage.core.api.function.batch_function import BatchFunction
from sage.core.api.function.map_function import MapFunction
from sage.common.utils.logging.custom_logger import CustomLogger

# 批处理数据源：作用是生成10条"Hello, World!"字符串
class HelloBatch(BatchFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.max_count = 10     # 生成10个数据包后返回None
    
    def execute(self):
        if self.counter >= self.max_count:
            return None         # 返回None表示批处理完成
        self.counter += 1
        return f"Hello, World! #{self.counter}"

# 简单的 MapFunction，将内容转大写
class UpperCaseMap(MapFunction):
    def execute(self, data):
        return data.upper()

# 简单 SinkFunction，直接打印结果
class PrintSink(SinkFunction):
    def execute(self, data):
        print(data)

def main():
    env = LocalEnvironment("Hello_World")
    
    # 批处理源 -> map -> sink
    env.from_batch(HelloBatch).map(UpperCaseMap).sink(PrintSink)

    env.submit(autostop=True)
    print("Hello World 批处理示例结束")

if __name__ == "__main__":
    # 关闭日志输出
    CustomLogger.disable_global_console_debug()
    main()
```

### 流式处理模式

以下示例来自 [`examples/tutorials/stream_mode/hello_streaming_world.py`](https://github.com/intellistream/SAGE/blob/main/examples/tutorials/stream_mode/hello_streaming_world.py)：

```python
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.sink_function import SinkFunction
from sage.core.api.function.source_function import SourceFunction
from sage.core.api.function.map_function import MapFunction
from sage.common.utils.logging.custom_logger import CustomLogger

# 流式数据源：从BatchFunction变成SourceFunction
class HelloStreaming(SourceFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0

    def execute(self):
        self.counter += 1
        return f"Hello, Streaming World! #{self.counter}"

class UpperCaseMap(MapFunction):
    def execute(self, data):
        return data.upper()

class PrintSink(SinkFunction):
    def execute(self, data):
        print(data)

def main():
    env = LocalEnvironment("hello_streaming_world")

    # 流式源，从 from_batch 变成 from_source
    env.from_source(HelloStreaming).map(UpperCaseMap).sink(PrintSink)

    try:
        print("Waiting for streaming processing to complete...")
        env.submit()

        # 暂停主程序，因为在LocalEnvironment下，流式处理是异步的
        from time import sleep
        sleep(1)

    except KeyboardInterrupt:
        print("停止运行")
    finally:
        print("Hello Streaming World 流式处理示例结束")

if __name__ == "__main__":
    # 关闭日志输出
    CustomLogger.disable_global_console_debug()
    main()
```

---

## 🔧 使用 SAGE 构建 RAG 流水线

SAGE 提供声明式、可组合的 API 接口构建数据流，以下为典型 RAG 管线：

```python
from sage.core.api.local_environment import LocalEnvironment
from sage.libs.io_utils.source import FileSource
from sage.libs.io_utils.sink import TerminalSink
from sage.libs.rag.retriever import DenseRetriever
from sage.libs.rag.promptor import QAPromptor
from sage.libs.rag.generator import OpenAIGenerator
from sage.common.utils.config.loader import load_config

def pipeline_run():
    """创建并运行RAG数据处理管道"""
    # 创建本地环境
    env = LocalEnvironment("rag_pipeline")

    # 加载配置
    config = load_config("examples/config/config.yaml")
    
    # 构建RAG处理流程
    (env
        .from_source(FileSource, config["source"])
        .map(DenseRetriever, config["retriever"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["vllm"])
        .sink(TerminalSink, config["sink"])
    )

    # 提交并运行
    env.submit()
    
    # 等待处理完成
    import time
    time.sleep(5)
    env.close()

if __name__ == '__main__':
    pipeline_run()
```

### 📘 配置说明

每个 Operator 的运行需传入 config 参数，你可在项目中的 [`examples/config/`](https://github.com/intellistream/SAGE/tree/main/examples/config) 文件夹中找到示例配置文件。

### 📘 分布式执行（Remote）

若需启用分布式执行，可以使用 RemoteEnvironment：
```python
from sage.core.api.remote_environment import RemoteEnvironment

# 连接到远程JobManager
env = RemoteEnvironment(
    name="remote_pipeline",
    host="127.0.0.1",  # JobManager主机
    port=19001          # JobManager端口
)
```

### 📘 服务注册

SAGE支持注册各种服务供流水线使用：
```python
from sage.middleware.services.memory import MemoryService

# 注册Memory服务
env.register_service("memory_service", MemoryService)

# 在Function中使用服务
def execute(self, data):
    result = self.call_service["memory_service"].search_memories(...)
    return result
```

---

## ⚠️ 注意事项

!!! warning "模块路径变化提示"
    若你基于不同版本运行上述代码，部分模块路径或参数可能有所调整。当前推荐的导入路径：
    
    - 环境：`sage.core.api.local_environment.LocalEnvironment`
    - 函数基类：`sage.core.api.function.*`
    - RAG组件：`sage.libs.rag.*`
    - IO组件：`sage.libs.io_utils.*`
    - 服务：`sage.middleware.services.*`

---

## 🧠 更多示例

- 若希望了解更多批处理示例，请参阅 [有界流处理](streaming/limited_streaming.md)
- 若希望了解流式处理示例，请参阅 [无界流处理](streaming/unlimited_streaming.md)
- 若希望构建RAG应用，请参阅 [Naive RAG](naive_rag/sage_naive_rag.md)
- 若希望了解中间件服务，请参阅 [中间件服务](middleware_service/middleware_quick_start.md)

---
