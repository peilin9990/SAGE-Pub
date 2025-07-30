# DataStream Operator 与 Function

在 SAGE 的数据处理模型中，`Function` 和 `Operator` 是支撑整个 DataStream 数据转换过程的核心构件，简而言之：

* **`Function` 是用户实现的业务逻辑模块** —— 你只需继承合适的 Base Function 类型并实现 `execute()` 方法，告诉系统你想“对数据做什么”。
* **`Operator` 是系统自动生成和调度的执行器** —— 它负责“如何执行你的逻辑”以及“在什么地方执行”（比如分布式线程、流调度、并发机制等），**用户无需直接操作或创建 Operator**。

[![DataStream Function](../../assets/img/function.png  "function实现与提交")](../../assets/img/function.png)

如图，在 SAGE 中，用户只需要选择合适的 Base Function 类型（如 `MapFunction`）并实现其核心逻辑，系统会在后续为其**创建匹配的 Operator**，并负责执行调度、资源管理、容错等所有底层细节。

---

## Function 类型总览

SAGE 中提供了一组标准 Base Function 类型，供用户继承并实现自定义的数据处理逻辑，你可以点击具体的 Function 查看用法：

| Function 类型       | 用途描述              |
| ----------------- | ----------------- |
| [`MapFunction`](#mapfunction) | 对每条数据进行一对一转换 | 
| [`FilterFunction`](#filterfunction) | 按条件筛选，仅保留满足条件的数据 |
| [`FlatMapFunction`](#flatmapfunction) | 将一条输入数据拆分为多条输出数据 |
| [`KeyByFunction`](#keybyfunction) | 提取关键字段，实现按 *key* 分区 | 
| [`SinkFunction`](#sinkfunction) | 将数据写出到终端、文件或外部系统 |
| [`BatchFunction`](#batchfunction) | 用于**批处理**模式下的数据源 |
| [`SourceFunction`](#sourcefunction) | 用于**流式**模式下的数据源 |
| [`CoMapFunction`](#comapfunction) | 用于处理双输入流的组合逻辑 |

### Function 编写示例

每个 Function 都需要实现一个或多个方法，最常见的是 `execute()` 方法。例如：

```python
class MyMap(MapFunction):
    def execute(self, value):
        return value * 2
```

### Function 传参示例

你可以在 Function 中定义构造函数（`__init__`），SAGE 支持通过 `.map(MyFunction, config)` 的方式注入参数。

```python
class MyFunction(MapFunction):
    def __init__(self, config):
        self.factor = config.get("factor")

    def execute(self, value):
        return value * self.factor

# 使用方式
mydatastream.map(MyFunction, config)
```

### Function 生命周期

Function 在算子执行过程中的生命周期包括：

1. `__init__()`：构造函数，在创建时调用，可接收参数；
2. `open()`：任务启动时（可选）调用，一般用于连接资源；
3. `execute()`：核心处理逻辑，每条数据到达时调用；
4. `close()`：任务结束时调用，用于资源释放等清理操作。

---

## Operator 原理解析

每一个 Function 在运行时都会由其对应的 `Operator` 包装和调度，Operator 负责：

* 接收上游数据
* 调用 Function 的 `execute()` 或其他接口方法
* 处理数据流传递、并发与容错
* 与底层调度器（如 LocalEnvironment）集成

系统会根据提交数据流选择合适的 Operator 来包装你的 Function，以下是两者的运行时关系图：

```
输入数据 → Operator.receive() 
          → Function.execute()
            → 输出数据 → 下游 Operator.receive()
```

---

## Function 类型详解

### MapFunction <a id="mapfunction"></a>

对每条数据做一对一转换。

```python
class Upper(MapFunction):
    def execute(self, s: str):
        return s.upper()

ds.map(Upper)
```


### FilterFunction <a id="filterfunction"></a>

N条数据输入，M条数据流出，按条件保留数据（N ≥ M）：

```python
class IsPositive(FilterFunction):
    def execute(self, x):
        return x > 0

ds.filter(IsPositive)
```

### FlatMapFunction <a id="flatmapfunction"></a>

一条数据输出多条数据，支持返回列表或调用 `collector.collect()`。

```python
class Split(FlatMapFunction):
    def execute(self, sentence):
        return sentence.split()
```

或使用 `collector`：

```python
class Split(FlatMapFunction):
    def execute(self, sentence, collector):
        for word in sentence.split():
            collector.collect(word)
```

### KeyByFunction <a id="keybyfunction"></a>

一条数据流转为多条数据流，为数据指定 Key，实现分区：

```python
ds.keyby(lambda x: x["user_id"], strategy="hash")
```

支持策略包括 `"hash"`、`"round_robin"`、`"broadcast"`。

### SinkFunction <a id="sinkfunction"></a>

将最终数据写入文件、终端、数据库等：

```python
class PrintSink(SinkFunction):
    def execute(self, value):
        print(value)

ds.sink(PrintSink)
```

### BatchFunction <a id="batchfunction"></a>

用于生成有限批量数据：

```python
class HelloBatch(BatchFunction):
    def __init__(self):
        self.counter = 0

    def execute(self):
        if self.counter >= 5:
            return None
        self.counter += 1
        return f"Hello #{self.counter}"

env.from_batch(HelloBatch)
```

### SourceFunction <a id="sourcefunction"></a>

用于生成无限流数据，例如读取 socket：

```python
class MySocket(SourceFunction):
    def run(self, ctx):
        while True:
            data = read_socket()
            ctx.collect(data)
```

### CoMapFunction <a id="comapfunction"></a>

处理双输入流，分别实现 `map1()` 和 `map2()`：

```python
class TagSource(CoMapFunction):
    def map1(self, a):
        return ("A", a)

    def map2(self, b):
        return ("B", b)

ds1.connect(ds2).co_map(TagSource)
```

---

## 总结

在本章中，我们深入讲解了 SAGE 中 `Function` 与 `Operator` 的角色与配合机制：

* **Function 是业务逻辑的核心单元**，用户只需关注“如何处理一条数据”，通过继承内置函数类型（如 `MapFunction`, `FilterFunction` 等）实现 `execute()` 方法。
* **Operator 是系统执行引擎的调度载体**，负责承载 Function 的执行、数据的输入输出、并发调度、状态维护与容错恢复等复杂逻辑，**由系统自动创建与管理**。
* SAGE 提供多种 Function 类型，涵盖流入（如 `BatchFunction`、`SourceFunction`）、转换（如 `MapFunction`、`FlatMapFunction`、`FilterFunction`）、多流操作（如 `CoMapFunction`）以及流出（如 `SinkFunction`）的完整生命周期。
* 用户可以通过构造函数注入参数、实现 `open()` 和 `close()` 方法来精细控制资源管理和初始化/清理流程。
* 通过 Operator 与调度系统的配合，用户只需专注于编写最小颗粒度的逻辑模块，系统即可高效、安全地完成整个流处理拓扑的构建与执行。

下一章将讲述：**数据流转换（Transformation）**，我们将详细讲解如何使用 `.map()`、`.filter()`、`.keyby()` 等 API，灵活组合各类 Function，构建完整、可运行的流处理管道。
