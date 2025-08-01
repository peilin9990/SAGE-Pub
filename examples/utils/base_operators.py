"""
Base operators for SAGE examples
提供通用的操作符基类和常用实现
"""
import sys
import time
from typing import Any, List, Tuple, Dict, Optional
from sage.core.function.map_function import MapFunction
from sage.core.function.sink_function import SinkFunction
from sage.core.function.source_function import SourceFunction
from sage.core.function.batch_function import BatchFunction
from .ui_helper import UIHelper


class BaseQuestionSource(BatchFunction):
    """基础问题源类"""
    
    def __init__(self, questions: List[str], config=None, **kwargs):
        super().__init__(**kwargs)
        self.questions = questions
        self.counter = 0

    def execute(self):
        """返回下一个问题，如果没有更多问题则返回None"""
        if self.counter >= len(self.questions):
            print(UIHelper.format_success("所有问题处理完成"))
            return None  # 返回None表示批处理完成

        question = self.questions[self.counter]
        print(f"\n{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}📝 正在处理第 {self.counter + 1}/{len(self.questions)} 个问题:{UIHelper.COLORS['END']}")
        print(f"   {UIHelper.COLORS['YELLOW']}❓ {question}{UIHelper.COLORS['END']}")
        self.counter += 1
        return question


class TerminalInputSource(SourceFunction):
    """终端输入源函数 - 改进版，控制输入时机"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.first_run = True
    
    def execute(self, data=None):
        # 如果不是第一次运行，添加一个小延迟让用户有时间阅读答案
        if not self.first_run:
            time.sleep(1.5)  # 给用户1.5秒时间阅读答案
            print()  # 添加空行分隔
        else:
            self.first_run = False
            
        while True:
            try:
                # 显示美化的输入提示符并获取输入
                user_input = input(UIHelper.format_input_prompt()).strip()
                
                if user_input:
                    return user_input
                else:
                    # 空输入时给予提示，继续等待
                    print(f"{UIHelper.COLORS['YELLOW']}⚠️  请输入有效问题{UIHelper.COLORS['END']}")
                    continue
                    
            except KeyboardInterrupt:
                print(UIHelper.format_success("\n✅ 感谢使用，再见！"))
                sys.exit(0)
            except EOFError:
                print(UIHelper.format_success("\n✅ 感谢使用，再见！"))
                sys.exit(0)


class QuestionProcessor(MapFunction):
    """问题处理器 - 清理和验证输入"""
    
    def execute(self, data):
        if not data or data.strip() == "":
            return None
        
        # 显示处理状态
        print(UIHelper.format_thinking())
        return data.strip()


class AnswerFormatter(MapFunction):
    """回答格式化器"""
    
    def execute(self, data):
        if not data:
            return None

        # OpenAIGenerator返回的格式是 (user_query, generated_text)
        if isinstance(data, tuple) and len(data) >= 2:
            user_query = data[0]
            answer = data[1]
            return {
                "question": user_query if user_query else "N/A",
                "answer": answer,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            return {
                "question": "N/A", 
                "answer": str(data),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }


class ConsoleSink(SinkFunction):
    """控制台输出 - 改进版，提供更好的用户体验"""
    
    def execute(self, data):
        if not data:
            return None

        if isinstance(data, dict):
            question = data.get('question', 'N/A')
            answer = data.get('answer', 'N/A')
            timestamp = data.get('timestamp', '')
            
            # 使用UIHelper的格式化输出
            output = UIHelper.format_answer_output(question, answer, timestamp)
            print(output)
            
            # 添加分隔线，表示当前回答完成
            print(f"{UIHelper.COLORS['CYAN']}{'─' * 60}{UIHelper.COLORS['END']}")
            
        else:
            print(f"\n{UIHelper.COLORS['GREEN']}🤖 {data}{UIHelper.COLORS['END']}")
            # 添加分隔线，表示当前回答完成
            print(f"{UIHelper.COLORS['CYAN']}{'─' * 60}{UIHelper.COLORS['END']}")

        return data


class BaseMemoryRetriever(MapFunction):
    """基础记忆检索器"""
    
    def __init__(self, collection_name: str, topk: int = 3, config=None, **kwargs):
        super().__init__(**kwargs)
        self.collection_name = collection_name
        self.topk = topk

    def execute(self, data):
        if not data:
            return None

        query = data
        print(f"   {UIHelper.COLORS['BLUE']}🔍 检索问题: {query}{UIHelper.COLORS['END']}")
        
        # 使用 memory service 检索相关信息
        result = self.call_service["memory_service"].retrieve_data(
            collection_name=self.collection_name,
            query_text=query,
            topk=self.topk,
            with_metadata=True
        )
        
        if result['status'] == 'success':
            retrieved_texts = [item.get('text', '') for item in result['results']]
            print(f"   {UIHelper.COLORS['GREEN']}📋 找到 {len(retrieved_texts)} 条相关信息{UIHelper.COLORS['END']}")
            return (query, retrieved_texts)
        else:
            print(f"   {UIHelper.COLORS['RED']}❌ 检索失败: {result['message']}{UIHelper.COLORS['END']}")
            return (query, [])
