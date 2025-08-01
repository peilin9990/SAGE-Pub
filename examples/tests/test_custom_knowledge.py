#!/usr/bin/env python3
"""
测试自定义知识库系统的脚本
"""
import sys
import os

# 添加项目根目录到路径 - 从examples/tests/回到根目录
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from example_factory import ExampleFactory, demo_custom_knowledge

def test_custom_knowledge():
    """测试自定义知识库系统"""
    print("🧪 开始测试自定义知识库系统...")
    
    try:
        # 测试数据
        test_knowledge = [
            "测试知识1：Python是一种编程语言。",
            "测试知识2：机器学习是人工智能的一个分支。",
            "测试知识3：SAGE是一个流处理框架。"
        ]
        
        test_questions = [
            "Python是什么？",
            "什么是机器学习？",
            "SAGE是什么？"
        ]
        
        # 测试创建自定义知识库
        runner = ExampleFactory.create_batch_qa_with_custom_knowledge(
            knowledge_list=test_knowledge,
            questions_list=test_questions,
            collection_name="test_knowledge"
        )
        print("✅ 自定义知识库系统创建成功")
        
        # 测试配置加载
        assert runner.config is not None, "配置加载失败"
        print("✅ 配置加载成功")
        
        # 测试环境创建
        assert runner.env is not None, "环境创建失败"
        print("✅ 环境创建成功")
        
        # 测试参数验证
        try:
            ExampleFactory.create_batch_qa_with_custom_knowledge([], test_questions)
            assert False, "应该抛出ValueError"
        except ValueError:
            print("✅ 空知识列表验证通过")
        
        try:
            ExampleFactory.create_batch_qa_with_custom_knowledge(test_knowledge, [])
            assert False, "应该抛出ValueError"
        except ValueError:
            print("✅ 空问题列表验证通过")
        
        print("✅ 测试通过，准备运行...")
        
        # 如果需要实际运行，取消下面这行的注释
        # runner.run()
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_custom_knowledge()
    if success:
        print("🎉 自定义知识库系统测试通过！")
    else:
        print("💥 测试失败")
        sys.exit(1)
