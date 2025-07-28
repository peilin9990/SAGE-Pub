# DataStream 数据流转换

DataStream 是 SAGE 程序中用于串联和组织各类数据处理函数（算子）的核心抽象。如图所示 用户可以通过在 DataStream 上依次声明不同的数据转换（如 map、filter、flatmap 等），SAGE 会通过 Complier 组件将它们连接为一个完整的数据处理流程，形成最终用于执行任务的 DataStream。

![DataStream Transformation](../../assets/img/transformation.png)

本节将详细介绍 DataStream API 的核心数据转换接口、算子的连接与组合方式，以及数据在各算子间的分区策略和调度机制。

---

## 一、map

```python
def map(self,
        function: Union[Type[BaseFunction], callable],
        *args, **kwargs
       ) -> DataStream
```

- 功能：一对一映射  
- 底层：`MapTransformation` + `MapOperator`  
- 参数：
  - `function`：自定义 `MapFunction` 类或 `lambda`/普通函数  
  - `*args, **kwargs`：传递给 Function 构造器的参数  
- 返回：新的 `DataStream`，记录 Map 结果类型  

示例：
```python
class MultiplyBy2(MapFunction):
    def execute(self, x):
        return x * 2

ds2 = ds.map(MultiplyBy2())
# 或者
ds2 = ds.map(lambda x: x*2)
```

---

## 二、filter

```python
def filter(self,
           function: Union[Type[BaseFunction], callable],
           *args, **kwargs
          ) -> DataStream
```

- 功能：按条件过滤，只保留 `execute()` 返回 `True` 的记录  
- 底层：`FilterTransformation` + `FilterOperator`  
- 参数同 `map`  
- 返回：新的 `DataStream`

示例：
```python
class PositiveFilter(FilterFunction):
    def execute(self, x):
        return x > 0

ds_flt = ds.filter(PositiveFilter())
```

---

## 三、flatmap

```python
def flatmap(self,
            function: Union[Type[BaseFunction], callable],
            *args, **kwargs
           ) -> DataStream
```

- 功能：一对多扁平映射  
- 底层：`FlatMapTransformation` + `FlatMapOperator`  
- 支持：
  1. 在 `execute()` 内部调用 `collector.collect(item)`  
  2. 直接返回可迭代对象  
- 参数同 `map`  
- 返回：新的 `DataStream`

示例：
```python
class SplitWords(FlatMapFunction):
    def execute(self, line):
        return line.split()

ds_words = ds.flatmap(SplitWords())
```

---

## 四、keyby

```python
def keyby(self,
          function: Union[Type[BaseFunction], callable],
          strategy: str = "hash",
          *args, **kwargs
         ) -> DataStream
```

- 功能：按 Key 分区，生成 `KeyedStream`  
- 底层：`KeyByTransformation` + `KeyByOperator`  
- 参数：
  - `function`：自定义 `KeyByFunction` 或 `lambda`，返回分区键  
  - `strategy`：分区策略，可选 `"hash"`、`"broadcast"`、`"round_robin"`  
- 返回：新的 `DataStream`

示例：
```python
ds_keyed = ds.keyby(lambda x: x["user_id"], strategy="round_robin")
```

---

## 五、sink

```python
def sink(self,
         function: Union[Type[BaseFunction], callable],
         *args, **kwargs
        ) -> DataStream
```

- 功能：将流末端数据写入外部系统  
- 底层：`SinkTransformation` + `SinkOperator`  
- 参数：
  - `function`：自定义 `SinkFunction` 或普通函数  
  - `*args, **kwargs`：构造器参数  
- 返回：当前 `DataStream`（终端算子，不生成新流）

示例：
```python
ds.sink(MyJdbcSink, url="jdbc:...", table="users")
```

---

## 六、connect

```python
def connect(self,
            other: Union[DataStream, ConnectedStreams]
           ) -> ConnectedStreams
```

- 功能：连接两条流或已连接的流，返回 `ConnectedStreams`  
- 用途：后续可调用 `co_map`、`co_flatmap` 等多流算子  
- 返回：`ConnectedStreams` 对象

示例：
```python
conn = ds1.connect(ds2)
```

---

## 七、fill_future

```python
def fill_future(self, future_stream: DataStream) -> None
```

- 功能：创建反馈边，将当前流与预先声明的未来流（`env.from_future()`）相连  
- 前置：`future_stream` 必须由 `env.from_future(name)` 创建  
- 效果：在内部 DAG 中填充 Future 节点  
- 返回：None

示例：
```python
future = env.from_future("loop")
processed = source.connect(future).co_map(MyCoMap)
processed.fill_future(future)
```

