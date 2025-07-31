"""
OpenAI Compatible Generator - 重构版
支持 OpenAI-Compatible / VLLM / DashScope 等端点的生成器
"""
import os
import json
import time
import requests
from typing import Any, List, Tuple, Optional
from sage.core.function.map_function import MapFunction


class OpenAIGenerator(MapFunction):
    """
    生成节点：调用 OpenAI-Compatible / VLLM / DashScope 等端点
    重构版本，更加模块化和可维护
    """

    def __init__(self, config: dict, enable_profile=False, **kwargs):
        super().__init__(**kwargs)
        self.config = config
        self.enable_profile = enable_profile
        self.num = 1
        self.session = requests.Session()
        
        # 初始化profile相关
        if self.enable_profile:
            self._init_profile_storage()

    def _init_profile_storage(self):
        """初始化profile数据存储"""
        if hasattr(self.ctx, 'env_base_dir') and self.ctx.env_base_dir:
            self.data_base_path = os.path.join(self.ctx.env_base_dir, ".sage_states", "generator_data")
        else:
            self.data_base_path = os.path.join(os.getcwd(), ".sage_states", "generator_data")
        os.makedirs(self.data_base_path, exist_ok=True)
        self.data_records = []

    def _prepare_headers(self) -> dict:
        """准备请求头"""
        headers = {"Content-Type": "application/json"}
        if self.config.get("api_key"):
            headers["Authorization"] = f"Bearer {self.config['api_key']}"
        return headers

    def _prepare_payload(self, prompt: str) -> dict:
        """准备请求载荷"""
        # 确保 prompt 是字符串
        if not isinstance(prompt, str):
            prompt = str(prompt)

        return {
            "model": self.config["model_name"],
            "messages": [{"role": "user", "content": prompt}],
            "temperature": float(self.config.get("temperature", 0.7)),
            "max_tokens": int(self.config.get("max_tokens", 1024)),
        }

    def _call_openai_api(self, prompt: str) -> str:
        """调用OpenAI兼容的API"""
        url = self.config["base_url"].rstrip("/") + "/chat/completions"
        headers = self._prepare_headers()
        payload = self._prepare_payload(prompt)

        try:
            resp = self.session.post(url, headers=headers, json=payload, timeout=60)
            
            if resp.status_code != 200:
                error_msg = f"API返回错误: {resp.status_code} {resp.text}"
                print(f"===> {error_msg}")
                resp.raise_for_status()
            
            data = resp.json()
            return data["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            return f"[API请求错误] {str(e)}"
        except (KeyError, IndexError) as e:
            return f"[响应解析错误] {str(e)}"
        except Exception as e:
            return f"[未知错误] {str(e)}"

    def _save_data_record(self, query: str, prompt: str, response: str):
        """保存数据记录"""
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
        """持久化数据记录"""
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
            print(f"保存数据记录失败: {e}")

    def _extract_input(self, data: Any) -> Tuple[Optional[str], str]:
        """从输入数据中提取用户查询和提示词"""
        if isinstance(data, (list, tuple)) and len(data) >= 2:
            user_query = data[0]
            prompt = data[1]
        elif isinstance(data, (list, tuple)) and len(data) == 1:
            user_query = None
            prompt = data[0]
        else:
            user_query = None
            prompt = str(data) if data else ""
        
        return user_query, prompt

    def execute(self, data: Any) -> Tuple[Optional[str], str]:
        """执行生成任务"""
        user_query, prompt = self._extract_input(data)
        
        if not prompt:
            return user_query, "[错误] 空提示词"

        # 调用API生成回答
        response = self._call_openai_api(prompt)
        
        # 保存记录（如果启用）
        if self.enable_profile:
            self._save_data_record(user_query or "", prompt, response)

        self.num += 1
        return user_query, response

    def __del__(self):
        """析构函数，确保数据持久化"""
        if hasattr(self, 'enable_profile') and self.enable_profile:
            try:
                self._persist_data_records()
            except:
                pass
