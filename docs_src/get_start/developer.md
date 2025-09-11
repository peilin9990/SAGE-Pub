# SAGE 安装指南

本文档将指导您如何以 **开发者模式** 安装 SAGE 源码及其相关依赖。

---

## *A*. 前置要求 (Prerequisites)

在开始安装之前，请确保您的开发环境满足以下要求：

* **操作系统 (OS)**：[Ubuntu 22.04及以上版本](https://ubuntu.com/)
* **基础依赖**：[Anaconda/Miniconda](https://www.anaconda.com/)
* **SAGE官方仓库**：[IntelliStreamSAGE](https://github.com/intellistream/SAGE)
<!-- 仓库链接待修改 -->
<small>您也可以通过以下命令快速拉取 SAGE 官方仓库</small>

<!-- 仓库链接待修改 -->
```bash
git clone git@github.com:intellistream/SAGE.git
```

---

## *B*. 本地安装 (Installation)

**第 1 步：运行安装脚本**

在本地的 SAGE 目录下，可见一个quickstart.sh的脚本，提前 **拉长终端边框** ，运行该脚本一键式安装 SAGE：

```bash
./quickstart.sh
```

运行该脚本后，您的终端会显示以下输出：

[![启动快速安装脚本](../assets/img/quickstart_intro.png  "启动快速安装脚本")](../assets/img/quickstart_intro.png)


**第 2 步：选择环境名称**

在终端中，输入 ++3+enter++, 以指定创建 SAGE 环境的名称： 

指定您希望创建的 SAGE 环境名称并 ++enter++ ，等待安装程序开始安装。
[![交互式安装](../assets/img/quickstart_install_1.png "交互式安装")](../assets/img/quickstart_install_1.png)

静待片刻后，显示以下页面，完成 SAGE 环境部署：

[![成功安装](../assets/img/quickstart_install_2.png "成功安装")](../assets/img/quickstart_install_2.png)

---

## *C*. 验证安装 (Verify Installation)

执行 SAGE 目录下的 [`hello_world.py`](https://github.com/intellistream/SAGE/blob/main/examples/tutorials/hello_world.py) 文件：

```bash
python examples/tutorials/hello_world.py
```

出现如下输出，说明 SAGE 安装成功，祝您使用愉快~

[![安装验证](../assets/img/quickstart_install_3.png "安装验证")](../assets/img/quickstart_install_3.png)

---

## *D*. 常见问题 (Common Question)

:octicons-info-16: **SAGE-Pub Failed to connect / 子模块设置失败**

报错内容大致如下：

```bash title="bash error"
fatal:unable to access'https://github.com/intellistream/SAGE-Pub.git/': Failed to connect_to github.com_port 443 after 118564 ms: Could not connect to server
```

这一般是因为网络原因导致无法与 github 建立连接，建议科学上网并切换到虚拟网卡模式重试。

## *E*. 安装演示 （Installation Demo）

<iframe 
  src="https://player.bilibili.com/player.html?bvid=BV1uKYNz8EEm" 
  scrolling="no" 
  border="0" 
  frameborder="no" 
  framespacing="0" 
  allowfullscreen="true" 
  style="width: 800px; height: 500px;">
</iframe>
