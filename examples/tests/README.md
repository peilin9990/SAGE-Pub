# SAGE 示例系统测试

本目录包含 SAGE 示例系统的所有测试文件。

## 测试文件说明

- `test_simple_qa.py` - 测试简单QA系统（无记忆）
- `test_batch_rag.py` - 测试批量RAG系统
- `test_interactive_rag.py` - 测试交互式RAG系统  
- `test_custom_knowledge.py` - 测试自定义知识库系统
- `run_all_tests.py` - 统一测试运行器

## 运行测试

### 运行单个测试

```bash
cd examples/tests
python test_simple_qa.py
```

### 运行所有测试

```bash
cd examples/tests
python run_all_tests.py
```

### 从项目根目录运行

```bash
# 运行单个测试
python examples/tests/test_simple_qa.py

# 运行所有测试  
python examples/tests/run_all_tests.py
```

## 测试说明

- 所有测试默认只测试系统创建和配置加载，不会实际运行完整的管道
- 如果需要测试完整功能，可以取消注释测试文件中的 `runner.run()` 行
- 测试需要有效的 SAGE 环境和配置文件

## 添加新测试

1. 在此目录下创建新的测试文件，遵循 `test_*.py` 的命名规范
2. 在测试文件中添加适当的路径设置
3. 在 `run_all_tests.py` 中添加新的测试文件名

## 注意事项

- 确保在 tsage conda 环境中运行测试
- 测试文件会自动添加项目根目录到 Python 路径
- 所有测试都包含基本的错误处理和断言
