#!/usr/bin/env python3
"""
测试交互式RAG系统的脚本
"""
import sys
import os

# 添加项目根目录到路径 - 从examples/tests/回到根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from example_factory import ExampleFactory

def test_interactive_rag():
    """测试交互式RAG系统"""
    print("🧪 开始测试交互式RAG系统...")
    
    try:
        runner = ExampleFactory.create_interactive_rag()
        print("✅ 交互式RAG系统创建成功")
        
        # 测试配置加载
        assert runner.config is not None, "配置加载失败"
        print("✅ 配置加载成功")
        
        # 测试环境创建
        assert runner.env is not None, "环境创建失败"
        print("✅ 环境创建成功")
        
        print("✅ 测试通过，准备运行...")
        
        # 如果需要实际运行，取消下面这行的注释
        # runner.run()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_interactive_rag()
    if success:
        print("🎉 交互式RAG系统测试通过！")
    else:
        print("💥 测试失败")
        sys.exit(1)
