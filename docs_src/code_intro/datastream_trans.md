# Transformation 数据流转换

DataStream Transformation 是 SAGE 程序中用于串联和组织各类数据处理函数（算子）的核心抽象。如图所示，用户通过在 DataStream 上依次声明不同的数据转换（如 map、filter、flatmap 等），SAGE 会通过 Complier 组件将它们连接为一个完整的数据处理流，形成最终用于执行任务的 DataStream。

[![DataStream Transformation](../../assets/img/transformation.png "transformation建立连接的过程")](../../assets/img/transformation.png)

本节将详细介绍 DataStream Transformation 的核心数据转换接口、算子的连接与组合方式，以及数据在各算子间的分区策略和调度机制。

---

## Transformation 总览
在 SAGE 中，用户通过链式调用一系列转换操作（如 map、filter、keyby 等），可以将原始数据逐步加工成业务所需的结构和形式，下表列出了 SAGE 中常用的 Transformation 类型及其作用范围，帮助你快速了解各种 API 的用途和返回类型：


| 类别 | 代表方法 | 作用 | 返回类型 |
|-----|---------|-----|---------|
| **记录级转换** | `map` / `filter` / `flatmap` | 逐条处理、过滤或展开数据 | `DataStream` |
| **分区与重分布** | `keyby`  | 控制数据如何在并行算子间分配 | `DataStream` |
| **多流转换** | `connect` / `comap` / `join` | 将两条或多条流组合到一起 | `ConnectedStreams` / `DataStream`|
| **终端输出** | `sink` | 将结果写出到外部系统或文件 | *无*（链路结束） |

---

## 记录级转换

### `map` —— 一对一映射

```python
ds2 = ds.map(lambda x: x * 2)
```

* 适用场景：QA问答、文本蒸馏、工具调用
* 底层：`MapTransformation` + `MapOperator`

### `filter` —— 条件过滤

```python
ds_positive = ds.filter(lambda x: x > 0)
```

* 适用场景：历史记忆遗忘、信息截断
* 底层：`FilterTransformation` + `FilterOperator`

### `flatmap` —— 一对多展开

```python
ds_words = ds.flatmap(lambda line: line.split())
```

* 适用场景：记忆联想、信息提取
* 底层：`FlatMapTransformation` + `FlatMapOperator`
* `execute()` 可 **返回可迭代对象** 或使用 `collector.collect()` 逐条输出


---

## 分区与重分布

### `keyby` —— Hash 分区（默认）

```python
orders_by_user = orders.keyby(lambda o: o["user_id"])
```

* 返回 `KeyedStream`，后续可进行 **窗口、状态** 等 Key 级操作
* 其他策略：`strategy="round_robin" | "broadcast"`

---

## 多流转换

### `connect` + `co_map`

将两条类型不同的流连接在一起，形成一个 `ConnectedStreams`，随后通过 `co_map()` 或 `co_flatmap()` 分别处理两侧流的数据。

```python
class DualStreamHandler(CoMapFunction):
    def map1(self, event):  # 第一条流处理逻辑
        return ("event", event)

    def map2(self, config):  # 第二条流处理逻辑
        return ("config", config)

connected = ds1.connect(ds2).co_map(DualStreamHandler)
```

* `connect()` 接收两条 DataStream
* `co_map()` 接收一个继承自 `CoMapFunction` 的函数
* 适用于：事件 + 配置、主流 + 控制流 等双流处理


---

## 终端输出

### `sink` —— 写出结果

```python
ds.sink(MyJdbcSink, url="jdbc:...", table="users")
```

* 一条数据只会被处理一次 **并发安全由 SinkFunction 保证**
* 支持多种外部系统：文件、控制台、JDBC、Kafka、Elasticsearch 等

---

## 反馈边与循环流

SAGE 支持在 DAG 中创建 **循环 (feedback edge)**：

```python
future = env.from_future("loop")            # 声明占位流
processed = source\
    .connect(future).co_map(LoopCoMap)      # 使用未来流参与计算

processed.fill_future(future)               # 闭合循环
```

典型用途：**机器学习在线迭代**、**告警抑制**、**流量增量补偿** 等。

---

## 总结

在本章中，介绍了 SAGE 中用于构建数据处理流程的核心机制 —— **DataStream Transformation**。通过链式组合多个算子，用户可以灵活实现从数据接入到结果输出的完整处理路径。

* **记录级转换**（如 `map`、`filter`、`flatmap`）提供了对每条数据的精细加工能力；
* **分区与重分布**（如 `keyby`）使得任务具备了按 Key 分组、并发处理与状态隔离的能力；
* **多流转换**（如 `connect`、`co_map`）支持异构流之间的融合，适用于配置驱动、实时联动等业务场景；
* **终端输出**（`sink`）则将处理结果写入外部系统，作为整个流任务的结束节点；
* 同时，SAGE 还支持 **反馈边（fill\_future）** 的构建，为循环依赖和迭代逻辑提供原生支持。

