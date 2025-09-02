# Hello FlatMap World 编程指南

本指南基于示例 `examples/tutorials/transformation-api/hello_flatmap_world.py`，讲解以下 API 的用法：

- DataStream.map
- DataStream.flatmap
- FlatMapFunction 的返回语义
- SinkFunction / BatchFunction

## 场景概述
从批源生成 1..10 的字符串记录，经 Map 转大写，再用 FlatMap 将每条字符串切分为多个单词并逐条下发，最终打印输出。

## 关键类与接口

- LocalEnvironment：本地执行环境。
- BatchFunction：批源函数，逐条产出数据。
- MapFunction：逐条一对一转换。
- FlatMapFunction：一对多展开；允许返回可迭代或使用 collector.collect() 逐条输出。
- SinkFunction：终端输出。

## 示例拆解

1) 批源 HelloBatch：返回 "Hello, World! #N"。

2) UpperCaseMap：将字符串转为大写。

3) SplitWords(FlatMap)：以空格切分，返回列表；框架会逐条下发列表中的每个元素。

4) PrintSink：打印结果。

## 流水线

- env.from_batch(HelloBatch)
  .map(UpperCaseMap)
  .flatmap(SplitWords)
  .sink(PrintSink)

## 常见陷阱与建议

- FlatMap 返回 None 将被视为无输出；返回空列表则继续但不会下发记录。
- 若使用 collector.collect() 方式，请确保不再返回列表，避免双重输出。
- 上游 Map 的格式要与 FlatMap 的切分逻辑匹配，避免异常。

## 扩展示例

- 对文本执行分词/正则抽取，再扁平化输出 token 列表。
- 对日志行进行解析，按字段拆分成多条下游记录。

!!! tip "运行提示"
    本示例通过 `FlatMapFunction` 将一条记录拆为多条；若返回空列表表示“无下游输出但继续”，返回 `None` 表示“忽略本条”。

## 示例代码

```python title="examples/tutorials/transformation-api/hello_flatmap_world.py" linenums="1"
# 此例意在说明FlatMap的使用
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.sink_function import SinkFunction
from sage.core.api.function.batch_function import BatchFunction
from sage.core.api.function.map_function import MapFunction
from sage.common.utils.logging.custom_logger import CustomLogger
from sage.core.api.function.flatmap_function import FlatMapFunction

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

class UpperCaseMap(MapFunction):
  def execute(self, data):
    return data.upper()

class PrintSink(SinkFunction):
  def execute(self, data):
    print(data)

# 利用FlatMapFunction实现单词拆分
class SplitWords(FlatMapFunction):
  def execute(self, data):
    words = data.split()
    return words


def main():
  env = LocalEnvironment("Hello_Flatmap_World")
    
  env.from_batch(HelloBatch).map(UpperCaseMap).flatmap(SplitWords).sink(PrintSink)

  env.submit(autostop=True)
  print("Hello Flatmap World 示例结束")

if __name__ == "__main__":
  # 关闭日志输出
  CustomLogger.disable_global_console_debug()
  main()

```
