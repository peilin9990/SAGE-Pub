"""
Common configuration and utilities for SAGE examples
提供通用的配置加载和环境设置
"""
import time
from typing import Dict, Any
from dotenv import load_dotenv
from sage.utils.config_loader import load_config
from sage.utils.custom_logger import CustomLogger
from sage.core.api.local_environment import LocalEnvironment


class ExampleConfig:
    """示例配置管理器"""
    
    @staticmethod
    def load_and_setup(config_file: str = "config_batch.yaml") -> Dict[str, Any]:
        """
        加载配置并设置环境
        
        Args:
            config_file: 配置文件名
            
        Returns:
            配置字典
        """
        # 设置日志和环境变量
        CustomLogger.disable_global_console_debug()
        load_dotenv(override=False)
        
        # 加载配置
        config = load_config(config_file)
        return config
    
    @staticmethod
    def create_environment() -> LocalEnvironment:
        """创建本地环境"""
        return LocalEnvironment()


class PipelineRunner:
    """管道运行器基类"""
    
    def __init__(self, config_file: str = "config_batch.yaml"):
        self.config = ExampleConfig.load_and_setup(config_file)
        self.env = ExampleConfig.create_environment()
    
    def register_services(self):
        """注册服务 - 子类可重写"""
        pass
    
    def build_pipeline(self):
        """构建管道 - 子类必须实现"""
        raise NotImplementedError("Subclasses must implement build_pipeline")
    
    def run(self):
        """运行管道"""
        try:
            self.register_services()
            self.build_pipeline()
            
            print("🚀 开始处理...")
            self.env.submit()
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("⚠️  处理中断")
        except Exception as e:
            print(f"❌ 运行错误: {e}")
        finally:
            print("🏁 处理结束")
            self.env.close()
