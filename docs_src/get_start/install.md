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

SAGE 提供简单的安装方式，您只需通过 `pip install isage` 命令，即可完成安装，无需下载源码，适合快速部署和使用。

### 安装步骤


**第 1 步：使用 pip 安装**

执行以下命令完成安装：

```bash
# 安装前请确保您处在正确的Python环境下
pip install isage
```

## ✅ 验证安装 (Verify Installation)
安装完成后，您可以通过以下任一方式来验证 SAGE 是否已成功安装。

### 方法1：查看包信息

运行 `pip show` 以检查 SAGE 的安装情况。

```Bash
pip show isage
```

您将会看到以下的类似输出：

```
Name: isage
Version: 0.1.2
Summary: SAGE (Meta Package)
Home-page: https://github.com/intellistream/SAGE
Author: 
Author-email: SAGE Team <sage@intellistream.com>
License: MIT
Location: /path/to/your/python/site-packages
Requires: isage-common, isage-kernel, isage-libs, isage-middleware
Required-by:
```
### 方法2：运行 SAGE HelloWorld 程序

执行 SAGE 官方发布仓库下(目前为私有库) `hello_world.py` Python 文件。

```Python
python hello_world.py
```

hello_world.py代码如下：
```Python
from sage.core.api.local_environment import LocalEnvironment
from sage.core.api.function.sink_function import SinkFunction
from sage.core.api.function.batch_function import BatchFunction
from sage.core.api.function.map_function import MapFunction
from sage.common.utils.logging.custom_logger import CustomLogger

# 批处理数据源：作用是生成10条"Hello, World!"字符串
class HelloBatch(BatchFunction):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.max_count = 10     # 生成10个数据包后返回None
    
    def execute(self):
        if self.counter >= self.max_count:
            return None         # 返回None表示批处理完成
        self.counter += 1
        return f"Hello, World! #{self.counter}"

# 简单的 MapFunction，将内容转大写
class UpperCaseMap(MapFunction):
    def execute(self, data):
        return data.upper()

# 简单 SinkFunction，直接打印结果
class PrintSink(SinkFunction):
    def execute(self, data):
        print(data)

def main():
    env = LocalEnvironment("Hello_World")
    
    # 批处理源 -> map -> sink
    env.from_batch(HelloBatch).map(UpperCaseMap).sink(PrintSink)

    env.submit(autostop=True)
    print("Hello World 批处理示例结束")

if __name__ == "__main__":
    # 关闭日志输出
    CustomLogger.disable_global_console_debug()
    main()
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

#❓pip install时可能遇到的问题以及解决方案
###问题1：Python版本过高，报错如下
```
Building wheels for collected packages: faiss-cpu, sgmllib3k
  Building wheel for faiss-cpu (pyproject.toml) ... error
  error: subprocess-exited-with-error

  × Building wheel for faiss-cpu (pyproject.toml) did not run successfully.
  │ exit code: 1
  ╰─> [138 lines of output]
      /tmp/pip-build-env-08i_jo3h/overlay/lib/python3.13/site-packages/setuptools/config/_apply_pyprojecttoml.py:82: SetuptoolsDeprecationWarning: `project.license` as a TOML table is deprecated
…
note: This error originates from a subprocess, and is likely not a problem with pip.
  ERROR: Failed building wheel for faiss-cpu
```
问题分析：Faiss官方包还没支持到Python 3.13，支持范围为3.7~3.12，因此推荐使用3.11。

###问题2：待补充
```


```
问题分析：