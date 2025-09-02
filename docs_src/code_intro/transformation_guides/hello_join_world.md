# Hello Join World 编程指南

本指南基于示例 `examples/tutorials/transformation-api/hello_join_world.py`，讲解按键分区与双流连接：

- DataStream.keyby
- DataStream.connect
- ConnectedStreams.join（JoinFunction）

## 场景概述
两条批源流产生带有 id 的记录，经 keyby 提取相同的 key 后，通过 connect + join 进行关联，输出配对后的合并结果。

## 关键类与接口

- LocalEnvironment：执行环境
- BatchFunction：批源
- KeyByFunction：提取 key，用于分区
- BaseJoinFunction：双流 Join 算子，框架传入 (payload, key, tag)
- SinkFunction：终端输出

## 示例拆解

1) 左右流创建并分别 keyby(IdKeyBy)

2) 连接：left.connect(right)

3) 关联：.join(HelloWorldJoin)

- execute(payload, key, tag)
- 内部使用两个缓存 hello_cache/world_cache 组合匹配的 pair

4) Sink：打印合并后的消息

## 流水线

- env.from_batch(SourceOne).keyby(IdKeyBy)
- env.from_batch(SourceTwo).keyby(IdKeyBy)
- left.connect(right).join(HelloWorldJoin).sink(PrintSink)

## 常见陷阱与建议

- keyby 的函数要稳定且覆盖所有需要 join 的记录；缺 key 会导致无法匹配。
- JoinFunction 需要考虑乱序、重复与缓存清理策略；示例是最简实现。
- join 是双向触发的：左右流任一到达都会尝试与对方缓存匹配。

## 扩展示例

- 订单与支付对账：order 流与 payment 流按 order_id join。
- 实时监控：指标流与阈值流按指标名 join，并产生告警。

!!! tip "提示"
    示例使用最简缓存实现并未处理乱序/过期；在真实生产中请结合窗口、水位线或 TTL 策略清理缓存。

## 示例代码

```python title="examples/tutorials/transformation-api/hello_join_world.py" linenums="1"
# 此例用到了keyby和join操作符，展示如何将两个数据流按key进行关联。
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.sink_function import SinkFunction
from sage.core.api.function.batch_function import BatchFunction
from sage.core.api.function.keyby_function import KeyByFunction
from sage.core.api.function.join_function import BaseJoinFunction
from sage.common.utils.logging.custom_logger import CustomLogger

class SourceOne(BatchFunction):
   def __init__(self):
      super().__init__()
      self.counter = 0

   def execute(self):
      self.counter += 1
      if self.counter > 5:
         return None
      return {"id": self.counter, "msg": f"Hello-{self.counter}", "type": "hello"}


class SourceTwo(BatchFunction):
   def __init__(self):
      super().__init__()
      self.counter = 0

   def execute(self):
      self.counter += 1
      if self.counter > 5:
         return None
      return {"id": self.counter, "msg": f"World-{self.counter}", "type": "world"}

class IdKeyBy(KeyByFunction):
   def execute(self, data):
      return data.get("id")

class PrintSink(SinkFunction):
   def execute(self, data):
      print(f"🔗 Joined Streaming: {data}")

class HelloWorldJoin(BaseJoinFunction):
   """
   Join 算子示例：
   execute(payload, key, tag) 参数说明：
     - payload: 流里传过来的原始数据 (dict)
     - key: 由 keyby 算子提取出来的分区键 (比如这里的 id)
     - tag: 数据来源标识 (0=左流 / 第一个流, 1=右流 / 第二个流)
   """
   def __init__(self, **kwargs):
      super().__init__(**kwargs)
      self.hello_cache = {}   # {key: [payloads]}
      self.world_cache = {}   # {key: [payloads]}

   def execute(self, payload, key, tag):
      results = []
      data_type = payload.get("type", "")

      if tag == 0:  # 第一个流 (Hello)
         if data_type == "hello":
            # 缓存 Hello 数据
            self.hello_cache.setdefault(key, []).append(payload)
                
            # 检查是否有匹配的 World 数据
            if key in self.world_cache:
               for world_data in self.world_cache[key]:
                  results.append(self._merge(payload, world_data, key))

      elif tag == 1:  # 第二个流 (World)
         if data_type == "world":
            # 缓存 World 数据
            self.world_cache.setdefault(key, []).append(payload)
                
            # 检查是否有匹配的 Hello 数据
            if key in self.hello_cache:
               for hello_data in self.hello_cache[key]:
                  results.append(self._merge(hello_data, payload, key))

      return results

   def _merge(self, hello_data, world_data, key):
      return {
         "id": key,
         "msg": f"{hello_data['msg']} + {world_data['msg']}"
      }

def main():
   env = LocalEnvironment("Hello_Join_World")

   source1 = env.from_batch(SourceOne).keyby(IdKeyBy)
   source2 = env.from_batch(SourceTwo).keyby(IdKeyBy)

   # connect + join
   source1.connect(source2).join(HelloWorldJoin).sink(PrintSink)

   # 提交但不使用 autostop，而是手动控制
   env.submit()
    
   # 等待一段时间让批处理完成
   import time
   time.sleep(2)  # 给足够时间让所有数据处理完成
    
   print("Hello Join World 示例结束")


if __name__ == "__main__":
   CustomLogger.disable_global_console_debug()
   main()

```
