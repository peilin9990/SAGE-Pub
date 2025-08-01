#!/usr/bin/env python3
"""
SAGE 示例系统统一测试运行器
"""
import sys
import os
import subprocess
from typing import List, Tuple

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def run_test(test_file: str) -> Tuple[bool, str]:
    """
    运行单个测试文件
    
    Args:
        test_file: 测试文件路径
        
    Returns:
        (是否成功, 输出信息)
    """
    try:
        result = subprocess.run(
            [sys.executable, test_file], 
            capture_output=True, 
            text=True,
            cwd=os.path.dirname(test_file)
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def main():
    """主测试函数"""
    print("🧪 SAGE 示例系统统一测试")
    print("=" * 60)
    
    # 测试文件列表
    test_files = [
        "test_simple_qa.py",
        "test_batch_rag.py", 
        "test_interactive_rag.py",
        "test_custom_knowledge.py"
    ]
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    passed = 0
    failed = 0
    
    for test_file in test_files:
        test_path = os.path.join(current_dir, test_file)
        if not os.path.exists(test_path):
            print(f"⚠️  测试文件不存在: {test_file}")
            failed += 1
            continue
        
        print(f"\n🔍 运行测试: {test_file}")
        print("-" * 40)
        
        success, output = run_test(test_path)
        
        if success:
            print(f"✅ {test_file} 测试通过")
            passed += 1
        else:
            print(f"❌ {test_file} 测试失败")
            print("错误输出:")
            print(output)
            failed += 1
    
    # 测试总结
    print("\n" + "=" * 60)
    print("📊 测试总结:")
    print(f"   ✅ 通过: {passed}")
    print(f"   ❌ 失败: {failed}")
    print(f"   📈 成功率: {passed/(passed+failed)*100:.1f}%" if (passed+failed) > 0 else "   📈 成功率: 0%")
    
    if failed == 0:
        print("\n🎉 所有测试都通过了！")
        return 0
    else:
        print(f"\n💥 有 {failed} 个测试失败")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
