#!/usr/bin/env python3
"""
测试简单QA系统的脚本
"""
import sys
import os

# 添加项目根目录到路径 - 从examples/tests/回到根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from example_factory import ExampleFactory

def test_simple_qa():
    """测试简单QA系统"""
    print("🧪 开始测试简单QA系统...")
    
    try:
        runner = ExampleFactory.create_simple_qa()
        print("✅ 简单QA系统创建成功")
        
        # 不实际运行，只测试创建过程
        print("✅ 测试通过，准备运行...")
        
        # 如果需要实际运行，取消下面这行的注释
        # runner.run()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_simple_qa()
    if success:
        print("🎉 简单QA系统测试通过！")
    else:
        print("💥 测试失败")
        sys.exit(1)
