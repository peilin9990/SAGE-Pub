import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dotenv import load_dotenv
from sage.utils.custom_logger import CustomLogger
from sage.core.api.local_environment import LocalEnvironment
from sage.core.function.batch_function import BatchFunction
from sage.core.function.map_function import MapFunction
from sage.lib.io.sink import TerminalSink
from sage.lib.rag.promptor import QAPromptor
from sage.utils.config_loader import load_config

import os
import json
import requests
from typing import Any, List, Tuple


class OpenAIGenerator(MapFunction):
    """
    生成节点：调用 OpenAI-Compatible / VLLM / DashScope 等端点。
    """

    def __init__(self, config: dict, enable_profile=False, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.enable_profile = enable_profile

        # Profile数据存储路径
        if self.enable_profile:
            if hasattr(self.ctx, 'env_base_dir') and self.ctx.env_base_dir:
                self.data_base_path = os.path.join(self.ctx.env_base_dir, ".sage_states", "generator_data")
            else:
                self.data_base_path = os.path.join(os.getcwd(), ".sage_states", "generator_data")
            os.makedirs(self.data_base_path, exist_ok=True)
            self.data_records = []

        self.num = 1
        self.session = requests.Session()

    def _call_openai_api(self, prompt: str) -> str:
        url = self.config["base_url"].rstrip("/") + "/chat/completions"
        headers = {
            "Content-Type": "application/json",
        }
        if self.config.get("api_key"):
            headers["Authorization"] = f"Bearer {self.config['api_key']}"

        # 强制保证 prompt 是字符串！
        if not isinstance(prompt, str):
            prompt = str(prompt)

        payload = {
            "model": self.config["model_name"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": float(self.config.get("temperature", 0.7)),
            "max_tokens": int(self.config.get("max_tokens", 1024)),
        }

        resp = self.session.post(url, headers=headers, json=payload, timeout=60)
        if resp.status_code != 200:
            print(f"===> DashScope返回: {resp.status_code} {resp.text}")
            resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    def _save_data_record(self, query, prompt, response):
        if not self.enable_profile:
            return
        record = {
            'timestamp': time.time(),
            'query': query,
            'prompt': prompt,
            'response': response,
            'model_name': self.config["model_name"]
        }
        self.data_records.append(record)
        self._persist_data_records()

    def _persist_data_records(self):
        if not self.enable_profile or not self.data_records:
            return
        timestamp = int(time.time())
        filename = f"generator_data_{timestamp}.json"
        path = os.path.join(self.data_base_path, filename)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.data_records, f, ensure_ascii=False, indent=2)
            self.data_records = []
        except Exception as e:
            print(f"Failed to persist data records: {e}")

    def execute(self, data: List[Any]) -> Tuple[str, str]:
        user_query = data[0] if len(data) > 1 else None
        prompt = data[1] if len(data) > 1 else data[0]

        print("🤖 正在生成回答...")
        try:
            response = self._call_openai_api(prompt)
            # 清理重复的Answer前缀
            if response.strip().startswith("Answer:"):
                response = response.strip()[7:].strip()
            print("✅ 回答生成完成")
        except Exception as e:
            response = f"[OpenAIGenerator ERROR] {e}"
            print(f"❌ 回答生成失败: {e}")

        self.num += 1

        if self.enable_profile:
            self._save_data_record(user_query, prompt, response)

        return user_query, response

    def __del__(self):
        if hasattr(self, 'enable_profile') and self.enable_profile:
            try:
                self._persist_data_records()
            except:
                pass


class PrivateKnowledgeBuilder:
    """私密信息知识库构建器"""
    
    def __init__(self, collection_name="private_info_knowledge", index_name="private_index"):
        self.collection_name = collection_name
        self.index_name = index_name
        self.knowledge_sentences = [
            "张先生通常将手机放在办公桌右侧的抽屉里，充电线在左侧抽屉。",
            "张先生的车钥匙一般放在玄关柜的小盒子里，备用钥匙在卧室梳妆台。",
            "张先生喜欢在周二和周四的下午3点去附近的咖啡厅工作。",
            "李女士喜欢把钱包放在手提包的内侧拉链袋中，从不放在外层。",
            "李女士的护照和重要证件放在卧室衣柜顶层的蓝色文件夹里。",
            "李女士的手机通常放在卧室床头柜上，但钥匙放在厨房抽屉里。",
            "王经理的办公室钥匙通常挂在腰间的钥匙扣上，备用钥匙在秘书那里。",
            "王经理开会时习惯带着黑色的皮质记事本，里面记录着重要联系人信息。",
            "王经理的手机放在办公桌上，但重要文件锁在保险柜里。",
            "张先生的钱包放在裤子口袋里，李女士的证件在抽屉中。"
        ]

    def ensure_knowledge_base_exists(self):
        """确保知识库存在，如果不存在则创建"""
        try:
            from sage.service.memory.memory_service import MemoryService
            from sage.utils.embedding_methods.embedding_api import apply_embedding_model
            
            embedding_model = apply_embedding_model("default")
            dim = embedding_model.get_dim()
            memory_service = MemoryService()
            
            collections = memory_service.list_collections()
            if collections["status"] == "success":
                collection_names = [c["name"] for c in collections["collections"]]
                if self.collection_name in collection_names:
                    print(f"✅ 知识库 '{self.collection_name}' 已存在")
                    return True
            
            print(f"🚀 创建私密信息知识库 '{self.collection_name}'...")
            return self._create_knowledge_base(memory_service, embedding_model, dim)
            
        except Exception as e:
            print(f"❌ 检查/创建知识库失败: {e}")
            return False

    def _create_knowledge_base(self, memory_service, embedding_model, dim):
        """创建知识库"""
        collection_result = memory_service.create_collection(
            name=self.collection_name,
            backend_type="VDB",
            description="Private information RAG knowledge base",
            embedding_model=embedding_model,
            dim=dim
        )

        if collection_result["status"] != "success":
            print(f"❌ 创建集合失败: {collection_result['message']}")
            return False

        print("📚 插入知识句子...")
        success_count = 0
        for i, sentence in enumerate(self.knowledge_sentences):
            result = memory_service.insert_data(
                collection_name=self.collection_name,
                text=sentence,
                metadata={"id": i + 1, "topic": "private_info", "type": "knowledge", "source": "manual"}
            )
            if result["status"] == "success":
                success_count += 1

        print(f"✅ 成功插入 {success_count}/{len(self.knowledge_sentences)} 句知识")

        index_result = memory_service.create_index(
            collection_name=self.collection_name,
            index_name=self.index_name,
            description="私密信息检索索引"
        )

        if index_result["status"] != "success":
            print(f"❌ 索引创建失败: {index_result['message']}")
            return False

        print(f"✅ 内存知识库构建完成")
        return True


class PrivateQABatch(BatchFunction):
    """
    私密信息QA批处理数据源：内置私密问题列表
    """
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.counter = 0
        self.questions = [
            "张先生的手机通常放在什么地方？",
            "李女士喜欢把钱包放在哪里？", 
            "王经理的办公室钥匙通常在哪里？",
            "张先生什么时候会去咖啡厅工作？",
            "李女士的重要证件放在什么地方？",
            "王经理开会时通常会带什么？"
        ]

    def execute(self):
        """返回下一个问题，如果没有更多问题则返回None"""
        if self.counter >= len(self.questions):
            print("✅ 所有问题处理完成")
            return None  # 返回None表示批处理完成

        question = self.questions[self.counter]
        print(f"📝 正在处理第 {self.counter + 1}/{len(self.questions)} 个问题: {question}")
        self.counter += 1
        return question


class SafePrivateRetriever(MapFunction):
    """带超时保护的私密信息知识检索器"""
    def __init__(self, config, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.collection_name = config.get("collection_name", "private_info_knowledge")
        self.index_name = config.get("index_name", "private_index")
        self.topk = config.get("ltm", {}).get("topk", 3)
        self.memory_service = None
        self.fallback_knowledge = [
            "张先生通常将手机放在办公桌右侧的抽屉里，充电线在左侧抽屉。",
            "张先生的车钥匙一般放在玄关柜的小盒子里，备用钥匙在卧室梳妆台。",
            "张先生喜欢在周二和周四的下午3点去附近的咖啡厅工作。",
            "李女士喜欢把钱包放在手提包的内侧拉链袋中，从不放在外层。",
            "李女士的护照和重要证件放在卧室衣柜顶层的蓝色文件夹里。",
            "李女士的手机通常放在卧室床头柜上，但钥匙放在厨房抽屉里。",
            "王经理的办公室钥匙通常挂在腰间的钥匙扣上，备用钥匙在秘书那里。",
            "王经理开会时习惯带着黑色的皮质记事本，里面记录着重要联系人信息。",
            "王经理的手机放在办公桌上，但重要文件锁在保险柜里。",
            "张先生的钱包放在裤子口袋里，李女士的证件在抽屉中。"
        ]
        self._init_memory_service()

    def _init_memory_service(self):
        """安全地初始化memory service"""
        def init_service():
            try:
                from sage.service.memory.memory_service import MemoryService
                from sage.utils.embedding_methods.embedding_api import apply_embedding_model
                
                embedding_model = apply_embedding_model("default")
                memory_service = MemoryService()
                
                # 检查集合是否存在
                collections = memory_service.list_collections()
                if collections["status"] == "success":
                    collection_names = [c["name"] for c in collections["collections"]]
                    if self.collection_name in collection_names:
                        return memory_service
                return None
            except Exception as e:
                print(f"初始化memory service失败: {e}")
                return None

        try:
            with ThreadPoolExecutor() as executor:
                future = executor.submit(init_service)
                self.memory_service = future.result(timeout=5)  # 5秒超时
                if self.memory_service:
                    print("Memory service初始化成功")
                else:
                    print("⚠️  Memory service初始化失败，将使用内存检索")
        except TimeoutError:
            print("⚠️  Memory service初始化超时，将使用内存检索")
            self.memory_service = None
        except Exception as e:
            print(f"⚠️  Memory service初始化异常: {e}，将使用内存检索")
            self.memory_service = None

    def _simple_text_search(self, query, topk=3):
        """简单的文本匹配检索"""
        keywords = []
        for keyword in ["张先生", "李女士", "王经理", "手机", "钱包", "钥匙", "咖啡厅", "证件", "记事本"]:
            if keyword in query:
                keywords.append(keyword)
        
        scored_sentences = []
        for sentence in self.fallback_knowledge:
            score = sum(1 for keyword in keywords if keyword in sentence)
            if score > 0:
                scored_sentences.append((sentence, score))
        
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        return [item[0] for item in scored_sentences[:topk]]

    def execute(self, data):
        if not data:
            return None

        query = data

        if self.memory_service:
            try:
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(self._retrieve_real, query)
                    result = future.result(timeout=3)
                    return result
            except (TimeoutError, Exception):
                print(f"🔍 检索异常，使用内存检索: {query}")
                retrieved_texts = self._simple_text_search(query, self.topk)
                print(f"   找到 {len(retrieved_texts)} 条相关信息")
                return (query, retrieved_texts)
        else:
            print(f"🔍 使用内存检索: {query}")
            retrieved_texts = self._simple_text_search(query, self.topk)
            print(f"   找到 {len(retrieved_texts)} 条相关信息")
            return (query, retrieved_texts)

    def _retrieve_real(self, query):
        """真实检索"""
        result = self.memory_service.retrieve_data(
            collection_name=self.collection_name,
            query_text=query,
            topk=self.topk,
            index_name=self.index_name,
            with_metadata=True
        )

        if result['status'] == 'success':
            retrieved_texts = [item.get('text', '') for item in result['results']]
            return (query, retrieved_texts)
        else:
            return (query, [])


def pipeline_run(config: dict) -> None:
    """创建并运行数据处理管道"""
    retriever_config = config.get("retriever", {})
    collection_name = retriever_config.get("collection_name", "private_info_knowledge")
    index_name = retriever_config.get("index_name", "private_index")
    
    kb_builder = PrivateKnowledgeBuilder(collection_name, index_name)
    if not kb_builder.ensure_knowledge_base_exists():
        print("❌ 知识库建立失败，终止程序")
        return
    
    print("✅ 知识库准备完成，开始构建处理管道...")
    
    env = LocalEnvironment()

    (env
        .from_batch(PrivateQABatch, config["source"])
        .map(SafePrivateRetriever, config["retriever"])
        .map(QAPromptor, config["promptor"])
        .map(OpenAIGenerator, config["generator"]["remote"])
        .sink(TerminalSink, config["sink"])
    )

    try:
        print("🚀 开始QA处理...")
        print(f"📊 处理流程: 问题源 → 知识检索 → Prompt构建 → AI生成 → 结果输出")
        print("=" * 60)
        env.submit()
        time.sleep(10)
    except KeyboardInterrupt:
        print("⚠️  测试中断")
    finally:
        print("=" * 60)
        print("🏁 测试结束")
        env.close()


if __name__ == '__main__':
    CustomLogger.disable_global_console_debug()
    load_dotenv(override=False)
    config = load_config("config_batch.yaml")
    pipeline_run(config)