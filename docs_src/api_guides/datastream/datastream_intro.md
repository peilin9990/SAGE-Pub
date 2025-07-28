# DataStream 编程指南

SAGE 中的 DataStream 是对数据流进行转换处理的应用程序。如图所示，数据流的起始是从各种源（例如消息队列、套接字流、文件）创建的，经过各种算子处理，结果通过 sink 返回，例如，可以将数据写入文件或标准输出（例如命令行终端）。

![DataStream Processing](../../assets/img/streaming.png)

为了创建自己的 SAGE DataStream 程序，我们建议您从 Hello World 程序剖析开始，然后逐渐添加自己的 stream transformation。

## Hello World 程序剖析

```Python
import time
from sage.core.api.local_environment import LocalEnvironment
from sage.core.function.sink_function import SinkFunction
from sage.core.function.batch_function import BatchFunction
from sage.core.function.map_function import MapFunction
from sage.utils.custom_logger import CustomLogger

# 批处理数据源：生成10条 Hello, World! 数据
class HelloBatch(BatchFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.max_count = 10  # 生成10个数据包后返回None
    
    def execute(self):
        if self.counter >= self.max_count:
            return None  # 返回None表示批处理完成
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
        return data

def main():
    
    env = LocalEnvironment("hello_world_batch_demo")
    
    # DataStream 定义：
    env.from_batch(HelloBatch).map(UpperCaseMap).sink(PrintSink)
    
    try:
        print("Waiting for batch processing to complete...")
        env.submit()
        # 让主线程睡眠，让批处理自动完成并停止

        time.sleep(3)  # 等待3秒
    except KeyboardInterrupt:
        print("停止运行")
    finally:
        print("Hello World 批处理示例结束")

if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    main()

```