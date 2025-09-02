# Hello CoMap World 编程指南

本指南基于示例 `examples/tutorials/transformation-api/hello_comap_world.py`，讲解多流转换：

- DataStream.connect
- ConnectedStreams.comap（CoMapFunction）
- 多源批流合并处理

## 场景概述
两条批源流：

- SourceOne 产生 5 条 {"msg": "No.i: Hello"}
- SourceTwo 产生 10 条 {"msg": "World! #j"}

通过 connect 连接为 ConnectedStreams，再用 comap 分别处理来自左流/右流的数据，统一下发到下游 Sink。

## 关键类与接口

- LocalEnvironment：本地执行环境
- BatchFunction：批源函数
- BaseCoMapFunction：定义 map0/map1，分别处理左/右两条流
- SinkFunction：终端输出

## 示例拆解

1) 两个批源：env.from_batch(SourceOne/Two)

2) 连接：source1.connect(source2) 得到 ConnectedStreams

3) 合流处理：.comap(HelloCoMapProcessor)

- map0(data)：处理第一条流的元素
- map1(data)：处理第二条流的元素

4) Sink：打印结果

## 流水线

- source1.connect(source2).comap(HelloCoMapProcessor).sink(PrintSink)

## 常见陷阱与建议

- CoMapFunction 中的 map0/map1 必须对输入数据契约一致（例如都包含 'msg' 字段），否则需要在合流前做清洗。
- 左右流速率不一致时，合流输出的时间分布也会不同；如需窗口或 join，请参考 join 示例。

## 扩展示例

- 实时事件流 + 配置流：用 comap 将配置变更与事件合并处理。
- A/B 实验：两路实验流合并，统一输出到监控 Sink。

!!! tip "提示"
    CoMap 的 `map0` 处理 connect 的左流，`map1` 处理右流；请确保两侧数据模式与处理逻辑匹配。

## 示例代码

```python title="examples/tutorials/transformation-api/hello_comap_world.py" linenums="1"
# 此例意在说明如何将两个流通过comap合为一个流

from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.sink_function import SinkFunction
from sage.common.utils.logging.custom_logger import CustomLogger
from sage.core.api.function.batch_function import BatchFunction
from sage.core.api.function.comap_function import BaseCoMapFunction

# 定义两个简单数据源：
class SourceOne(BatchFunction):
   def __init__(self):
      super().__init__()
      self.counter = 0

   def execute(self):
      self.counter += 1
      if self.counter > 5:
         return None
      return {"msg": f"No.{self.counter}: Hello"}

class SourceTwo(BatchFunction):
   def __init__(self):
      super().__init__()
      self.counter = 0

   def execute(self):
      self.counter += 1
      if self.counter > 10:
         return None
      return {"msg": f"World! #{self.counter}"}

class HelloCoMapProcessor(BaseCoMapFunction):
   def map0(self, data):
      return f"[Stream0] 👋 {data['msg']}"
    
   def map1(self, data):
      return f"[Stream1] 🌍 {data['msg']}"

class PrintSink(SinkFunction):
   def execute(self, data):
      print(data)

def main():
   env = LocalEnvironment("Hello_CoMap_World")

   # 两个数据源
   source1 = env.from_batch(SourceOne)
   source2 = env.from_batch(SourceTwo)

   # 将两个流 connect 在一起，并用 comap 分开处理
   source1.connect(source2).comap(HelloCoMapProcessor).sink(PrintSink)

   env.submit(autostop=True)
   print("Hello Comap World 示例结束")

if __name__ == "__main__":
   CustomLogger.disable_global_console_debug()
   main()
```
