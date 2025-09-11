


packages/sage/src/sage
packages/sage-common/src/sage
packages/sage-libs/src/sage
packages/sage-kernel/src/sage
packages/sage-middleware/src/sage
以上目录下的__init__.py文件，可以语言服务器检查到sage下的各个组件，有了这个可以让语言服务器进行补全提示。

```Python
# 扩展命名空间包路径以支持子包
__path__ = __import__('pkgutil').extend_path(__path__, __name__)
```



`packages/sage/src/sage/_version.py` 该文件被 `packages/sage/pyproject.toml` 导入，具体语句如下：
``` Python
version = {attr = "sage._version.__version__"}
```
主要作用是：
* 动态版本获取：根据环境（开发/构建）智能选择版本来源
* 统一版本控制：确保所有 SAGE 子包使用一致的版本号
* 安装时版本提供：为 pip install 提供版本信息


