"""
RAG智能问答系统 - 重构版
基于私密知识库的检索增强生成
使用模块化组件实现
"""
from sage.lib.io.sink import TerminalSink
from sage.lib.rag.promptor import QAPromptor
from ..operators.openai_generator import OpenAIGenerator

from ..utils.ui_helper import UIHelper
from ..utils.base_operators import BaseQuestionSource, BaseMemoryRetriever
from ..utils.memory_helper import MemoryServiceHelper, KnowledgeDatasets
from ..utils.common import PipelineRunner


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


def main():
    """主函数"""
    runner = RAGPipelineRunner()
    runner.run()


if __name__ == '__main__':
    main()
