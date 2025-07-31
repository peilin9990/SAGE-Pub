"""
终端交互式QA无界流处理
支持终端输入问题，使用大模型生成回答的无界流处理示例
"""
# 加载一些工具类
import time
import sys
from dotenv import load_dotenv
from sage.utils.config_loader import load_config
from sage.utils.custom_logger import CustomLogger

# 加载SAGE核心组件
from sage.core.api.local_environment import LocalEnvironment
from sage.core.function.map_function import MapFunction
from sage.core.function.sink_function import SinkFunction
from sage.core.function.source_function import SourceFunction

# 加载SAGE Lib或自行实现的算子
from sage.lib.rag.promptor import QAPromptor
from my_operator.open_ai_generator import OpenAIGenerator


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
{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}
╔══════════════════════════════════════════════════════════════╗
║                    🤖 SAGE QA助手 v1.0                      ║  
║              智能问答无界流处理系统                            ║
╚══════════════════════════════════════════════════════════════╝
{UIHelper.COLORS['END']}"""
        print(header)
    
    @staticmethod
    def print_pipeline_diagram():
        """打印管道流程图"""
        diagram = f"""
{UIHelper.COLORS['YELLOW']}{UIHelper.COLORS['BOLD']}📊 数据流管道架构:{UIHelper.COLORS['END']}

{UIHelper.COLORS['CYAN']}┌─────────────────┐{UIHelper.COLORS['END']}    {UIHelper.COLORS['BLUE']}┌─────────────────┐{UIHelper.COLORS['END']}    {UIHelper.COLORS['GREEN']}┌─────────────────┐{UIHelper.COLORS['END']}
{UIHelper.COLORS['CYAN']}│  终端输入源      │{UIHelper.COLORS['END']} ──▶ {UIHelper.COLORS['BLUE']}│  问题处理器      │{UIHelper.COLORS['END']} ──▶ {UIHelper.COLORS['GREEN']}│  QA提示器       │{UIHelper.COLORS['END']}
{UIHelper.COLORS['CYAN']}│ TerminalInput   │{UIHelper.COLORS['END']}    {UIHelper.COLORS['BLUE']}│ QuestionProc    │{UIHelper.COLORS['END']}    {UIHelper.COLORS['GREEN']}│ QAPromptor      │{UIHelper.COLORS['END']}
{UIHelper.COLORS['CYAN']}└─────────────────┘{UIHelper.COLORS['END']}    {UIHelper.COLORS['BLUE']}└─────────────────┘{UIHelper.COLORS['END']}    {UIHelper.COLORS['GREEN']}└─────────────────┘{UIHelper.COLORS['END']}
           │                           │                           │
           ▼                           ▼                           ▼
    {UIHelper.COLORS['CYAN']}📝 用户键盘输入{UIHelper.COLORS['END']}          {UIHelper.COLORS['BLUE']}🔧 清理和验证{UIHelper.COLORS['END']}           {UIHelper.COLORS['GREEN']}📋 构造提示词{UIHelper.COLORS['END']}

{UIHelper.COLORS['RED']}┌─────────────────┐{UIHelper.COLORS['END']}    {UIHelper.COLORS['HEADER']}┌─────────────────┐{UIHelper.COLORS['END']}    {UIHelper.COLORS['YELLOW']}┌─────────────────┐{UIHelper.COLORS['END']}
{UIHelper.COLORS['RED']}│  控制台输出      │{UIHelper.COLORS['END']} ◀── {UIHelper.COLORS['HEADER']}│  回答格式化      │{UIHelper.COLORS['END']} ◀── {UIHelper.COLORS['YELLOW']}│  AI生成器       │{UIHelper.COLORS['END']}
{UIHelper.COLORS['RED']}│ ConsoleSink     │{UIHelper.COLORS['END']}    {UIHelper.COLORS['HEADER']}│ AnswerFormat    │{UIHelper.COLORS['END']}    {UIHelper.COLORS['YELLOW']}│ OpenAIGenerator │{UIHelper.COLORS['END']}
{UIHelper.COLORS['RED']}└─────────────────┘{UIHelper.COLORS['END']}    {UIHelper.COLORS['HEADER']}└─────────────────┘{UIHelper.COLORS['END']}    {UIHelper.COLORS['YELLOW']}└─────────────────┘{UIHelper.COLORS['END']}
           │                           │                           │
           ▼                           ▼                           ▼
    {UIHelper.COLORS['RED']}🖥️  终端显示回答{UIHelper.COLORS['END']}       {UIHelper.COLORS['HEADER']}📝 美化输出格式{UIHelper.COLORS['END']}        {UIHelper.COLORS['YELLOW']}🧠 AI模型推理{UIHelper.COLORS['END']}
"""
        print(diagram)
    
    @staticmethod 
    def print_config_info(config):
        """打印配置信息"""
        model_info = config["generator"]["remote"]
        info = f"""
{UIHelper.COLORS['GREEN']}{UIHelper.COLORS['BOLD']}⚙️  系统配置信息:{UIHelper.COLORS['END']}
  🤖 AI模型: {UIHelper.COLORS['YELLOW']}{model_info.get('model_name', 'Unknown')}{UIHelper.COLORS['END']}
  🌐 API端点: {UIHelper.COLORS['CYAN']}{model_info.get('base_url', 'Unknown')}{UIHelper.COLORS['END']}
  🎯 管道名称: {UIHelper.COLORS['BLUE']}{config['pipeline'].get('name', 'Unknown')}{UIHelper.COLORS['END']}
  📖 描述: {config['pipeline'].get('description', 'No description')}
"""
        print(info)
    
    @staticmethod
    def print_usage_tips():
        """打印使用提示"""
        tips = f"""
{UIHelper.COLORS['GREEN']}{UIHelper.COLORS['BOLD']}💡 使用提示:{UIHelper.COLORS['END']}
  • 输入任何问题后按 {UIHelper.COLORS['YELLOW']}Enter{UIHelper.COLORS['END']} 键提交
  • 按 {UIHelper.COLORS['RED']}Ctrl+C{UIHelper.COLORS['END']} 退出程序
  • 空输入将被忽略，请输入有效问题
  • 程序支持中英文问答
  
{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}🚀 系统就绪，等待您的问题...{UIHelper.COLORS['END']}
{UIHelper.COLORS['BLUE']}{'='*60}{UIHelper.COLORS['END']}
"""
        print(tips)
    
    @staticmethod
    def format_input_prompt():
        """格式化输入提示符"""
        return f"{UIHelper.COLORS['BOLD']}{UIHelper.COLORS['CYAN']}❓ 请输入您的问题: {UIHelper.COLORS['END']}"
    
    @staticmethod  
    def format_thinking():
        """显示思考状态"""
        return f"{UIHelper.COLORS['YELLOW']}🤔 AI正在思考中...{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_error(error_msg):
        """格式化错误信息"""
        return f"{UIHelper.COLORS['RED']}{UIHelper.COLORS['BOLD']}❌ 错误: {error_msg}{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_success(msg):
        """格式化成功信息"""
        return f"{UIHelper.COLORS['GREEN']}{UIHelper.COLORS['BOLD']}✅ {msg}{UIHelper.COLORS['END']}"


# ========== 核心算子实现 ==========
class TerminalInputSource(SourceFunction):
    """终端输入源函数 - 美化版"""
    def execute(self, data=None):
        try:
            # 显示美化的输入提示符
            user_input = input(UIHelper.format_input_prompt()).strip()
            if user_input:
                # 显示处理状态
                print(UIHelper.format_thinking())
                return user_input
            return self.execute(data)
        except (EOFError, KeyboardInterrupt):
            print(f"\n{UIHelper.format_success('感谢使用，再见！')}")
            sys.exit(0)


class QuestionProcessor(MapFunction):
    """问题处理器"""
    def execute(self, data):
        if not data or data.strip() == "":
            return None

        question = data.strip()
        return question


class AnswerFormatter(MapFunction):
    """回答格式化器 - 美化版"""
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
    """控制台输出 - 美化版"""
    def execute(self, data):
        if not data:
            return None

        if isinstance(data, dict):
            question = data.get('question', 'N/A')
            answer = data.get('answer', 'N/A')
            timestamp = data.get('timestamp', '')
            
            # 美化输出格式
            output = f"""
{UIHelper.COLORS['BLUE']}{'='*60}{UIHelper.COLORS['END']}
{UIHelper.COLORS['BOLD']}{UIHelper.COLORS['GREEN']}🤖 AI助手回答:{UIHelper.COLORS['END']}

{UIHelper.COLORS['CYAN']}📝 问题: {UIHelper.COLORS['END']}{question}

{UIHelper.COLORS['YELLOW']}💡 回答: {UIHelper.COLORS['END']}
{answer}

{UIHelper.COLORS['HEADER']}⏰ 时间: {timestamp}{UIHelper.COLORS['END']}
{UIHelper.COLORS['BLUE']}{'='*60}{UIHelper.COLORS['END']}
"""
            print(output)
        else:
            print(f"\n{UIHelper.COLORS['GREEN']}🤖 {data}{UIHelper.COLORS['END']}\n")

        return data


def create_qa_pipeline():
    """创建QA处理管道"""
    # 加载配置
    load_dotenv(override=False)
    config = load_config("config_source.yaml")

    # 显示美化的启动界面
    UIHelper.print_header()
    UIHelper.print_pipeline_diagram()
    UIHelper.print_config_info(config)
    UIHelper.print_usage_tips()

    # 创建本地环境
    env = LocalEnvironment()

    try:
        # 构建无界流处理管道
        (env
            .from_source(TerminalInputSource)
            .map(QuestionProcessor)
            .map(QAPromptor, config["promptor"])
            .map(OpenAIGenerator, config["generator"]["remote"])
            .map(AnswerFormatter)
            .sink(ConsoleSink)
        )

        # 提交并运行
        env.submit()
        
        # 保持主线程运行，直到用户退出
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n{UIHelper.format_success('用户主动退出程序')}")
    except Exception as e:
        print(UIHelper.format_error(f"管道运行出错: {str(e)}"))
    finally:
        try:
            env.close()
            print(UIHelper.format_success("QA流处理管道已关闭"))
        except:
            pass


if __name__ == "__main__":
    CustomLogger.disable_global_console_debug()
    create_qa_pipeline()