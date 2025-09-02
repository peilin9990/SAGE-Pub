# 🔧 故障排除指南

## 常见问题与解决方案

### 1. "连接失败: Gist 请求失败: 403" 错误

#### 问题描述
- 读取 Gist 时出现 403 权限错误
- 但写入功能正常工作

#### 原因分析
这通常发生在以下情况：
- ✅ **Secret Gist**: 您的 Gist 是私有的，需要认证才能读取
- ✅ **缺少认证头**: 读取请求没有包含 GitHub Token

#### 解决方案

**方法 1: 使用 Token 认证读取**
1. 在测试页面或主程序中输入您的 GitHub Token
2. 系统会自动在读取请求中添加认证头
3. 这样既可以读取 Secret Gist，也可以读取 Public Gist

**方法 2: 将 Gist 设为公开**
1. 访问您的 Gist 页面
2. 点击 "Edit" 按钮
3. 取消勾选 "Secret" 选项
4. 保存更改

#### 推荐做法
- 🔒 **生产环境**: 使用 Secret Gist + Token 认证（更安全）
- 🌐 **测试环境**: 可以使用 Public Gist（更方便测试）

### 2. Token 权限问题

#### 问题描述
- Token 无效或权限不足
- 401 Unauthorized 错误

#### 解决方案
确保您的 GitHub Personal Access Token 包含以下权限：
- ✅ `gist` - 完整的 Gist 访问权限

### 3. Gist ID 格式问题

#### 问题描述
- 404 Not Found 错误
- Gist 不存在

#### 解决方案
1. 检查 Gist ID 格式（应该是32位十六进制字符）
2. 确认 Gist 确实存在且未被删除
3. 从 Gist URL 中正确提取 ID
   ```
   https://gist.github.com/username/b7b18befbd332c97f938e7859df5f7ef
   ID 是: b7b18befbd332c97f938e7859df5f7ef
   ```

### 4. 网络连接问题

#### 问题描述
- 请求超时
- 网络错误

#### 解决方案
1. 检查网络连接
2. 确认可以访问 api.github.com
3. 检查防火墙设置

### 5. 数据格式错误

#### 问题描述
- JSON 解析错误
- 数据结构不匹配

#### 解决方案
1. 使用测试工具验证 Gist 内容
2. 确保 JSON 格式正确
3. 重置 Gist 内容为默认格式

## 🧪 测试工具使用

### 连接测试页面
访问 [Gist 连接测试](/join_sage/gist_test/) 页面：

1. **输入 Gist ID**: 从您的 Gist URL 中获取
2. **输入 Token**: 如果是 Secret Gist 或需要写入权限
3. **测试读取**: 验证基本连接
4. **测试写入**: 验证写入权限

### 测试结果解读

#### 成功案例
```
✅ Gist 读取成功！
📄 Gist 信息:
   - 创建者: your-username
   - 创建时间: 2024/09/02 15:13:07
   - 更新时间: 2024/09/02 15:13:22
   - 文件数量: 1
✅ 找到 schedule_data.json 文件
```

#### 失败案例及解决
```
❌ 读取失败: HTTP 403: 
💡 可能的原因:
   - Secret gist 需要身份验证
解决方案: 输入您的 GitHub Token
```

## 🔑 安全最佳实践

### Token 管理
1. **永远不要**在代码中硬编码 Token
2. 使用环境变量或运行时配置
3. 定期轮换 Token
4. 使用最小权限原则

### Gist 安全
1. 不要在 Gist 中存储敏感信息
2. 定期备份重要数据
3. 使用 Secret Gist 保护隐私

## 📞 获取帮助

如果以上解决方案都无法解决您的问题：

1. 检查 [GitHub API 状态](https://www.githubstatus.com/)
2. 查看浏览器开发者工具的控制台错误
3. 尝试使用不同的 Gist 或重新创建
4. 联系技术支持

---

**更新时间**: 2024年9月2日  
**版本**: v1.1 - 增加了 Secret Gist 认证支持
