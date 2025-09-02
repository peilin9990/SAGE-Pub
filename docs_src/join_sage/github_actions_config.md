# GitHub Actions 环境变量配置方案

## 🎯 使用 GitHub Actions Secrets 管理 Token

这是最安全的方案，Token 不会出现在代码中，只在构建时注入。

### 第一步：设置 GitHub Secrets

1. **进入仓库设置**
   - 打开您的 GitHub 仓库
   - 点击 `Settings` → `Secrets and variables` → `Actions`

2. **添加 Repository Secret**
   - 点击 `New repository secret`
   - Name: `GIST_TOKEN`
   - Secret: 您的 GitHub Token
   - 点击 `Add secret`

### 第二步：创建 GitHub Actions 工作流

创建 `.github/workflows/deploy.yml` 文件：

```yaml
name: Deploy Documentation

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Configure Gist Token
      run: |
        # 替换配置文件中的 token 占位符
        sed -i "s/GIST_TOKEN_PLACEHOLDER/${{ secrets.GIST_TOKEN }}/g" docs_src/join_sage/weekly_meeting_v2.md
    
    - name: Build documentation
      run: |
        mkdocs build
    
    - name: Upload artifact
      uses: actions/upload-pages-artifact@v2
      with:
        path: ./site

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
    - name: Deploy to GitHub Pages
      id: deployment
      uses: actions/deploy-pages@v2
```

### 第三步：修改代码使用占位符

在 `weekly_meeting_v2.md` 中使用占位符：

```javascript
this.GITHUB_CONFIG = {
    gistId: 'b7b18befbd332c97f938e7859df5f7ef',
    token: 'GIST_TOKEN_PLACEHOLDER', // 构建时会被替换
    filename: 'schedule_data.json'
};
```

## 方案二：运行时从环境获取（推荐）

### 创建配置注入脚本

创建 `docs_src/assets/config.js`：

```javascript
// 这个文件在构建时生成，包含环境变量
window.SAGE_RUNTIME_CONFIG = {
    gistToken: '{{GIST_TOKEN}}' // 构建时替换
};
```

### 修改 HTML 引入配置

在 `weekly_meeting_v2.md` 的 `<script>` 标签前添加：

```html
<script>
// 运行时配置
window.SAGE_RUNTIME_CONFIG = window.SAGE_RUNTIME_CONFIG || {};
</script>
```

### 修改 JavaScript 代码

```javascript
constructor() {
    // GitHub Gist 配置
    this.GITHUB_CONFIG = {
        gistId: 'b7b18befbd332c97f938e7859df5f7ef',
        token: window.SAGE_RUNTIME_CONFIG?.gistToken || '', // 从运行时配置获取
        filename: 'schedule_data.json'
    };
    
    // 如果没有配置 token，提示用户
    if (!this.GITHUB_CONFIG.token) {
        console.warn('未检测到 GitHub Token，请配置后使用写入功能');
    }
    
    // 尝试从 localStorage 加载配置（作为后备方案）
    this.loadConfig();
}
```

## 方案三：使用 MkDocs 环境变量插件

### 安装插件

```bash
pip install mkdocs-macros-plugin
```

### 配置 mkdocs.yml

```yaml
plugins:
  - macros:
      module_name: macros
      
extra:
  gist_token: !ENV GIST_TOKEN
```

### 在 Markdown 中使用

```javascript
this.GITHUB_CONFIG = {
    gistId: 'b7b18befbd332c97f938e7859df5f7ef',
    token: '{{ extra.gist_token }}', // MkDocs 变量
    filename: 'schedule_data.json'
};
```

## 🚀 推荐实现方案

我推荐使用**方案二**，因为它：
- ✅ 安全：Token 不出现在源码中
- ✅ 灵活：支持运行时配置
- ✅ 简单：易于实现和维护
- ✅ 兼容：支持本地开发和生产环境

您希望我帮您实现哪种方案？
