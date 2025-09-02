# 免费云端数据库同步方案

## 方案 A: 使用 Firebase Realtime Database

### 优点：
- 完全免费（有配额限制）
- 实时同步
- 简单易用
- 支持离线缓存

### 实现步骤：

1. **创建 Firebase 项目**
   - 访问 https://console.firebase.google.com/
   - 创建新项目
   - 启用 Realtime Database

2. **获取配置信息**
```javascript
const firebaseConfig = {
  apiKey: "your-api-key",
  authDomain: "your-project.firebaseapp.com",
  databaseURL: "https://your-project-default-rtdb.firebaseio.com/",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
};
```

3. **集成代码**
```html
<!-- 在 HTML 中添加 Firebase SDK -->
<script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-app.js"></script>
<script src="https://www.gstatic.com/firebasejs/9.0.0/firebase-database.js"></script>

<script>
// 初始化 Firebase
import { initializeApp } from 'firebase/app';
import { getDatabase, ref, set, get } from 'firebase/database';

const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

class FirebaseScheduler {
    async saveToCloud(data) {
        try {
            await set(ref(database, 'schedule'), data);
            this.updateSyncStatus('synced', '数据已同步到云端');
        } catch (error) {
            this.updateSyncStatus('error', '同步失败');
            throw error;
        }
    }
    
    async loadFromCloud() {
        try {
            const snapshot = await get(ref(database, 'schedule'));
            if (snapshot.exists()) {
                return { data: snapshot.val() };
            }
            return null;
        } catch (error) {
            throw new Error('云端加载失败');
        }
    }
}
</script>
```

## 方案 B: 使用 JSONBin.io

### 优点：
- 完全免费
- 简单的 REST API
- 无需注册即可使用
- 支持版本控制

### 实现步骤：

1. **创建 JSONBin**
   - 访问 https://jsonbin.io/
   - 创建账号获取 API Key（可选）

2. **集成代码**
```javascript
class JSONBinScheduler {
    constructor() {
        this.JSONBIN_CONFIG = {
            binId: 'your_bin_id_here', // 创建后获得
            apiKey: 'your_api_key_here' // 可选
        };
    }
    
    async saveToCloud(data) {
        const { binId, apiKey } = this.JSONBIN_CONFIG;
        
        const headers = {
            'Content-Type': 'application/json',
        };
        
        if (apiKey) {
            headers['X-Master-Key'] = apiKey;
        }
        
        const response = await fetch(`https://api.jsonbin.io/v3/b/${binId}`, {
            method: 'PUT',
            headers: headers,
            body: JSON.stringify(data)
        });
        
        if (!response.ok) {
            throw new Error('JSONBin 保存失败');
        }
        
        return await response.json();
    }
    
    async loadFromCloud() {
        const { binId, apiKey } = this.JSONBIN_CONFIG;
        
        const headers = {};
        if (apiKey) {
            headers['X-Master-Key'] = apiKey;
        }
        
        const response = await fetch(`https://api.jsonbin.io/v3/b/${binId}/latest`, {
            headers: headers
        });
        
        if (!response.ok) {
            throw new Error('JSONBin 加载失败');
        }
        
        const result = await response.json();
        return { data: result.record };
    }
}
```

## 方案 C: 使用 Supabase

### 优点：
- 免费额度充足
- PostgreSQL 数据库
- 实时订阅功能
- 完整的后端服务

### 实现步骤：

1. **创建 Supabase 项目**
   - 访问 https://supabase.com/
   - 创建新项目
   - 创建表结构

2. **SQL 表结构**
```sql
CREATE TABLE schedule_data (
  id SERIAL PRIMARY KEY,
  data JSONB NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 插入初始数据
INSERT INTO schedule_data (data) VALUES ('{}');
```

3. **集成代码**
```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'your-supabase-url'
const supabaseKey = 'your-supabase-anon-key'
const supabase = createClient(supabaseUrl, supabaseKey)

class SupabaseScheduler {
    async saveToCloud(data) {
        const { error } = await supabase
            .from('schedule_data')
            .update({ data: data, updated_at: new Date() })
            .eq('id', 1);
            
        if (error) {
            throw new Error('Supabase 保存失败');
        }
    }
    
    async loadFromCloud() {
        const { data, error } = await supabase
            .from('schedule_data')
            .select('data')
            .eq('id', 1)
            .single();
            
        if (error) {
            throw new Error('Supabase 加载失败');
        }
        
        return { data: data.data };
    }
    
    // 实时监听数据变化
    subscribeToChanges() {
        supabase
            .channel('schedule_changes')
            .on('postgres_changes', 
                { event: 'UPDATE', schema: 'public', table: 'schedule_data' },
                (payload) => {
                    this.loadData(payload.new.data);
                    this.renderMembers();
                    this.updateSyncStatus('synced', '数据已同步');
                }
            )
            .subscribe();
    }
}
```

## 推荐选择

1. **最简单**: JSONBin.io - 无需配置，直接使用
2. **最可靠**: Firebase - Google 提供，稳定性高
3. **最强大**: Supabase - 功能最全面，支持实时同步

根据您的需求选择合适的方案即可。
