# DataStream 编程指南

SAGE 中的 **DataStream** 是对数据流进行转换处理的应用程序。如图所示，数据流的起始是从各种源（例如消息队列、套接字流、文件）创建的，经过各种算子处理，结果通过 sink 返回，例如，可以将数据写入文件或标准输出（例如命令行终端）。

[![DataStream Processing](../../assets/img/streaming.png  "数据流处理流程")](../../assets/img/streaming.png)

为了创建自己的 SAGE 程序，我们建议您从 Hello World 程序剖析开始，然后逐渐添加自定义的DataStream。

---

## Hello World 程序剖析

最简单的 SAGE 应用程序由以下几个基本部分构成：

1. **配置运行环境**
2. **声明数据流入**
3. **定义数据处理逻辑**
4. **声明数据流出**
5. **启动任务执行**


先让我们来看一个完整的 SAGE 程序，本程序演示了如何利用 SAGE 编写一个简单的批处理任务：

```Python linenums="1" title="Python"
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
    
    # from_batch -> map -> sink
    env.from_batch(HelloBatch).map(UpperCaseMap).sink(PrintSink)
    # 提交 pipeline，并启动自动停止（仅from_batch模式有效）
    env.submit(autostop=True)
    print("Hello World 批处理示例结束")

if __name__ == "__main__":
    # 关闭日志输出
    CustomLogger.disable_global_console_debug()
    main()


```

---

下面我们将对这些部分逐一进行概述，以便理解 SAGE 编程的主要思想：

### `HelloBatch`：批量数据源

```python
class HelloBatch(BatchFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.max_count = 10 

    def execute(self):
        if self.counter >= self.max_count:
            return None 
        self.counter += 1
        return f"Hello, World! #{self.counter}"
```

> **说明：**
>
> * 继承自 `BatchFunction`，需要实例化抽象接口 `execute()`，用于批量生成数据。
> * 每调用一次 `execute()`，返回一个新的 `"Hello, World! #编号"` 字符串。
> * 当生成 10 条数据后，返回 `None`，**通知框架数据已经生成完毕**，数据源自动结束。

---

### `UpperCaseMap`：数据转换

```python
class UpperCaseMap(MapFunction):
    def execute(self, data):
        return data.upper()
```

> **说明：**
>
> * 继承自 `MapFunction`，这是 SAGE 中常见的数据转换节点（map）。
> * 对传入的每条数据执行 `.upper()`，**将字符串转为大写**。
> * 无状态、单条转换，非常高效。

---

### `PrintSink`：结果终端

```python
class PrintSink(SinkFunction):
    def execute(self, data):
        print(data)
        return data
```

> **说明：**
>
> * 继承自 `SinkFunction`，用作数据处理的“终点”。
> * 每收到一条数据，**直接打印输出**。
> * 返回数据本身，这里主要是为了流程完整，实际 sink 的返回值不会再用到。

---

### `main`函数：环境和数据流搭建

```python
def main():
    env = LocalEnvironment("Hello_World")
    
    # from_batch -> map -> sink
    env.from_batch(HelloBatch).map(UpperCaseMap).sink(PrintSink)
    # 提交 pipeline，并启动自动停止（仅from_batch模式有效）
    env.submit(autostop=True)
    print("Hello World 批处理示例结束")
```

> **说明：**
>
> * 创建本地执行环境 `LocalEnvironment`，方便本地开发与调试。
> * 用链式 API 定义数据流处理步骤：
>
>   1. `from_batch(HelloBatch)`：指定数据源
>   2. `.map(UpperCaseMap)`：添加 map 转换
>   3. `.sink(PrintSink)`：指定输出终点
> * `env.submit(autostop=True)`：**启动任务**。
> * 最后打印“批处理示例结束”。

---


### 运行效果

控制台输出效果：

```plaintext
Waiting for batch processing to complete...
HELLO, WORLD! #1
HELLO, WORLD! #2
HELLO, WORLD! #3
HELLO, WORLD! #4
HELLO, WORLD! #5
HELLO, WORLD! #6
HELLO, WORLD! #7
HELLO, WORLD! #8
HELLO, WORLD! #9
HELLO, WORLD! #10
Hello World 批处理示例结束
```

---

## 结语

本章主要介绍了 SAGE DataStream 编程的基本流程，包括运行环境的配置、数据流的声明、处理逻辑的定义以及结果的输出。

总的来说，SAGE 提供了简洁直观的 API，使得流式与批量数据处理程序的开发更加高效和可维护。在实际应用中，可以根据业务需求灵活组合不同的数据源、转换算子和输出方式，构建出适应多种场景的数据处理任务。建议读者以本示例为基础，进一步拓展和实践，深入理解 SAGE 的编程模式和体系结构。

下面的章节将讲解算子与数据流，供用户编写更加复杂的Pipeline以适应复杂的业务需求。
