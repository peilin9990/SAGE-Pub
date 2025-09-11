# SAGE Middleware 中间件服务

SAGE Middleware 是位于 SAGE Kernel 和应用层之间的服务层，提供了一系列开箱即用的中间件服务，包括存储、消息队列、缓存等基础设施服务。

## 🏗️ 架构定位

```
┌─────────────────┐
│   Applications  │  ← RAG、Agent、Tools等高级应用
├─────────────────┤
│   Middleware    │  ← 中间件服务层 (当前文档)
├─────────────────┤  
│   SAGE Kernel   │  ← 核心流处理引擎
└─────────────────┘
```

Middleware 层为应用层提供了标准化的服务接口，屏蔽了底层实现的复杂性，让开发者能够专注于业务逻辑的实现。

## 📋 核心服务

### Memory 服务
提供高性能的内存存储和缓存服务：

<!-- - [Memory 概览](service/memory/memory_intro.md) - 内存服务架构和特性 -->
<!-- - [Memory API](service/memory/memory_api.md) - 内存服务API参考 -->

### 键值存储服务 (KV Service)
分布式键值存储，支持：
- 高并发读写
- 数据持久化
- 集群部署
- 自动故障转移

### 向量数据库服务 (VDB Service)  
专为AI应用优化的向量存储：
- 高维向量存储
- 相似性搜索
- 多种距离度量
- 索引优化

### 消息队列服务
异步消息处理：
- 发布/订阅模式
- 消息持久化
- 负载均衡
- 死信队列

## 🚀 快速开始

### 基础使用

```python
from sage.middleware.services import MemoryService, KVService

# 初始化内存服务
memory = MemoryService()
memory.set("key1", "value1")
value = memory.get("key1")

# 初始化KV服务
kv = KVService()
kv.put("user:123", {"name": "张三", "age": 25})
user = kv.get("user:123")
```

### 与 Kernel 集成

```python
from sage.core.api import LocalEnvironment
from sage.middleware.services import VDBService

# 在流处理中使用向量数据库
env = LocalEnvironment("vdb_demo")
vdb = VDBService()

def store_embeddings(data):
    # 存储向量到VDB
    vdb.insert(data["id"], data["vector"])
    return data

def search_similar(query_vector):
    # 搜索相似向量
    results = vdb.search(query_vector, top_k=10)
    return results

stream = env.create_stream("embeddings")
stream.map(store_embeddings).sink(print)
```

## 🔧 服务配置

### 统一配置接口

所有中间件服务都支持统一的配置接口：

```python
from sage.middleware.config import ServiceConfig

config = ServiceConfig({
    "memory": {
        "max_size": "1GB",
        "eviction_policy": "LRU"
    },
    "kv": {
        "persistence": True,
        "sync_interval": 30
    },
    "vdb": {
        "dimension": 768,
        "index_type": "HNSW"
    }
})
```

### 环境变量配置

```bash
# Memory 服务配置
SAGE_MEMORY_MAX_SIZE=2GB
SAGE_MEMORY_EVICTION_POLICY=LFU

# KV 服务配置  
SAGE_KV_PERSISTENCE=true
SAGE_KV_BACKUP_INTERVAL=60

# VDB 服务配置
SAGE_VDB_DIMENSION=1024
SAGE_VDB_INDEX_TYPE=IVF
```

## 📊 监控和运维

### 健康检查

每个服务都提供健康检查接口：

```python
from sage.middleware.health import HealthChecker

checker = HealthChecker()
status = checker.check_all_services()

print(f"Memory Service: {status['memory']}")
print(f"KV Service: {status['kv']}")  
print(f"VDB Service: {status['vdb']}")
```

### 性能指标

```python
from sage.middleware.metrics import MetricsCollector

metrics = MetricsCollector()
stats = metrics.get_service_stats()

print(f"Memory Usage: {stats['memory']['usage']}")
print(f"KV Operations/sec: {stats['kv']['ops_per_sec']}")
print(f"VDB Query Latency: {stats['vdb']['avg_latency']}")
```

## 🔗 集成示例

### RAG 应用集成

```python
from sage.middleware.services import VDBService, KVService
from sage.applications.rag import RAGPipeline

# 初始化服务
vdb = VDBService()  # 存储文档向量
kv = KVService()    # 缓存查询结果

# 创建 RAG 管道
rag = RAGPipeline(
    vector_store=vdb,
    cache_store=kv
)

# 处理查询
answer = rag.query("什么是SAGE框架？")
```

### 多租户支持

```python
from sage.middleware.tenant import TenantManager

# 创建租户管理器
tenant_mgr = TenantManager()

# 为不同租户创建隔离的服务实例
tenant_a_vdb = tenant_mgr.get_service("tenant_a", "vdb")
tenant_b_vdb = tenant_mgr.get_service("tenant_b", "vdb")

# 数据隔离，互不干扰
tenant_a_vdb.insert("doc1", vector_a)
tenant_b_vdb.insert("doc1", vector_b)
```

## 🔒 安全特性

### 访问控制

```python
from sage.middleware.auth import ServiceAuth

auth = ServiceAuth()

# 设置服务访问权限
auth.grant_permission("user123", "memory", ["read", "write"])
auth.grant_permission("user456", "vdb", ["read"])

# 验证权限
if auth.check_permission("user123", "memory", "write"):
    memory.set("key", "value")
```

### 数据加密

```python
from sage.middleware.encryption import DataEncryption

encryption = DataEncryption()

# 存储时自动加密
kv.put("sensitive_data", encryption.encrypt(data))

# 读取时自动解密  
decrypted_data = encryption.decrypt(kv.get("sensitive_data"))
```

## 🚀 部署模式

### 单机部署

```yaml
# docker-compose.yml
version: '3.8'
services:
  sage-middleware:
    image: sage/middleware:latest
    environment:
      - SAGE_MODE=standalone
    ports:
      - "8080:8080"
```

### 集群部署

```yaml
# kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sage-middleware
spec:
  replicas: 3
  selector:
    matchLabels:
      app: sage-middleware
  template:
    spec:
      containers:
      - name: middleware
        image: sage/middleware:latest
        env:
        - name: SAGE_MODE
          value: cluster
        - name: SAGE_CLUSTER_NODES
          value: "node1:8080,node2:8080,node3:8080"
```

---

SAGE Middleware 通过提供标准化、高性能的基础服务，大大简化了复杂应用的开发和部署。它是连接底层 Kernel 和上层应用的重要桥梁。
