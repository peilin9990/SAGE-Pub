# GitHub Gist 同步实现指南

## 步骤 1: 创建 GitHub Gist

1. 访问 https://gist.github.com/
2. 创建一个新的 Gist，文件名为 `schedule_data.json`
3. 初始内容设置为：
```json
{
  "members": [],
  "currentCycle": 1,
  "weekHistory": [],
  "currentWeekPresenters": [],
  "nextWeekPresenters": [],
  "lastSync": null,
  "version": "2.0"
}
```
4. 创建后记录 Gist ID（URL 中的长字符串）

## 步骤 2: 获取 GitHub Token（可选，用于写入操作）

1. 访问 GitHub Settings > Developer settings > Personal access tokens
2. 生成新的 token，权限选择 `gist`
3. 保存生成的 token

## 步骤 3: 更新网页代码

在 weekly_meeting_v2.md 中找到以下配置并更新：

```javascript
this.GITHUB_CONFIG = {
    gistId: 'your_gist_id_here', // 替换为您的 Gist ID
    token: 'your_github_token_here' // 可选：用于写入操作
};
```

## 步骤 4: 实现读写方法

以下是完整的 Gist 同步实现：

```javascript
async fetchFromGist() {
    const { gistId } = this.GITHUB_CONFIG;
    const response = await fetch(`https://api.github.com/gists/${gistId}`);
    
    if (!response.ok) {
        throw new Error('Gist 请求失败');
    }
    
    const gist = await response.json();
    const content = gist.files['schedule_data.json']?.content;
    
    if (content) {
        return { data: JSON.parse(content) };
    }
    
    return null;
}

async saveToGist(data) {
    const { gistId, token } = this.GITHUB_CONFIG;
    
    if (!token) {
        throw new Error('需要 GitHub Token 才能保存数据');
    }
    
    const response = await fetch(`https://api.github.com/gists/${gistId}`, {
        method: 'PATCH',
        headers: {
            'Authorization': `token ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            files: {
                'schedule_data.json': {
                    content: JSON.stringify(data, null, 2)
                }
            }
        })
    });
    
    if (!response.ok) {
        throw new Error('Gist 保存失败');
    }
    
    return await response.json();
}
```
