# SAGE 安装指南

本文档将指导您如何安装 SAGE 及其相关依赖。请根据您的需求选择合适的安装方式。

---

## 📋 前置要求 (Prerequisites)

在开始安装之前，请确保您的开发环境满足以下要求：

* **支持的操作系统 (OS)**:
    * Linux
    * macOS(docker ubuntu 22.04+)
    * Windows(WSL ubuntu 22.04+)
* **Python**：建议使用版本 **≥ 3.11.10** 的 Python 解释器。例如使用 Conda 在虚拟环境中创建并激活环境：

```bash
conda create -n sage python=3.11.10
conda activate sage
```

*温馨提示：若 Conda 创建失败，可能是网络问题导致，请及时更换 Conda 源。*

---

## 🚀 下载安装 (Installation)

SAGE 提供简单的安装方式，您只需通过 `.whl` 文件即可完成安装，无需下载源码，适合快速部署和使用。

### 安装步骤

**第 1 步：下载 Wheel 文件**

前往 SAGE 的官方发布仓库下载最新的 `.whl` 安装包，在当前版本中，该安装包名称如下：`sage-0.1.2-cp311-cp311-linux_x86_64.whl`：

- 下载地址：[https://github.com/IntelliStream/SAGE-Pub](https://github.com/IntelliStream/SAGE-Pub)


**第 2 步：使用 pip 安装**

在终端中切换到 `.whl` 文件所在目录，执行以下命令完成安装：

```bash
# 安装前请确保您处在正确的目录以及Python环境下
# (sage) user-name:~/download_path/SAGE-Pub$
pip install sage-0.1.2-cp311-cp311-linux_x86_64.whl
```


## ✅ 验证安装 (Verify Installation)
安装完成后，您可以通过以下任一方式来验证 SAGE 是否已成功安装。

### 方法1：查看包信息

运行 `pip show` 以检查 SAGE 的安装情况。

```Bash
pip show sage
```

您将会看到以下的类似输出：

```
Name: sage
Version: 0.1.0
Summary: 
Home-page: [https://github.com/IntelliStream/SAGE](https://github.com/IntelliStream/SAGE)
Author: IntelliStream
Author-email: intellistream@outlook.com
License: 
Location: /path/to/your/python/site-packages
Requires: accelerate, aioboto3, ...
Required-by: 
```
### 方法2：运行 SAGE HelloWorld 程序

执行 SAGE 官方发布仓库下 `hello_world.py` Python 文件。

```Python
python hello_world.py
```

您将会看到一系列的终端输出，表明您顺利完成 SAGE 的安装。

```
Waiting for batch processing to complete...
HELLO, WORLD! #1
HELLO, WORLD! #2
HELLO, WORLD! #3
HELLO, WORLD! #4
HELLO, WORLD! #5
HELLO, WORLD! #6
HELLO, WORLD! #7
HELLO, WORLD! #8
HELLO, WORLD! #9
HELLO, WORLD! #10
Hello World 批处理示例结束
```

至此，您已成功安装 SAGE，祝您使用愉快！
