# SAGE-Pub

本仓库用于发布和维护 [SAGE](https://github.com/intellistream/SAGE) 系统的对外文档。

SAGE 是一个模块化、高性能的推理框架，支持向量增强、流数据、神经记忆与复杂数据处理。

---

## � 快速体验

体验 SAGE 系统的各种 QA 功能：

```bash
# 激活环境
conda activate tsage  # 或你的SAGE环境

# 运行示例工厂
python example_factory.py
```

选择要体验的系统类型：
1. 简单QA系统（无记忆）
2. 批量RAG系统（私密信息）  
3. 交互式RAG系统
4. 自定义知识库（科技公司）

---

## �📘 文档入口

👉 [在线文档地址](https://intellistream.github.io/SAGE-Pub/)

---

## 🧠 包含内容

- 快速开始（安装、运行示例）
- 架构图与核心模块说明
- Dashboard 使用指南
- 系统 API 文档（公开部分）
- 研究论文与引用方式

---

## 🧾 引用 SAGE

如果你在学术工作中使用了 SAGE，请引用：

```
To be updated ...
```


---

## 🔒 关于源码访问

本项目文档为开源，SAGE 源码为私有。若需合作或访问，请联系项目负责人。

---

## 🛠️ 构建与贡献

```bash
# 安装
pip install mkdocs mkdocs-material

# 本地预览
mkdocs serve

# 部署（已配置自动部署）
mkdocs gh-deploy

## 🎯 它应该做的事

| Section        | 功能                           |
|----------------|--------------------------------|
| 项目介绍       | 定位一句话，不谈实现细节          |
| 文档入口       | 明确指出用户该去哪               |
| 包含内容       | 给出目录概览                     |
| 引用方式       | 支持学术引用                     |
| 源码访问声明   | 避免用户误以为这里有源码           |
| 本地构建说明   | 面向开发/维护者的构建指南          |