# 🤖 GitHub Actions Environment Secrets 设置指南

## 🎯 概述

使用 GitHub Actions Environment Secrets 是管理敏感信息（如 GitHub Token）的最佳实践。这种方式确保 Token 不会出现在源代码中，只在构建和部署时安全地注入。

## 📋 设置步骤

### 第一步：创建 GitHub Personal Access Token

1. **访问 GitHub 设置**
   - 打开 https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"

2. **配置 Token**
   - **Note**: `SAGE Weekly Schedule Gist Access`
   - **Expiration**: 建议选择 90 days 或 1 year
   - **Scopes**: 只勾选 `gist` 权限

3. **生成并复制 Token**
   - 点击 "Generate token"
   - **立即复制保存**，页面刷新后无法再次查看

### 第二步：设置 Repository Secret

1. **进入仓库设置**
   - 打开您的 GitHub 仓库 `intellistream/SAGE-Pub`
   - 点击 `Settings` 标签页

2. **添加 Secret**
   - 侧边栏选择 `Secrets and variables` → `Actions`
   - 点击 `New repository secret`

3. **配置 Secret**
   - **Name**: `GIST_TOKEN`
   - **Secret**: 粘贴您在第一步复制的 Token
   - 点击 `Add secret`

### 第三步：验证配置

1. **触发部署**
   - 推送任何更改到 `main` 分支
   - 或者在 Actions 页面手动触发工作流

2. **检查部署日志**
   - 访问 `Actions` 标签页
   - 查看最新的 "Deploy SAGE Documentation" 工作流
   - 确认 "Inject GitHub Token" 步骤成功执行

3. **测试功能**
   - 访问部署后的网站
   - 打开浏览器开发者工具控制台
   - 应该看到 "🔑 GitHub Token 已从环境变量注入" 的消息

## 🔧 工作原理

### 构建时注入

GitHub Actions 在构建时执行以下操作：

```bash
# 创建运行时配置文件
cat > docs_src/assets/js/runtime-config.js << 'EOF'
window.SAGE_RUNTIME_CONFIG = window.SAGE_RUNTIME_CONFIG || {};
window.SAGE_RUNTIME_CONFIG.gistToken = '${{ secrets.GIST_TOKEN }}';
EOF

# 在 HTML 中注入配置引用
sed -i '/<script>/i <script src="../../assets/js/runtime-config.js"></script>' \
  docs_src/join_sage/weekly_meeting_v2.md
```

### 运行时使用

JavaScript 代码从运行时配置获取 Token：

```javascript
this.GITHUB_CONFIG = {
    gistId: 'b7b18befbd332c97f938e7859df5f7ef',
    token: window.SAGE_RUNTIME_CONFIG?.gistToken || '', // 从环境变量获取
    filename: 'schedule_data.json'
};
```

## 🛡️ 安全优势

1. **源码安全**: Token 永远不会出现在源代码中
2. **传输安全**: Token 通过 HTTPS 加密传输
3. **存储安全**: GitHub 加密存储 Secrets
4. **访问控制**: 只有仓库管理员可以查看/修改 Secrets
5. **审计日志**: 所有 Secret 使用都有日志记录

## 🔄 本地开发

### 方法一：使用配置界面（推荐）

在本地开发时，直接使用网页上的"⚙️ 配置 Gist"按钮设置 Token。

### 方法二：创建本地配置文件

```javascript
// docs_src/assets/js/runtime-config.local.js
window.SAGE_RUNTIME_CONFIG = window.SAGE_RUNTIME_CONFIG || {};
window.SAGE_RUNTIME_CONFIG.gistToken = 'your_local_token_here';
```

然后在 HTML 中引入：
```html
<script src="../../assets/js/runtime-config.local.js"></script>
```

⚠️ **注意**: 不要将包含真实 Token 的本地配置文件提交到 Git！

## 📊 配置状态检查

您可以通过以下方式检查配置状态：

1. **浏览器控制台**
   ```javascript
   console.log('Token 状态:', window.SAGE_RUNTIME_CONFIG?.gistToken ? '已配置' : '未配置');
   ```

2. **网页界面**
   - 查看同步状态指示器
   - 使用"🧪 连接测试工具"验证

3. **GitHub Actions 日志**
   - 检查部署工作流的执行日志
   - 确认 Token 注入步骤成功

## 🚀 部署后验证

部署完成后，访问您的网站：

1. **打开周会排班页面**
   - 访问云端同步版本
   - 检查是否能正常加载数据

2. **测试写入功能**
   - 尝试拖拽成员到不同区域
   - 观察同步状态变化

3. **检查控制台消息**
   ```
   📋 本地开发配置已加载
   🔑 GitHub Token 已从环境变量注入
   ✅ 连接成功！
   ```

## 🔧 故障排除

### Secret 未生效

1. 检查 Secret 名称是否为 `GIST_TOKEN`
2. 确认工作流有权限访问 Secrets
3. 重新触发部署工作流

### Token 权限错误

1. 确认 Token 包含 `gist` 权限
2. 检查 Token 是否已过期
3. 验证 Gist ID 是否正确

### 部署失败

1. 检查 GitHub Actions 日志
2. 确认 `mkdocs.yml` 配置正确
3. 验证依赖安装成功

---

**配置完成！** 🎉 您的周会排班系统现在使用安全的环境变量管理 Token，既保证了功能正常，又确保了安全性。
