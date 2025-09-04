# SAGE Kernel 核心框架

SAGE Kernel 是 SAGE 框架的核心引擎，提供了强大的流数据处理和分布式计算能力。它是整个 SAGE 生态系统的基石，为上层的中间件服务和应用组件提供了统一的运行时环境。

## 🏗️ 架构概览

SAGE Kernel 采用分层架构设计：

- **执行环境层**: 提供本地和远程执行环境
- **数据流层**: 核心的流处理API和算子
- **函数层**: 用户自定义处理逻辑的接口
- **配置层**: 系统配置和参数管理

## 📚 核心组件文档

### DataStream API
流数据处理的核心API，提供丰富的数据转换和处理操作：

<!-- - [DataStream 概览](datastream/datastream_intro.md) - 基础概念和编程模式 -->
- DataStream 概览 - 基础概念和编程模式
<!-- - [Operator 与 Function](datastream/datastream_function.md) - 算子和函数的设计原理 -->
- Operator 与 Function - 算子和函数的设计原理
<!-- - [Transformation](datastream/datastream_trans.md) - 数据转换操作详解 -->
- Transformation - 数据转换操作详解

### 执行环境 API
管理任务执行的环境和资源：

- [Environments API](api/environments.md) - 本地和远程执行环境
- [DataStreams API](api/datastreams.md) - 数据流处理和管道
- [Functions API](api/functions.md) - 自定义函数开发
- [Connected Streams API](api/connected-streams.md) - 多流处理和复杂事件处理

### 系统配置和工具
- [Config 配置](config/config.md) - 系统配置参数详解
- [CLI Reference](components/cli.md) - 命令行工具使用指南

## 📖 深入学习

### 核心概念
- [Architecture Overview](architecture.md) - 系统架构设计
- [Core Concepts](concepts.md) - 核心概念和术语

### 开发指南
- [Quick Start Guide](guides/quickstart.md) - 快速入门教程
- [Best Practices](best-practices.md) - 开发最佳实践
- [FAQ](faq.md) - 常见问题解答

### 示例代码
- [Examples Collection](examples/README.md) - 实用示例集合

## 🔗 与其他组件的关系

### Middleware 层
SAGE Kernel 为 [中间件服务](../middleware/service/service_intro.md) 提供运行时支持

### Application 层
上层应用组件基于 Kernel 构建：
<!-- - [RAG 应用](../applications/rag.md) -->
- RAG 应用
<!-- - [智能代理](../applications/agents.md) -->
- 智能代理
<!-- - [工具集成](../applications/tools_intro.md) -->
- 工具集成

## 🚀 快速开始

```python
from sage.core.api.local_environment import LocalEnvironment

# 创建本地环境
env = LocalEnvironment("my_app")

# 创建数据流管道
stream = env.from_batch([1, 2, 3, 4, 5])
result = stream.map(lambda x: x * 2).sink(print)

# 提交执行
env.submit()
```

## 📋 主要特性

- **🔄 流式处理**: 支持无限数据流的实时处理
- **🌐 分布式**: 原生支持集群部署和分布式计算
- **🎯 类型安全**: 基于Python泛型的编译时类型检查
- **🔌 可扩展**: 插件化架构，支持自定义算子和服务
- **🛠️ 工具完善**: 完整的CLI工具链和监控体系
- **🏢 企业级**: 提供商业版高级功能

## 📞 获取帮助

- [GitHub Issues](https://github.com/intellistream/SAGE/issues) - 报告问题
- [讨论区](https://github.com/intellistream/SAGE/discussions) - 社区讨论
- [官方文档](https://intellistream.github.io/SAGE-Pub/) - 完整文档

## 📄 许可证

MIT License - 详见 LICENSE 文件
