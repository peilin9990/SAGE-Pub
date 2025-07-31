"""
SAGE 示例工厂 - 统一入口点
快速创建和运行不同类型的QA系统
展示模块化设计的优势：通过组合不同的组件快速构建不同功能的系统
"""
import time
from sage.lib.rag.promptor import QAPromptor
from sage.lib.io.sink import TerminalSink
from examples.operators.openai_generator import OpenAIGenerator

from examples.utils.ui_helper import UIHelper
from examples.utils.base_operators import (
    BaseQuestionSource, TerminalInputSource, QuestionProcessor, 
    AnswerFormatter, ConsoleSink, BaseMemoryRetriever
)
from examples.utils.memory_helper import MemoryServiceHelper, KnowledgeDatasets
from examples.utils.common import PipelineRunner


class ExampleFactory:
    """示例工厂类 - 包含所有示例的实现"""
    
    @staticmethod
    def create_simple_qa():
        """创建简单QA系统（无记忆）"""
        class SimpleQAPipelineRunner(PipelineRunner):
            def __init__(self):
                super().__init__("config_source.yaml")
            
            def build_pipeline(self):
                UIHelper.print_sage_header("🎯 简单QA系统", "直接对话，无记忆检索")
                
                components = [
                    ("TerminalInput", "📝 用户输入"),
                    ("QAPromptor", "📋 提示构造"),
                    ("OpenAIGenerator", "🧠 AI生成"),
                    ("ConsoleSink", "🖥️  结果输出")
                ]
                UIHelper.print_pipeline_diagram(components)
                
                tips = [
                    f"输入任何问题后按 {UIHelper.COLORS['YELLOW']}Enter{UIHelper.COLORS['END']} 键提交",
                    f"按 {UIHelper.COLORS['RED']}Ctrl+C{UIHelper.COLORS['END']} 退出程序",
                    "空输入将被忽略，请输入有效问题",
                    "程序支持中英文问答"
                ]
                UIHelper.print_usage_tips(tips)
                
                print(f"{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}🚀 系统就绪，等待您的问题...{UIHelper.COLORS['END']}")
                UIHelper.print_separator()
                
                (self.env
                    .from_source(TerminalInputSource)
                    .map(QuestionProcessor)
                    .map(QAPromptor, self.config["promptor"])
                    .map(OpenAIGenerator, self.config["generator"]["remote"])
                    .map(AnswerFormatter)
                    .sink(ConsoleSink)
                )
            
            def run(self):
                """运行管道 - 重写以支持无界流"""
                try:
                    self.register_services()
                    self.build_pipeline()
                    
                    # 提交并运行
                    self.env.submit()
                    
                    # 保持主线程运行，直到用户退出
                    while True:
                        time.sleep(1)

                except KeyboardInterrupt:
                    print(f"\n{UIHelper.format_success('用户主动退出程序')}")
                except Exception as e:
                    print(UIHelper.format_error(f"管道运行出错: {str(e)}"))
                finally:
                    try:
                        self.env.close()
                        print(UIHelper.format_success("QA流处理管道已关闭"))
                    except:
                        pass
        
        return SimpleQAPipelineRunner()
    
    @staticmethod
    def create_batch_rag():
        """创建批量RAG系统（私密信息）"""
        class PrivateQABatch(BaseQuestionSource):
            """私密信息QA批处理数据源"""
            def __init__(self, config=None, **kwargs):
                dataset = KnowledgeDatasets.get_dataset("private_info")
                super().__init__(dataset["questions"], config, **kwargs)

        class SafePrivateRetriever(BaseMemoryRetriever):
            """使用 memory service 的私密信息知识检索器"""
            def __init__(self, config=None, **kwargs):
                super().__init__(collection_name="private_info_knowledge", topk=3, config=config, **kwargs)

        class RAGPipelineRunner(PipelineRunner):
            """RAG管道运行器"""
            def __init__(self):
                super().__init__("config_batch.yaml")
            
            def register_services(self):
                """注册记忆服务"""
                dataset = KnowledgeDatasets.get_dataset("private_info")
                
                def memory_service_factory():
                    return MemoryServiceHelper.create_memory_service_with_knowledge(
                        collection_name=dataset["collection_name"],
                        knowledge_sentences=dataset["knowledge"],
                        description=dataset["description"]
                    )
                
                self.env.register_service("memory_service", memory_service_factory)
            
            def build_pipeline(self):
                """构建RAG处理管道"""
                # 显示界面信息
                UIHelper.print_sage_header("🧠 SAGE RAG智能问答系统", "基于私密知识库的检索增强生成")
                
                # 管道组件描述
                components = [
                    ("PrivateQABatch", "📝 批量问题生成"),
                    ("SafePrivateRetriever", "🔍 向量检索知识"),
                    ("QAPromptor", "📋 RAG提示模板"),
                    ("OpenAIGenerator", "🧠 LLM智能推理"),
                    ("TerminalSink", "🖥️  答案终端显示")
                ]
                UIHelper.print_pipeline_diagram(components)
                UIHelper.print_config_info(self.config)
                
                dataset = KnowledgeDatasets.get_dataset("private_info")
                UIHelper.print_knowledge_base_info(len(dataset["knowledge"]), dataset["collection_name"])
                UIHelper.print_test_questions(dataset["questions"])

                # 构建处理管道
                (self.env
                    .from_batch(PrivateQABatch)
                    .map(SafePrivateRetriever)
                    .map(QAPromptor, self.config["promptor"])
                    .map(OpenAIGenerator, self.config["generator"]["remote"])
                    .sink(TerminalSink, self.config["sink"])
                )

        return RAGPipelineRunner()
    
    @staticmethod
    def create_interactive_rag():
        """创建交互式RAG系统"""
        class InteractiveRetriever(BaseMemoryRetriever):
            def __init__(self, config=None, **kwargs):
                super().__init__(collection_name="private_info_knowledge", topk=3, config=config, **kwargs)
        
        class InteractiveRAGPipelineRunner(PipelineRunner):
            def __init__(self):
                super().__init__("config_source.yaml")
            
            def register_services(self):
                dataset = KnowledgeDatasets.get_dataset("private_info")
                def memory_service_factory():
                    return MemoryServiceHelper.create_memory_service_with_knowledge(
                        collection_name=dataset["collection_name"],
                        knowledge_sentences=dataset["knowledge"],
                        description=dataset["description"]
                    )
                self.env.register_service("memory_service", memory_service_factory)
            
            def build_pipeline(self):
                UIHelper.print_sage_header("🔄 交互式RAG系统", "实时对话 + 知识检索")
                
                components = [
                    ("TerminalInput", "📝 交互输入"),
                    ("MemoryRetriever", "🔍 知识检索"),
                    ("QAPromptor", "📋 RAG提示"),
                    ("OpenAIGenerator", "🧠 AI推理"),
                    ("ConsoleSink", "🖥️  美化输出")
                ]
                UIHelper.print_pipeline_diagram(components)
                
                tips = [
                    "基于私密知识库的交互式问答",
                    "每个问题都会检索相关知识",
                    f"按 {UIHelper.COLORS['RED']}Ctrl+C{UIHelper.COLORS['END']} 退出程序"
                ]
                UIHelper.print_usage_tips(tips)
                
                print(f"{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}🚀 RAG系统就绪，开始智能问答...{UIHelper.COLORS['END']}")
                UIHelper.print_separator()
                
                (self.env
                    .from_source(TerminalInputSource)
                    .map(QuestionProcessor)
                    .map(InteractiveRetriever)
                    .map(QAPromptor, self.config["promptor"])
                    .map(OpenAIGenerator, self.config["generator"]["remote"])
                    .map(AnswerFormatter)
                    .sink(ConsoleSink)
                )
            
            def run(self):
                """运行管道 - 重写以支持无界流"""
                try:
                    self.register_services()
                    self.build_pipeline()
                    
                    # 提交并运行
                    self.env.submit()
                    
                    # 保持主线程运行，直到用户退出
                    while True:
                        time.sleep(1)

                except KeyboardInterrupt:
                    print(f"\n{UIHelper.format_success('用户主动退出程序')}")
                except Exception as e:
                    print(UIHelper.format_error(f"管道运行出错: {str(e)}"))
                finally:
                    try:
                        self.env.close()
                        print(UIHelper.format_success("RAG流处理管道已关闭"))
                    except:
                        pass
        
        return InteractiveRAGPipelineRunner()
    
    @staticmethod
    def create_batch_qa_with_custom_knowledge(knowledge_list, questions_list, collection_name="custom_knowledge"):
        """创建自定义知识库的批量QA系统"""
        class CustomBatchQAPipelineRunner(PipelineRunner):
            def __init__(self):
                super().__init__("config_batch.yaml")
                self.knowledge_list = knowledge_list
                self.questions_list = questions_list
                self.collection_name = collection_name
            
            def register_services(self):
                def memory_service_factory():
                    return MemoryServiceHelper.create_memory_service_with_knowledge(
                        collection_name=self.collection_name,
                        knowledge_sentences=self.knowledge_list,
                        description=f"Custom knowledge base: {self.collection_name}"
                    )
                self.env.register_service("memory_service", memory_service_factory)
            
            def build_pipeline(self):
                UIHelper.print_sage_header("📚 自定义知识库QA", f"基于{len(self.knowledge_list)}条知识的RAG系统")
                
                components = [
                    ("CustomQABatch", "📝 自定义问题"),
                    ("CustomRetriever", "🔍 知识检索"),
                    ("QAPromptor", "📋 RAG提示"),
                    ("OpenAIGenerator", "🧠 AI推理"),
                    ("TerminalSink", "🖥️  输出")
                ]
                UIHelper.print_pipeline_diagram(components)
                UIHelper.print_knowledge_base_info(len(self.knowledge_list), self.collection_name)
                UIHelper.print_test_questions(self.questions_list)
                
                # 动态创建问题源和检索器
                class CustomQABatch(BaseQuestionSource):
                    def __init__(self, config=None, **kwargs):
                        super().__init__(questions_list, config, **kwargs)
                
                class CustomRetriever(BaseMemoryRetriever):
                    def __init__(self, config=None, **kwargs):
                        super().__init__(collection_name=collection_name, topk=3, config=config, **kwargs)
                
                (self.env
                    .from_batch(CustomQABatch)
                    .map(CustomRetriever)
                    .map(QAPromptor, self.config["promptor"])
                    .map(OpenAIGenerator, self.config["generator"]["remote"])
                    .sink(TerminalSink, self.config["sink"])
                )
        
        return CustomBatchQAPipelineRunner()


def demo_custom_knowledge():
    """演示自定义知识库"""
    # 科技公司知识库
    tech_knowledge = [
        "Apple公司成立于1976年，总部位于加利福尼亚州库比蒂诺。",
        "Google的搜索引擎算法叫做PageRank，由Larry Page和Sergey Brin发明。",
        "Microsoft Windows操作系统首次发布于1985年。",
        "Amazon最初是一家在线书店，成立于1994年。",
        "Facebook现在叫做Meta，专注于社交媒体和元宇宙技术。",
        "Tesla是一家电动汽车制造商，由Elon Musk领导。",
        "Netflix最初是DVD租赁服务，后来转型为流媒体平台。"
    ]
    
    tech_questions = [
        "Apple公司什么时候成立的？",
        "Google的搜索算法叫什么名字？",
        "Microsoft Windows什么时候发布？",
        "Amazon最初是做什么业务的？",
        "Facebook现在叫什么名字？"
    ]
    
    runner = ExampleFactory.create_batch_qa_with_custom_knowledge(
        tech_knowledge, tech_questions, "tech_company_knowledge"
    )
    runner.run()


def main():
    """主函数 - 统一入口点"""
    print("🏭 SAGE 示例工厂 - 选择要运行的系统类型：")
    print("1. 简单QA系统（无记忆）")
    print("2. 批量RAG系统（私密信息）")
    print("3. 交互式RAG系统")
    print("4. 自定义知识库（科技公司）")
    
    choice = input("请选择 (1-4): ").strip()
    
    if choice == "1":
        print("\n🎯 启动简单QA系统...")
        runner = ExampleFactory.create_simple_qa()
        runner.run()
    elif choice == "2":
        print("\n🧠 启动批量RAG系统...")
        runner = ExampleFactory.create_batch_rag()
        runner.run()
    elif choice == "3":
        print("\n🔄 启动交互式RAG系统...")
        runner = ExampleFactory.create_interactive_rag()
        runner.run()
    elif choice == "4":
        print("\n📚 启动自定义知识库系统...")
        demo_custom_knowledge()
    else:
        print("❌ 无效选择，默认运行简单QA系统")
        runner = ExampleFactory.create_simple_qa()
        runner.run()


if __name__ == "__main__":
    main()
