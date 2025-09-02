# 🧪 Gist 连接测试

这个页面可以帮助您测试 Gist 连接是否正常工作。

<div id="test-container">
    <h3>连接测试</h3>
    <div class="test-section">
        <label for="gist-id">Gist ID:</label>
        <input type="text" id="gist-id" placeholder="输入您的 Gist ID" style="width: 300px; padding: 8px; margin: 5px;">
    </div>
    
    <div class="test-section">
        <label for="github-token">GitHub Token (可选):</label>
        <input type="password" id="github-token" placeholder="输入您的 GitHub Token" style="width: 300px; padding: 8px; margin: 5px;">
        <small style="display: block; color: #666;">仅用于测试写入功能，不会被保存</small>
    </div>
    
    <div class="test-buttons">
        <button onclick="testRead()" style="padding: 10px 20px; margin: 10px 5px; background: #007acc; color: white; border: none; border-radius: 5px; cursor: pointer;">测试读取</button>
        <button onclick="testWrite()" style="padding: 10px 20px; margin: 10px 5px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">测试写入</button>
        <button onclick="clearResults()" style="padding: 10px 20px; margin: 10px 5px; background: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer;">清除结果</button>
    </div>
    
    <div id="test-results" style="margin-top: 20px; padding: 15px; background: #f8f9fa; border-radius: 5px; min-height: 100px;">
        <strong>测试结果将显示在这里...</strong>
    </div>
</div>

<style>
#test-container {
    max-width: 800px;
    margin: 20px auto;
    padding: 20px;
    border: 1px solid #ddd;
    border-radius: 8px;
    background: white;
}

.test-section {
    margin: 15px 0;
}

.test-section label {
    display: block;
    font-weight: bold;
    margin-bottom: 5px;
}

.test-buttons {
    margin: 20px 0;
}

#test-results {
    font-family: 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.5;
    white-space: pre-wrap;
    max-height: 400px;
    overflow-y: auto;
}

.success {
    color: #28a745;
}

.error {
    color: #dc3545;
}

.info {
    color: #007acc;
}
</style>

<script>
function log(message, type = 'info') {
    const results = document.getElementById('test-results');
    const timestamp = new Date().toLocaleTimeString();
    const className = type === 'success' ? 'success' : type === 'error' ? 'error' : 'info';
    
    if (results.innerHTML === '<strong>测试结果将显示在这里...</strong>') {
        results.innerHTML = '';
    }
    
    results.innerHTML += `<span class="${className}">[${timestamp}] ${message}</span>\n`;
    results.scrollTop = results.scrollHeight;
}

async function testRead() {
    const gistId = document.getElementById('gist-id').value.trim();
    const token = document.getElementById('github-token').value.trim();
    
    if (!gistId) {
        log('请输入 Gist ID', 'error');
        return;
    }
    
    log('开始测试读取...', 'info');
    
    try {
        // 构建请求选项，如果有 token 就添加认证头
        const fetchOptions = {
            method: 'GET',
            headers: {
                'Accept': 'application/vnd.github.v3+json'
            }
        };
        
        if (token) {
            fetchOptions.headers['Authorization'] = `token ${token}`;
            log('🔐 使用认证 Token 进行读取', 'info');
        } else {
            log('📖 尝试公开读取（如果是 Secret Gist 可能会失败）', 'info');
        }
        
        const response = await fetch(`https://api.github.com/gists/${gistId}`, fetchOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const gist = await response.json();
        log('✅ Gist 读取成功！', 'success');
        log(`📄 Gist 信息:`, 'info');
        log(`   - 创建者: ${gist.owner.login}`, 'info');
        log(`   - 创建时间: ${new Date(gist.created_at).toLocaleString()}`, 'info');
        log(`   - 更新时间: ${new Date(gist.updated_at).toLocaleString()}`, 'info');
        log(`   - 文件数量: ${Object.keys(gist.files).length}`, 'info');
        
        const scheduleFile = gist.files['schedule_data.json'];
        if (scheduleFile) {
            log('✅ 找到 schedule_data.json 文件', 'success');
            try {
                const data = JSON.parse(scheduleFile.content);
                log(`📊 数据信息:`, 'info');
                log(`   - 成员数量: ${data.members?.length || 0}`, 'info');
                log(`   - 当前周期: ${data.currentCycle || 'N/A'}`, 'info');
                log(`   - 最后同步: ${data.lastSync ? new Date(data.lastSync).toLocaleString() : '从未'}`, 'info');
            } catch (parseError) {
                log('⚠️ JSON 数据格式错误: ' + parseError.message, 'error');
            }
        } else {
            log('❌ 未找到 schedule_data.json 文件', 'error');
            log('📁 可用文件: ' + Object.keys(gist.files).join(', '), 'info');
        }
        
    } catch (error) {
        log('❌ 读取失败: ' + error.message, 'error');
        
        if (error.message.includes('404')) {
            log('💡 可能的原因:', 'info');
            log('   - Gist ID 不正确', 'info');
            log('   - Gist 不存在或已删除', 'info');
            log('   - Secret gist 需要身份验证', 'info');
        }
    }
}

async function testWrite() {
    const gistId = document.getElementById('gist-id').value.trim();
    const token = document.getElementById('github-token').value.trim();
    
    if (!gistId) {
        log('请输入 Gist ID', 'error');
        return;
    }
    
    if (!token) {
        log('请输入 GitHub Token 以测试写入功能', 'error');
        return;
    }
    
    log('开始测试写入...', 'info');
    
    // 创建测试数据
    const testData = {
        test: true,
        timestamp: new Date().toISOString(),
        message: '这是一个测试写入'
    };
    
    try {
        const response = await fetch(`https://api.github.com/gists/${gistId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `token ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/vnd.github.v3+json'
            },
            body: JSON.stringify({
                files: {
                    'test_write.json': {
                        content: JSON.stringify(testData, null, 2)
                    }
                }
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`HTTP ${response.status}: ${errorData.message || response.statusText}`);
        }
        
        const result = await response.json();
        log('✅ 写入测试成功！', 'success');
        log(`📝 已创建测试文件: test_write.json`, 'success');
        log(`🔗 查看 Gist: ${result.html_url}`, 'info');
        
        // 清理测试文件
        log('正在清理测试文件...', 'info');
        const cleanupResponse = await fetch(`https://api.github.com/gists/${gistId}`, {
            method: 'PATCH',
            headers: {
                'Authorization': `token ${token}`,
                'Content-Type': 'application/json',
                'Accept': 'application/vnd.github.v3+json'
            },
            body: JSON.stringify({
                files: {
                    'test_write.json': null // 删除文件
                }
            })
        });
        
        if (cleanupResponse.ok) {
            log('✅ 测试文件已清理', 'success');
        } else {
            log('⚠️ 测试文件清理失败，请手动删除', 'error');
        }
        
    } catch (error) {
        log('❌ 写入失败: ' + error.message, 'error');
        
        if (error.message.includes('401')) {
            log('💡 可能的原因:', 'info');
            log('   - Token 无效或已过期', 'info');
            log('   - Token 缺少 gist 权限', 'info');
        } else if (error.message.includes('404')) {
            log('💡 可能的原因:', 'info');
            log('   - Gist ID 不正确', 'info');
            log('   - 没有写入权限', 'info');
        }
    }
}

function clearResults() {
    document.getElementById('test-results').innerHTML = '<strong>测试结果将显示在这里...</strong>';
}

// 页面加载时的提示
document.addEventListener('DOMContentLoaded', function() {
    log('🧪 Gist 连接测试工具已准备就绪', 'info');
    log('📝 使用步骤:', 'info');
    log('   1. 输入您的 Gist ID', 'info');
    log('   2. 点击"测试读取"验证 Gist 访问', 'info');
    log('   3. 输入 GitHub Token（可选）', 'info');
    log('   4. 点击"测试写入"验证写入权限', 'info');
    log('', 'info');
});
</script>
