# 🚀 GitHub Gist 配置快速指南

## 第一步：创建 GitHub Gist

1. **访问 GitHub Gist**
   - 打开 https://gist.github.com/
   - 登录您的 GitHub 账号

2. **创建新的 Gist**
   - 点击右上角的 `+` 按钮
   - 文件名输入：`schedule_data.json`
   - 文件内容粘贴以下初始数据：

```json
{
  "members": [
    { "id": 1, "name": "Hongru", "lastPresented": null, "cycleCount": 0 },
    { "id": 2, "name": "Mingqi", "lastPresented": null, "cycleCount": 0 },
    { "id": 3, "name": "Ruicheng", "lastPresented": null, "cycleCount": 0 },
    { "id": 4, "name": "Ruipeng", "lastPresented": null, "cycleCount": 0 },
    { "id": 5, "name": "Xinyan", "lastPresented": null, "cycleCount": 0 },
    { "id": 6, "name": "Ziao", "lastPresented": null, "cycleCount": 0 },
    { "id": 7, "name": "Senlei", "lastPresented": null, "cycleCount": 0 },
    { "id": 8, "name": "Xincai", "lastPresented": null, "cycleCount": 0 },
    { "id": 9, "name": "Liujun", "lastPresented": null, "cycleCount": 0 },
    { "id": 10, "name": "Yanbo", "lastPresented": null, "cycleCount": 0 },
    { "id": 11, "name": "Jinyun", "lastPresented": null, "cycleCount": 0 },
    { "id": 12, "name": "Jingyuan", "lastPresented": null, "cycleCount": 0 },
    { "id": 13, "name": "Peilin", "lastPresented": null, "cycleCount": 0 },
    { "id": 14, "name": "Xiaohan", "lastPresented": null, "cycleCount": 0 },
    { "id": 15, "name": "Changwu", "lastPresented": null, "cycleCount": 0 }
  ],
  "currentCycle": 1,
  "weekHistory": [],
  "currentWeekPresenters": [],
  "nextWeekPresenters": [],
  "lastSync": null,
  "version": "2.0"
}
```

3. **设置为公开或私有**
   - 选择 "Create public gist" 或 "Create secret gist"
   - 推荐选择 "Create public gist" 便于团队访问

4. **获取 Gist ID**
   - 创建后，从 URL 中复制 Gist ID
   - 例如：`https://gist.github.com/username/a1b2c3d4e5f6` 中的 `a1b2c3d4e5f6`

## 第二步：获取 GitHub Token（用于写入数据）

1. **访问 GitHub 设置**
   - 打开 https://github.com/settings/tokens
   - 点击 "Generate new token" → "Generate new token (classic)"

2. **配置 Token**
   - Note: `SAGE Weekly Schedule`
   - Expiration: 选择合适的过期时间
   - Scopes: 勾选 `gist` 权限

3. **生成并保存 Token**
   - 点击 "Generate token"
   - **重要**: 立即复制 Token，页面刷新后将无法再次查看

## 第三步：配置网页

在 `weekly_meeting_v2.md` 文件中找到配置部分，更新为您的信息：

```javascript
// GitHub Gist 配置
this.GITHUB_CONFIG = {
    gistId: 'a1b2c3d4e5f6', // 替换为您的 Gist ID
    token: 'ghp_xxxxxxxxxxxxxxxxxxxx', // 替换为您的 GitHub Token
    filename: 'schedule_data.json'
};
```

## 第四步：测试同步

1. **打开网页**
   - 访问您的 GitHub Pages 上的周会安排页面

2. **测试读取**
   - 页面应该能自动加载 Gist 中的数据
   - 同步状态显示为 "已同步"

3. **测试写入**
   - 拖拽一个成员到不同区域
   - 观察同步状态变化
   - 检查 Gist 是否已更新

## 🔧 故障排除

### 常见问题

**1. "请先配置有效的 Gist ID" 错误**
- 检查 Gist ID 是否正确复制
- 确保没有包含额外的字符或空格

**2. "保存数据需要 GitHub Token" 错误**
- 检查 Token 是否正确配置
- 确保 Token 有 `gist` 权限

**3. "Gist 请求失败: 404" 错误**
- 检查 Gist 是否存在
- 如果是 secret gist，确保有正确的访问权限

**4. "Gist 保存失败: 401" 错误**
- Token 可能已过期或无效
- 重新生成 Token 并更新配置

### 验证步骤

1. **检查 Gist 访问**
   ```bash
   curl https://api.github.com/gists/YOUR_GIST_ID
   ```

2. **检查 Token 权限**
   ```bash
   curl -H "Authorization: token YOUR_TOKEN" https://api.github.com/user
   ```

## 🎉 完成！

配置完成后，您的周会排班系统将：

- ✅ 自动从 Gist 加载最新数据
- ✅ 实时同步所有修改到云端
- ✅ 支持多人同时访问和修改
- ✅ 提供同步状态指示
- ✅ 离线时使用本地缓存

所有团队成员现在都能看到最新的排班安排了！

## 📱 移动端支持

该方案完全支持移动设备访问和操作，团队成员可以在手机上查看和修改排班。

---

**需要帮助？** 如果遇到问题，请检查浏览器控制台的错误信息，或参考上面的故障排除部分。
