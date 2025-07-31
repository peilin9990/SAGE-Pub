"""
Terminal UI Helper for SAGE examples
提供统一的终端界面美化工具
"""
import time


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
    def print_sage_header(title: str, subtitle: str = ""):
        """打印SAGE程序头部信息"""
        header = f"""
{UIHelper.COLORS['HEADER']}{UIHelper.COLORS['BOLD']}
╔══════════════════════════════════════════════════════════════╗
║                   {title:^40}                   ║  
║              {subtitle:^40}              ║
╚══════════════════════════════════════════════════════════════╝
{UIHelper.COLORS['END']}"""
        print(header)
    
    @staticmethod
    def print_pipeline_diagram(components: list):
        """
        打印管道流程图
        components: [(name, description), ...]
        """
        print(f"{UIHelper.COLORS['YELLOW']}{UIHelper.COLORS['BOLD']}📊 数据流管道架构:{UIHelper.COLORS['END']}")
        print()
        
        # 打印组件箱子
        colors = [UIHelper.COLORS['CYAN'], UIHelper.COLORS['BLUE'], 
                 UIHelper.COLORS['GREEN'], UIHelper.COLORS['YELLOW'], 
                 UIHelper.COLORS['RED'], UIHelper.COLORS['HEADER']]
        
        boxes = []
        descriptions = []
        
        for i, (name, desc) in enumerate(components):
            color = colors[i % len(colors)]
            box = f"{color}┌─────────────────┐{UIHelper.COLORS['END']}"
            content = f"{color}│{name:^17}│{UIHelper.COLORS['END']}"
            bottom = f"{color}└─────────────────┘{UIHelper.COLORS['END']}"
            
            boxes.append((box, content, bottom))
            descriptions.append(f"{color}{desc}{UIHelper.COLORS['END']}")
        
        # 打印顶部
        line = "    ".join([box[0] for box in boxes])
        print(line)
        
        # 打印内容
        line = " ──▶ ".join([box[1] for box in boxes])
        print(line)
        
        # 打印底部
        line = "    ".join([box[2] for box in boxes])
        print(line)
        
        # 打印描述
        print("           │" + "                           │" * (len(components) - 1))
        print("           ▼" + "                           ▼" * (len(components) - 1))
        desc_line = "        ".join(descriptions)
        print(f"    {desc_line}")
        print()
    
    @staticmethod 
    def print_config_info(config: dict):
        """打印配置信息"""
        model_info = config.get("generator", {}).get("remote", {})
        pipeline_info = config.get("pipeline", {})
        
        info = f"""
{UIHelper.COLORS['GREEN']}{UIHelper.COLORS['BOLD']}⚙️  系统配置信息:{UIHelper.COLORS['END']}
  🤖 AI模型: {UIHelper.COLORS['YELLOW']}{model_info.get('model_name', 'Unknown')}{UIHelper.COLORS['END']}
  🌐 API端点: {UIHelper.COLORS['CYAN']}{model_info.get('base_url', 'Unknown')}{UIHelper.COLORS['END']}
  🎯 管道名称: {UIHelper.COLORS['BLUE']}{pipeline_info.get('name', 'Unknown')}{UIHelper.COLORS['END']}
  📖 描述: {pipeline_info.get('description', 'No description')}
"""
        print(info)
    
    @staticmethod
    def print_knowledge_base_info(sentences_count: int, collection_name: str = "knowledge"):
        """打印知识库信息"""
        info = f"""
{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}📚 知识库信息:{UIHelper.COLORS['END']}
  📄 知识条目数: {UIHelper.COLORS['YELLOW']}{sentences_count}{UIHelper.COLORS['END']} 条
  🏷️  集合名称: {UIHelper.COLORS['GREEN']}{collection_name}{UIHelper.COLORS['END']}
  🔍 检索方式: {UIHelper.COLORS['BLUE']}向量相似度 + 关键词匹配{UIHelper.COLORS['END']}
  💾 存储后端: {UIHelper.COLORS['HEADER']}VectorDB{UIHelper.COLORS['END']}
"""
        print(info)
    
    @staticmethod
    def print_test_questions(questions: list):
        """打印测试问题列表"""
        info = f"""
{UIHelper.COLORS['YELLOW']}{UIHelper.COLORS['BOLD']}❓ 预设测试问题:{UIHelper.COLORS['END']}"""
        print(info)
        for i, question in enumerate(questions, 1):
            print(f"  {UIHelper.COLORS['CYAN']}{i}.{UIHelper.COLORS['END']} {question}")
        print()
    
    @staticmethod
    def print_usage_tips(tips: list):
        """打印使用提示"""
        print(f"{UIHelper.COLORS['GREEN']}{UIHelper.COLORS['BOLD']}💡 使用提示:{UIHelper.COLORS['END']}")
        for tip in tips:
            print(f"  • {tip}")
        print()
    
    @staticmethod
    def format_input_prompt():
        """格式化输入提示符 - 同步版本"""
        prompt = f"{UIHelper.COLORS['BOLD']}{UIHelper.COLORS['CYAN']}❓ 请输入您的问题: {UIHelper.COLORS['END']}"
        return prompt
    
    @staticmethod
    def format_success(msg: str):
        """格式化成功信息"""
        return f"{UIHelper.COLORS['GREEN']}{UIHelper.COLORS['BOLD']}✅ {msg}{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_error(msg: str):
        """格式化错误信息"""
        return f"{UIHelper.COLORS['RED']}{UIHelper.COLORS['BOLD']}❌ {msg}{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_warning(msg: str):
        """格式化警告信息"""
        return f"{UIHelper.COLORS['YELLOW']}{UIHelper.COLORS['BOLD']}⚠️  {msg}{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_info(msg: str):
        """格式化信息"""
        return f"{UIHelper.COLORS['BLUE']}{UIHelper.COLORS['BOLD']}ℹ️  {msg}{UIHelper.COLORS['END']}"
    
    @staticmethod
    def format_processing(msg: str):
        """格式化处理信息"""
        return f"{UIHelper.COLORS['CYAN']}{UIHelper.COLORS['BOLD']}🔄 {msg}{UIHelper.COLORS['END']}"
    
    @staticmethod  
    def format_thinking():
        """显示思考状态"""
        return f"{UIHelper.COLORS['YELLOW']}🤔 AI正在思考中...{UIHelper.COLORS['END']}"
    
    @staticmethod
    def print_separator(char="=", length=60):
        """打印分隔符"""
        print(f"{UIHelper.COLORS['BLUE']}{char * length}{UIHelper.COLORS['END']}")
    
    @staticmethod
    def format_answer_output(question: str, answer: str, timestamp: str = None):
        """格式化QA输出"""
        if timestamp is None:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            
        return f"""
{UIHelper.COLORS['BLUE']}{'='*60}{UIHelper.COLORS['END']}
{UIHelper.COLORS['BOLD']}{UIHelper.COLORS['GREEN']}🤖 AI助手回答:{UIHelper.COLORS['END']}

{UIHelper.COLORS['CYAN']}📝 问题: {UIHelper.COLORS['END']}{question}

{UIHelper.COLORS['YELLOW']}💡 回答: {UIHelper.COLORS['END']}
{answer}

{UIHelper.COLORS['HEADER']}⏰ 时间: {timestamp}{UIHelper.COLORS['END']}
{UIHelper.COLORS['BLUE']}{'='*60}{UIHelper.COLORS['END']}
"""
