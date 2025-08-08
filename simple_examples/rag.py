import time
from dotenv import load_dotenv
from sage.utils.custom_logger import CustomLogger
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.batch_function import BatchFunction
from sage.core.api.function.map_function import MapFunction
from sage.lib.io.sink import TerminalSink
from sage.lib.rag.promptor import QAPromptor
from sage.utils.config_loader import load_config
from my_operator.open_ai_generator import OpenAIGenerator
from sage.middleware.services.memory.memory_service import MemoryService


# ========== 界面美化工具函数 ==========
class UIHelper:
    """终端界面美化工具类"""
    
    # 颜色常量
    COLORS = {
        'HEADER': '\033[95m',
        'BLUE': '\033[94m',
        'CYAN': '\033[96m',
        'GREEN': '\033[92m',
        'YELLOW': '\033[93m',
        'RED': '\033[91m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m',
        'END': '\033[0m'
    }
    
    @staticmethod
    def print_header():
        """打印程序头部信息"""
        header = f"""
{UIHelper.COLORS['HEADER']}{UIHelper.COLORS['BOLD']}
╔══════════════════════════════════════════════════════════════╗
║                   🧠 SAGE RAG智能问答系统                    ║  
║              基于私密知识库的检索增强生成                      ║
╚══════════════════════════════════════════════════════════════╝
{UIHelper.COLORS['END']}"""
        print(header)
    
    @staticmethod
    def print_pipeline_diagram():
        """打印管道流程图"""
        diagram = f"""
{UIHelper.COLORS['YELLOW']}{UIHelper.COLORS['BOLD']}📊 RAG数据处理管道架构:{UIHelper.COLORS['END']}

{UIHelper.COLORS['CYAN']}┌─────────────────┐{UIHelper.COLORS['END']}    {UIHelper.COLORS['BLUE']}┌─────────────────┐{UIHelper.COLORS['END']}    {UIHelper.COLORS['GREEN']}┌─────────────────┐{UIHelper.COLORS['END']}
{UIHelper.COLORS['CYAN']}│   问题批处理源   │{UIHelper.COLORS['END']} ──▶ {UIHelper.COLORS['BLUE']}│   知识检索器     │{UIHelper.COLORS['END']} ──▶ {UIHelper.COLORS['GREEN']}│   提示词构造器   │{UIHelper.COLORS['END']}
{UIHelper.COLORS['CYAN']}│ PrivateQABatch  │{UIHelper.COLORS['END']}    {UIHelper.COLORS['BLUE']}│SafePrivateRetrie│{UIHelper.COLORS['END']}    {UIHelper.COLORS['GREEN']}│   QAPromptor    │{UIHelper.COLORS['END']}
{UIHelper.COLORS['CYAN']}└─────────────────┘{UIHelper.COLORS['END']}    {UIHelper.COLORS['BLUE']}└─────────────────┘{UIHelper.COLORS['END']}    {UIHelper.COLORS['GREEN']}└─────────────────┘{UIHelper.COLORS['END']}
           │                           │                           │
           ▼                           ▼                           ▼
    {UIHelper.COLORS['CYAN']}📝 批量问题生成{UIHelper.COLORS['END']}        {UIHelper.COLORS['BLUE']}🔍 向量检索知识{UIHelper.COLORS['END']}       {UIHelper.COLORS['GREEN']}📋 RAG提示模板{UIHelper.COLORS['END']}

{UIHelper.COLORS['RED']}┌─────────────────┐{UIHelper.COLORS['END']}    {UIHelper.COLORS['YELLOW']}┌─────────────────┐{UIHelper.COLORS['END']}
{UIHelper.COLORS['RED']}│   终端输出器     │{UIHelper.COLORS['END']} ◀── {UIHelper.COLORS['YELLOW']}│   AI生成器      │{UIHelper.COLORS['END']}
{UIHelper.COLORS['RED']}│  TerminalSink   │{UIHelper.COLORS['END']}    {UIHelper.COLORS['YELLOW']}│ OpenAIGenerator │{UIHelper.COLORS['END']}
{UIHelper.COLORS['RED']}└─────────────────┘{UIHelper.COLORS['END']}    {UIHelper.COLORS['YELLOW']}└─────────────────┘{UIHelper.COLORS['END']}
           │                           │
           ▼                           ▼
    {UIHelper.COLORS['RED']}🖥️  答案终端显示{UIHelper.COLORS['END']}        {UIHelper.COLORS['YELLOW']}🧠 LLM智能推理{UIHelper.COLORS['END']}
"""
        print(diagram)
    
    @staticmethod 
    def print_config_info(config):
        """打印配置信息"""
        model_info = config.get("generator", {}).get("remote", {})
        retriever_info = config.get("retriever", {})
        info = f"""
{UIHelper.COLORS['GREEN']}{UIHelper.COLORS['BOLD']}⚙️  系统配置信息:{UIHelper.COLORS['END']}
  🤖 AI模型: {UIHelper.COLORS['YELLOW']}{model_info.get('model_name', 'Unknown')}{UIHelper.COLORS['END']}
  🌐 API端点: {UIHelper.COLORS['CYAN']}{model_info.get('base_url', 'Unknown')}{UIHelper.COLORS['END']}
  📚 知识库: {UIHelper.COLORS['BLUE']}{retriever_info.get('collection_name', 'private_info_knowledge')}{UIHelper.COLORS['END']}
  🔍 检索TopK: {UIHelper.COLORS['HEADER']}{retriever_info.get('ltm', {}).get('topk', 3)}{UIHelper.COLORS['END']}
  📖 管道描述: 基于私密知识库的RAG智能问答系统
"""
        print(info)
    
    @staticmethod
    def print_knowledge_base_info(sentences_count):
        """打印知识库信息"""
        info = f"""
{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}📚 知识库信息:{UIHelper.COLORS['END']}
  📄 知识条目数: {UIHelper.COLORS['YELLOW']}{sentences_count}{UIHelper.COLORS['END']} 条
  🏷️  覆盖主题: {UIHelper.COLORS['GREEN']}张先生、李女士、王经理的个人物品位置{UIHelper.COLORS['END']}
  🔍 检索方式: {UIHelper.COLORS['BLUE']}向量相似度 + 关键词匹配{UIHelper.COLORS['END']}
  💾 存储后端: {UIHelper.COLORS['HEADER']}VectorDB{UIHelper.COLORS['END']}
"""
        print(info)
    
    @staticmethod
    def print_test_questions(questions):
        """打印测试问题列表"""
        info = f"""
{UIHelper.COLORS['YELLOW']}{UIHelper.COLORS['BOLD']}❓ 预设测试问题:{UIHelper.COLORS['END']}"""
        print(info)
        for i, question in enumerate(questions, 1):
            print(f"  {UIHelper.COLORS['CYAN']}{i}.{UIHelper.COLORS['END']} {question}")
        print()
    
    @staticmethod
    def format_success(msg):
        """格式化成功信息"""
        return f"{UIHelper.COLORS['GREEN']}{UIHelper.COLORS['BOLD']}✅ {msg}{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_error(msg):
        """格式化错误信息"""
        return f"{UIHelper.COLORS['RED']}{UIHelper.COLORS['BOLD']}❌ {msg}{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_warning(msg):
        """格式化警告信息"""
        return f"{UIHelper.COLORS['YELLOW']}{UIHelper.COLORS['BOLD']}⚠️  {msg}{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_info(msg):
        """格式化信息"""
        return f"{UIHelper.COLORS['BLUE']}{UIHelper.COLORS['BOLD']}ℹ️  {msg}{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_processing(msg):
        """格式化处理信息"""
        return f"{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}🔄 {msg}{UIHelper.COLORS['END']}"

# 移除 PrivateKnowledgeBuilder 类，改为在 memory service factory 中处理


class PrivateQABatch(BatchFunction):
    """
    私密信息QA批处理数据源：内置私密问题列表
    """
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.questions = [
            "张先生的手机通常放在什么地方？",
            "李女士喜欢把钱包放在哪里？", 
            "王经理的办公室钥匙通常在哪里？",
            "张先生什么时候会去咖啡厅工作？",
            "李女士的重要证件放在什么地方？"
        ]

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


class SafePrivateRetriever(MapFunction):
    """使用 memory service 的私密信息知识检索器"""
    def __init__(self, config=None, **kwargs):
        super().__init__(**kwargs)
        self.collection_name = "private_info_knowledge"

    def execute(self, data):
        if not data:
            return None

        query = data
        print(f"   {UIHelper.COLORS['BLUE']}🔍 检索问题: {query}{UIHelper.COLORS['END']}")
        
        # 使用 memory service 检索相关信息
        result = self.call_service["memory_service"].retrieve_data(
            collection_name=self.collection_name,
            query_text=query,
            topk=3,
            with_metadata=True
        )
        
        if result['status'] == 'success':
            retrieved_texts = [item.get('text', '') for item in result['results']]
            print(f"   {UIHelper.COLORS['GREEN']}📋 找到 {len(retrieved_texts)} 条相关信息{UIHelper.COLORS['END']}")
            return (query, retrieved_texts)
        else:
            print(f"   {UIHelper.COLORS['RED']}❌ 检索失败: {result['message']}{UIHelper.COLORS['END']}")
            return (query, [])


def pipeline_run() -> None:
    """创建并运行数据处理管道"""
    
    config = load_config("config_batch.yaml")   
     
    # 创建本地环境
    env = LocalEnvironment()
    
    # 注册 memory service 并预先插入知识数据
    def memory_service_factory():
        """创建 memory service 并预先插入私密信息知识"""
        # 私密信息知识句子
        knowledge_sentences = [
            "张先生通常将手机放在办公桌右侧的抽屉里，充电线在左侧抽屉。",
            "张先生的车钥匙一般放在玄关柜的小盒子里，备用钥匙在卧室梳妆台。",
            "张先生喜欢在周二和周四的下午3点去附近的咖啡厅工作。",
            "李女士喜欢把钱包放在手提包的内侧拉链袋中，从不放在外层。",
            "李女士的护照和重要证件放在卧室衣柜顶层的蓝色文件夹里。",
            "李女士的手机通常放在卧室床头柜上，但钥匙放在厨房抽屉里。",
            "王经理的办公室钥匙通常挂在腰间的钥匙扣上，备用钥匙在秘书那里。",
            "王经理开会时习惯带着黑色的皮质记事本，里面记录着重要联系人信息。",
            "王经理的手机放在办公桌上，但重要文件锁在保险柜里。",
            "张先生的钱包放在裤子口袋里，李女士的证件在抽屉中。"
        ]
        
        # 创建 memory service 实例
        memory_service = MemoryService()
        collection_name = "private_info_knowledge"
        
        # 创建集合
        result = memory_service.create_collection(
            name=collection_name,
            backend_type="VDB",
            description="Private information RAG knowledge base"
        )
        
        if result['status'] == 'success':
            print(UIHelper.format_success("知识库集合创建成功"))
            
            # 预先插入知识句子
            print(UIHelper.format_processing("正在插入私密信息知识..."))
            success_count = 0
            
            for i, sentence in enumerate(knowledge_sentences):
                insert_result = memory_service.insert_data(
                    collection_name=collection_name,
                    text=sentence,
                    metadata={
                        "id": i + 1, 
                        "topic": "private_info", 
                        "type": "knowledge", 
                        "source": "manual",
                        "date": "2025-07-31"
                    }
                )
                
                if insert_result['status'] == 'success':
                    success_count += 1
                else:
                    print(UIHelper.format_error(f"插入第 {i+1} 条知识失败: {insert_result['message']}"))
            
            print(UIHelper.format_success(f"成功插入 {success_count}/{len(knowledge_sentences)} 条私密信息知识"))
            
        else:
            print(UIHelper.format_error(f"创建知识库集合失败: {result['message']}"))
            
        return memory_service
    
    # 注册服务到环境中
    env.register_service("memory_service", memory_service_factory)
    
    # 显示界面信息
    UIHelper.print_header()
    UIHelper.print_pipeline_diagram()
    UIHelper.print_config_info(config)
    UIHelper.print_knowledge_base_info(10)  # 10 条知识
    
    # 获取问题列表用于显示
    test_questions = [
        "张先生的手机通常放在什么地方？",
        "李女士喜欢把钱包放在哪里？", 
        "王经理的办公室钥匙通常在哪里？",
        "张先生什么时候会去咖啡厅工作？",
        "李女士的重要证件放在什么地方？"
    ]
    UIHelper.print_test_questions(test_questions)

    # 构建处理管道
    (env
        .from_batch(PrivateQABatch)
        .map(SafePrivateRetriever)
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["remote"])
        .sink(TerminalSink, config["sink"])
    )

    try:
        print("🚀 开始RAG问答处理...")
        print(f"📊 处理流程: 问题源 → 知识检索 → Prompt构建 → AI生成 → 结果输出")
        print("=" * 60)
        env.submit()
        time.sleep(3)
    except KeyboardInterrupt:
        print("⚠️  测试中断")
    finally:
        print("=" * 60)
        print("🏁 测试结束")
        env.close()


if __name__ == '__main__':
    CustomLogger.disable_global_console_debug()
    load_dotenv(override=False)
    pipeline_run()