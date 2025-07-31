import os
import json
import time
import requests
from typing import Any, List, Tuple
from sage.core.function.map_function import MapFunction

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

        try:
            response = self._call_openai_api(prompt)
        except Exception as e:
            response = f"[OpenAIGenerator ERROR] {e}"

        self.num += 1

        if self.enable_profile:
            self._save_data_record(user_query, prompt, response)

        # 只在调试模式下打印详细信息
        # print(f"[{self.__class__.__name__}] Response: {response}")
        return user_query, response

    def __del__(self):
        if hasattr(self, 'enable_profile') and self.enable_profile:
            try:
                self._persist_data_records()
            except:
                pass
