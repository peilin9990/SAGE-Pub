# 服务快速入门：在算子（Function）中注入并使用服务

本节面向已理解 SAGE 编程模型的读者，演示如何注册服务并在算子中调用。示例尽量对齐仓库现有接口与用法。

## 示例一：注册 Memory Service 并在 Function 中调用

=== "Python"
    ```python title="环境中注册服务 + 在 Function 中调用" linenums="1"
    from sage.core.api.local_environment import LocalEnvironment
    from sage.core.api.function.base_function import BaseFunction
    from sage.middleware.services.memory import MemoryService  # 参考仓库 README 用法

    # 1) 在环境中注册服务（工厂函数返回服务实例）
    def memory_service_factory():
        service = MemoryService()
        # 如需初始化集合，可在此进行（示例取自 README 思路）：
        # service.create_collection(name="qa_collection", backend_type="VDB", description="QA pipeline memory")
        return service

    env = LocalEnvironment("svc_quickstart")
    env.register_service("memory_service", memory_service_factory)

    # 2) 在 Function 中通过 call_service 访问服务
    class ConversationMemory(BaseFunction):
        def execute(self, data):
            session_id = data["session_id"]
            content = data["content"]
            vector = data["vector"]

            # 存储记忆（同步）
            memory_id = self.call_service["memory_service"].store_memory(
                content=content,
                vector=vector,
                session_id=session_id,
                memory_type="conversation",
                metadata={"source": "user_input"}
            )

            # 检索相关记忆（同步）
            related = self.call_service["memory_service"].retrieve_memories(
                query_vector=vector,
                session_id=session_id,
                top_k=5
            )
            return {"memory_id": memory_id, "related": related}
    ```

要点：
- 使用 env.register_service("name", factory) 注册服务
- 在 BaseFunction.execute 中用 self.call_service["name"].method(...) 访问服务
- 需要并发/非阻塞时，使用 self.call_service_async["name"].method(...)

## 示例二：仅使用 KV 服务（最小闭环）

=== "Python"
    ```python title="仅 KV 服务最小示例（调用风格一致）" linenums="1"
    from sage.core.api.function.base_function import BaseFunction

    class KVWriter(BaseFunction):
        def execute(self, data):
            self.call_service["kv_service"].put("key1", data)
            return {"ok": True}

    class KVReader(BaseFunction):
        def execute(self, _):
            fut = self.call_service_async["kv_service"].get("key1")
            value = fut.result(timeout=5)
            return {"value": value}
    ```

提示：
- 上述示例假设你已在环境中注册了名为 "kv_service" 的服务
- 实际后端（内存/Redis/等）由服务实现决定；调用侧不感知
