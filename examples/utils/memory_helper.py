"""
Memory service utilities for SAGE examples
提供记忆服务相关的工具函数
"""
from typing import List, Dict, Any
from sage.service.memory.memory_service import MemoryService
from .ui_helper import UIHelper


class MemoryServiceHelper:
    """记忆服务助手类"""
    
    @staticmethod
    def create_memory_service_with_knowledge(
        collection_name: str,
        knowledge_sentences: List[str],
        description: str = "Knowledge base collection"
    ) -> MemoryService:
        """
        创建带有预设知识的记忆服务
        
        Args:
            collection_name: 集合名称
            knowledge_sentences: 知识句子列表
            description: 集合描述
            
        Returns:
            MemoryService实例
        """
        # 创建 memory service 实例
        memory_service = MemoryService()
        
        # 创建集合
        result = memory_service.create_collection(
            name=collection_name,
            backend_type="VDB",
            description=description
        )
        
        if result['status'] == 'success':
            print(UIHelper.format_success("知识库集合创建成功"))
            
            # 预先插入知识句子
            print(UIHelper.format_processing("正在插入知识..."))
            success_count = 0
            
            for i, sentence in enumerate(knowledge_sentences):
                insert_result = memory_service.insert_data(
                    collection_name=collection_name,
                    text=sentence,
                    metadata={
                        "id": i + 1, 
                        "type": "knowledge", 
                        "source": "manual",
                        "date": "2025-07-31"
                    }
                )
                
                if insert_result['status'] == 'success':
                    success_count += 1
                else:
                    print(UIHelper.format_error(f"插入第 {i+1} 条知识失败: {insert_result['message']}"))
            
            print(UIHelper.format_success(f"成功插入 {success_count}/{len(knowledge_sentences)} 条知识"))
            
        else:
            print(UIHelper.format_error(f"创建知识库集合失败: {result['message']}"))
            
        return memory_service


class KnowledgeDatasets:
    """预设知识数据集"""
    
    PRIVATE_INFO_KNOWLEDGE = [
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
    
    PRIVATE_INFO_QUESTIONS = [
        "张先生的手机通常放在什么地方？",
        "李女士喜欢把钱包放在哪里？", 
        "王经理的办公室钥匙通常在哪里？",
        "张先生什么时候会去咖啡厅工作？",
        "李女士的重要证件放在什么地方？"
    ]
    
    @staticmethod
    def get_dataset(name: str) -> Dict[str, Any]:
        """获取指定的数据集"""
        datasets = {
            "private_info": {
                "knowledge": KnowledgeDatasets.PRIVATE_INFO_KNOWLEDGE,
                "questions": KnowledgeDatasets.PRIVATE_INFO_QUESTIONS,
                "collection_name": "private_info_knowledge",
                "description": "Private information RAG knowledge base"
            }
        }
        return datasets.get(name, {})
