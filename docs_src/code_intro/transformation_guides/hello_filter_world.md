# Hello Filter World 编程指南

本指南基于示例 `examples/tutorials/transformation-api/hello_filter_world.py`，结合《DataStream 数据流转换》中的概念，讲解以下 API 的用法：

- DataStream.map
- DataStream.filter
- SinkFunction
- BatchFunction

## 场景概述
从一个批源生成 1..10 的字符串记录，经 Map 转大写，再用 Filter 仅保留结尾为奇数的记录，最终打印输出。

## 关键类与接口

- LocalEnvironment：本地执行环境，负责 DAG 构建与调度。
- BatchFunction：批源函数，每次 execute 返回一条数据，返回 None 表示结束。
- MapFunction：记录级一对一转换。
- FilterFunction：记录级过滤，返回 None 的记录会被丢弃。
- SinkFunction：终端输出。

## 示例拆解
1) 批源

- HelloBatch.execute 按计数递增返回 "Hello, World! #N"，到达上限返回 None 结束。

2) Map 转换

- UpperCaseMap.execute 将字符串转为大写。

3) Filter 过滤

- Oddpicker.execute 解析末尾数字，仅保留奇数编号；偶数返回 None 被丢弃。

4) Sink 输出

- PrintSink.execute 打印最终保留的记录。

## 流水线

- env.from_batch(HelloBatch)
    .map(UpperCaseMap)
    .filter(Oddpicker)
    .sink(PrintSink)

## 常见陷阱与建议

- Filter 返回 None 即表示丢弃该条记录；确保上游 Map 的输出格式与 Filter 逻辑一致。
- 批源需要在达到条件时返回 None 以终止流水线；否则可能阻塞退出。
- 调试时可暂时开启日志或在函数内打印关键中间值。

## 扩展示例

- 在 Map 中解析 JSON 再 Filter 符合条件的字段。
- 将 Filter 条件抽象为可配置阈值，方便实验调参。

!!! tip "运行提示"
    示例中通过 `CustomLogger.disable_global_console_debug()` 关闭控制台日志；使用 `env.submit(autostop=True)` 可在数据耗尽后自动退出。

## 示例代码

```python title="examples/tutorials/transformation-api/hello_filter_world.py" linenums="1"
# 此例意在说明 Fileter 算子的使用
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.sink_function import SinkFunction
from sage.core.api.function.batch_function import BatchFunction
from sage.core.api.function.map_function import MapFunction
from sage.core.api.function.filter_function import FilterFunction
from sage.common.utils.logging.custom_logger import CustomLogger

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

# 过滤器示例，过滤所有偶数结尾的数据
class Oddpicker(FilterFunction):
  def execute(self, data):
    if int(data[-1]) % 2 != 0:
      return data
    else:
      return None

def main():
  env = LocalEnvironment("Hello_Filter_World")

  env.from_batch(HelloBatch).map(UpperCaseMap).filter(Oddpicker).sink(PrintSink)

  env.submit(autostop=True)
  print("Hello Filter World 示例结束")

if __name__ == "__main__":
  # 关闭日志输出
  CustomLogger.disable_global_console_debug()
  main()

```
