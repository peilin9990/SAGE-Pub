"""
终端交互式QA无界流处理 - 重构版
支持终端输入问题，使用大模型生成回答的无界流处理
使用模块化组件实现
"""
import time
from sage.lib.rag.promptor import QAPromptor
from ..operators.openai_generator import OpenAIGenerator

from ..utils.ui_helper import UIHelper
from ..utils.base_operators import TerminalInputSource, QuestionProcessor, AnswerFormatter, ConsoleSink
from ..utils.common import PipelineRunner


class InteractiveQAPipelineRunner(PipelineRunner):
    """交互式QA管道运行器"""
    
    def __init__(self):
        super().__init__("config_source.yaml")
    
    def build_pipeline(self):
        """构建交互式QA处理管道"""
        # 显示美化的启动界面
        UIHelper.print_sage_header("🤖 SAGE QA助手 v1.0", "智能问答无界流处理系统")
        
        # 管道组件描述
        components = [
            ("TerminalInput", "📝 用户键盘输入"),
            ("QuestionProc", "🔧 清理和验证"),
            ("QAPromptor", "📋 构造提示词"),
            ("OpenAIGenerator", "🧠 AI模型推理"),
            ("AnswerFormat", "📝 美化输出格式"),
            ("ConsoleSink", "🖥️  终端显示回答")
        ]
        UIHelper.print_pipeline_diagram(components)
        UIHelper.print_config_info(self.config)
        
        # 使用提示
        tips = [
            f"输入任何问题后按 {UIHelper.COLORS['YELLOW']}Enter{UIHelper.COLORS['END']} 键提交",
            f"按 {UIHelper.COLORS['RED']}Ctrl+C{UIHelper.COLORS['END']} 退出程序",
            "空输入将被忽略，请输入有效问题",
            "程序支持中英文问答"
        ]
        UIHelper.print_usage_tips(tips)
        
        print(f"{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}🚀 系统就绪，等待您的问题...{UIHelper.COLORS['END']}")
        UIHelper.print_separator()

        # 构建无界流处理管道
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


def main():
    """主函数"""
    runner = InteractiveQAPipelineRunner()
    runner.run()


if __name__ == "__main__":
    main()
