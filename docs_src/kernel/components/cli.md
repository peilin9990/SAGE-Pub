# CLI 命令行工具

SAGE 提供了完整的命令行工具集，支持系统部署、作业管理、集群管理和开发调试等全生命周期操作。

## 🔧 主要命令

### sage - 主入口命令

```bash
# 查看版本信息  
sage version show

# 查看帮助
sage --help

# 显示可用扩展信息
sage extensions

# 配置管理
sage config show
sage config init
```

### 核心管理命令

```bash
# 启动作业管理器
sage jobmanager start

# 启动工作节点
sage worker start

# 启动集群头节点
sage head start

# 集群管理
sage cluster start
sage cluster stop
sage cluster status
sage cluster scale
```

## 📊 作业管理

### 作业控制

```bash
# 列出所有作业
sage job list

# 查看作业状态
sage job status

# 查看作业详情
sage job show <job-id>

# 停止/暂停作业
sage job stop <job-id>

# 继续/恢复作业
sage job continue <job-id>

# 删除作业
sage job delete <job-id>

# 清理所有作业
sage job cleanup
```

### 作业监控

```bash
# 健康检查
sage job health

# 显示JobManager系统信息
sage job info

# 实时监控所有作业
sage job monitor

# 监控特定作业
sage job watch <job-id>
```

## 🚀 系统部署

### 系统控制

```bash
# 启动SAGE系统（Ray集群 + JobManager）
sage deploy start

# 停止SAGE系统
sage deploy stop

# 重启SAGE系统
sage deploy restart

# 显示系统状态
sage deploy status
```

### 集群管理

```bash
# 启动整个Ray集群
sage cluster start

# 停止整个Ray集群
sage cluster stop

# 重启整个Ray集群
sage cluster restart

# 检查集群状态
sage cluster status

# 部署SAGE到所有Worker节点
sage cluster deploy

# 动态扩缩容集群
sage cluster scale

# 显示集群配置信息
sage cluster info
```

### 节点管理

```bash
# Head节点管理
sage head start
sage head stop
sage head status
sage head restart
sage head logs

# 或者通过cluster子命令管理Head节点
sage cluster head start
sage cluster head stop
sage cluster head status

# Worker节点管理
sage worker start
sage worker stop
sage worker status
sage worker restart
sage worker add
sage worker remove
sage worker list
sage worker config
sage worker deploy

# 或者通过cluster子命令管理Worker节点
sage cluster worker start
sage cluster worker stop
sage cluster worker status
sage cluster worker add
sage cluster worker remove

# JobManager管理
sage jobmanager start
sage jobmanager stop
sage jobmanager restart
sage jobmanager status
sage jobmanager kill
```

## 🛠️ 开发工具 (sage-dev)

SAGE 提供了专门的开发工具 `sage-dev`，用于项目开发、测试和发布。

### 项目分析和管理

```bash
# 分析项目依赖
sage-dev dependencies

# 分析类依赖关系
sage-dev classes

# 检查导入依赖
sage-dev check-dependency <package-name>

# 清理构建产物
sage-dev artifacts

# 管理SAGE主目录和日志
sage-dev home
```

### 包管理和发布

```bash
# 发布开源包(保留源码)
sage-dev opensource

# 发布闭源包(编译为字节码)  
sage-dev proprietary

# 显示包信息
sage-dev info

# 生成开发报告
sage-dev generate

# 显示版本信息
sage-dev show
```

### 测试工具

```bash
# 运行测试
sage-dev test

# PyPI包管理
sage-dev pypi

# 包管理命令
sage-dev package
```

## 📈 监控和诊断

### 系统诊断

```bash
# 系统健康检查
sage doctor check

# 查看系统状态
sage deploy status
sage cluster status
sage jobmanager status
```

### Web界面

```bash
# 启动Web界面
sage web-ui start

# 查看Web界面状态
sage web-ui status

# 显示Web界面信息
sage web-ui info
```

### Studio可视化编辑器

```bash
# 启动Studio服务
sage studio start

# 停止Studio服务
sage studio stop

# 重启Studio服务
sage studio restart

# 查看Studio状态
sage studio status

# 查看Studio日志
sage studio logs

# 安装Studio依赖
sage studio install

# 显示Studio信息
sage studio info

# 在浏览器中打开Studio
sage studio open
```

## ⚙️ 配置管理

### 全局配置

```bash
# 查看配置信息
sage config show

# 初始化配置文件
sage config init
```
```

## 🔌 扩展管理

### 扩展信息

```bash
# 显示可用扩展信息
sage extensions

# 查看当前安装状态
sage extensions  # 会显示当前安装的扩展状态
```

### 扩展安装（通过pip）

```bash
# 安装前端扩展
pip install isage[frontend]

# 安装开发工具扩展
pip install isage[dev]

# 安装所有免费扩展
pip install isage[full]

# 安装商业扩展（需要授权）
pip install isage[commercial]
```

## � 示例命令组合

### 生产部署

```bash
# 1. 启动SAGE系统
sage deploy start

# 2. 检查集群状态
sage cluster status

# 3. 启动作业管理器
sage jobmanager start

# 4. 监控系统状态
sage deploy status
```

### 运维监控

```bash
# 1. 检查集群健康
sage cluster status
sage deploy status

# 2. 查看作业状态
sage job list
sage job status

# 3. 系统诊断
sage doctor check

# 4. 查看Web界面
sage web-ui start
sage studio start
```

## 🔧 故障排除

### 常见问题诊断

```bash
# 检查系统状态
sage doctor check
```

## 📚 更多信息

- 查看 `sage <command> --help` 获取详细帮助
- 访问 [CLI 参考文档](../cli-reference.md) 了解所有命令
- 查看 [配置参考](../configuration.md) 了解配置选项
