# 🔒 GitHub Gist 配置说明

## 重要安全提醒

为了保护您的 GitHub Token 安全，请按照以下步骤配置：

### 方法一：直接在代码中配置（推荐用于私人使用）

在 `weekly_meeting_v2.md` 文件中找到配置部分，更新为：

```javascript
this.GITHUB_CONFIG = {
    gistId: 'b7b18befbd332c97f938e7859df5f7ef', // 您的 Gist ID
    token: 'YOUR_GITHUB_TOKEN_HERE',            // 您的 GitHub Token
    filename: 'schedule_data.json'
};
```

### 方法二：使用环境变量（推荐用于团队使用）

如果您的网站需要多人使用，建议使用以下配置方式：

```javascript
this.GITHUB_CONFIG = {
    gistId: 'b7b18befbd332c97f938e7859df5f7ef',
    token: prompt('请输入您的 GitHub Token:') || '', // 运行时输入
    filename: 'schedule_data.json'
};
```

### 方法三：使用 JavaScript 配置文件

创建一个单独的配置文件 `config.js`：

```javascript
// config.js (不要提交到 git)
window.SAGE_CONFIG = {
    gistId: 'b7b18befbd332c97f938e7859df5f7ef',
    token: 'YOUR_GITHUB_TOKEN_HERE',
    filename: 'schedule_data.json'
};
```

然后在 HTML 中引入：
```html
<script src="config.js"></script>
```

并在代码中使用：
```javascript
this.GITHUB_CONFIG = window.SAGE_CONFIG || {
    gistId: 'b7b18befbd332c97f938e7859df5f7ef',
    token: '',
    filename: 'schedule_data.json'
};
```

## 🔐 Token 安全建议

1. **定期更新 Token**：建议每 3-6 个月更新一次
2. **最小权限原则**：只赋予 `gist` 权限
3. **不要提交到 Git**：确保 Token 不会被提交到代码仓库
4. **团队使用**：考虑为每个团队成员创建单独的 Token

## 📋 当前配置状态

- ✅ Gist ID: `b7b18befbd332c97f938e7859df5f7ef`
- ⚠️ Token: 需要私下配置
- ✅ 文件名: `schedule_data.json`

配置完成后，您的周会排班系统就可以实现全局同步了！
