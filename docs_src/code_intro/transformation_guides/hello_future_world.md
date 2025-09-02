# Hello Future World 编程指南（反馈边与循环流）

本指南基于示例 `examples/tutorials/transformation-api/hello_future_world.py`，讲解反馈边与循环：

- env.from_future 占位流
- DataStream.connect + ConnectedStreams.comap
- DataStream.fill_future 将结果回填到未来流，形成闭环

## 场景概述

- StartSource 发送一次启动信号
- 与反馈流 connect 后 comap 统一处理
- SentenceProvider 在收到反馈后向前推进，依次提供句子
- Sink 打印后经 FeedbackDelayer 延迟一段时间，再回填到 future 流，触发下一轮

## 关键类与接口

- LocalEnvironment：执行环境
- from_source / from_future：分别创建源与未来流占位
- BaseCoMapFunction：合流处理器
- BaseFunction/MapFunction：在流上做一步处理
- SinkFunction：终端输出

## 示例拆解

1) start_stream = env.from_source(StartSource)

2) feedback_stream = env.from_future("feedback")

3) merged = start_stream.connect(feedback_stream).comap(SignalMerger)

4) provided = merged.map(SentenceProvider)

5) sinked = provided.sink(FeedbackSink)

6) delayed = sinked.map(FeedbackDelayer)

7) delayed.fill_future(feedback_stream)  # 闭环

## 常见陷阱与建议

- 循环必须有“节流”环节（示例中的延迟），避免忙等与资源耗尽。
- from_future 必须最终被 fill_future 闭合；否则合流会一直等待反馈导致停滞。
- 有状态处理器要考虑多次反馈时的状态推进与边界退出条件。

## 扩展示例

- 在线学习：预测→评估→参数更新→再预测的迭代闭环。
- 告警抑制：阈值触发→观察窗口→确认/抑制→反馈下一轮。

!!! warning "注意"
	循环拓扑务必加入节流环节（示例中通过 `sleep`），否则可能造成忙等与资源耗尽；另外请确保 `from_future` 最终被 `fill_future` 回填闭合。

## 示例代码

```python title="examples/tutorials/transformation-api/hello_future_world.py" linenums="1"
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.comap_function import BaseCoMapFunction
from sage.core.api.function.base_function import BaseFunction
from sage.core.api.function.batch_function import BatchFunction
from sage.core.api.function.sink_function import SinkFunction
from sage.common.utils.logging.custom_logger import CustomLogger
from time import sleep

# 启动信号源（只发一次启动信号）
class StartSource(BatchFunction):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.started = False

	def execute(self):
		if not self.started:
			self.started = True
			print("已发送启动信号")
			return {"signal": "start"}
		else:
			return None


# 合流处理器（map0 = 启动，map1 = 反馈）
class SignalMerger(BaseCoMapFunction):
	def map0(self, data):
		print(f">>> StartSource：收到启动数据: {data}")
		return data

	def map1(self, data):
		print(f">>> PipelineSource： 收到反馈数据: {data}")
		return data


# 从语句列表中按顺序取语句（只在收到反馈时推进）
class SentenceProvider(BatchFunction):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.sentences = [
			"这是第一句。",
			"这是第二句。",
			"这是第三句。",
			"所有语句已完成！"
		]
		self.index = 0

	def execute(self, data):
		if data is None:
			return None

		if self.index >= len(self.sentences):
			print("全部语句已输出完毕，结束数据流。")
			return None

		sentence = self.sentences[self.index]
		self.index += 1
		new_data = {"句子": sentence}
		print(f">>> SentenceProvider 提供句子: {new_data}")
		return new_data


# Sink：打印句子（立即打印，不加 sleep）
class FeedbackSink(SinkFunction):
	def execute(self, data):
		if data:
			print(f">>> Sink 打印: {data}")
		return data


# 延迟反馈算子：控制节奏
class FeedbackDelayer(BaseFunction):
	def execute(self, data):
		if data is None:
			return None
		sleep(1)  # 控制间隔
		print(">>> FeedbackDelayer等待 2 秒后反馈...")
		return data


def main():
	env = LocalEnvironment("句子顺序输出")

	# 1. 启动源
	start_stream = env.from_source(StartSource)

	# 2. future stream 用于反馈
	feedback_stream = env.from_future("feedback")

	# 3. 合流
	merged = start_stream.connect(feedback_stream).comap(SignalMerger)

	# 4. 语句提供器
	provided = merged.map(SentenceProvider)

	# 5. Sink，打印结果
	sinked = provided.sink(FeedbackSink)

	# 6. 在反馈前加延迟
	delayed = sinked.map(FeedbackDelayer)

	# 7. 把延迟后的结果反馈到 future stream
	delayed.fill_future(feedback_stream)


	env.submit()

	from time import sleep
	sleep(6)  # 给足够时间让所有数据处理完成

	print("Hello Future World 示例结束")

if __name__ == "__main__":
	CustomLogger.disable_global_console_debug()
	main()

```
