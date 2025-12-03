import uuid
from datetime import datetime, timezone
from typing_extensions import Annotated, Optional, Any
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointTuple,
    CheckpointMetadata,
    ChannelVersions
)
from langgraph.checkpoint.serde.base import SerializerProtocol
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from langgraph.checkpoint.mongodb.aio import AsyncMongoDBSaver


class CustomMongoDBSaver(BaseCheckpointSaver):

    conn: AsyncDatabase

    def __init__(self, conn: AsyncDatabase, collection_name: str = "checkpoints"):
        super().__init__()
        self.conn = conn
        self.collection_name = collection_name
        
    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """체크포인트 가져오기"""
        thread_id = config["configurable"]["thread_id"] # conversation id = chatroom id
        checkpoint_id = config["configurable"].get("checkpoint_id")
        
        query = {"thread_id": thread_id}
        if checkpoint_id:
            query["checkpoint_id"] = checkpoint_id
        
        doc = await self.conn[self.collection_name].find_one(
            query,
            sort=[("created_at", -1)]
        )
        
        if not doc:
            return None
            
        try:
            # 체크포인트 역직렬화
            checkpoint = self.serde.loads(doc["checkpoint"])
            
            # parent_config 올바르게 구성
            parent_config = None
            if doc.get("parent_checkpoint_id"):
                parent_config = {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": doc["parent_checkpoint_id"]
                    }
                }
            
            return CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_id": doc["checkpoint_id"]
                    }
                },
                checkpoint=checkpoint,
                metadata=doc.get("metadata", {}),
                parent_config=parent_config
            )
        except Exception as e:
            print(f"Error deserializing checkpoint: {e}")
            return None

    async def aput(
        self, 
        config: RunnableConfig, 
        checkpoint: Checkpoint, 
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """체크포인트 저장"""
        thread_id = config["configurable"]["thread_id"]
        checkpoint_id = checkpoint["id"]

        try:
            # 체크포인트 직렬화
            serialized_checkpoint = self.serde.dumps(checkpoint)
            
            # metadata 안전하게 처리
            clean_metadata = {}
            if metadata:
                for k, v in metadata.items():
                    if k not in ["writes"]:  # writes는 보통 직렬화 불가능
                        try:
                            # 직렬화 가능한지 테스트
                            self.serde.dumps(v)
                            clean_metadata[k] = v
                        except:
                            # 직렬화 불가능한 경우 문자열로 변환
                            clean_metadata[k] = str(v)
            
            doc = {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint_id,
                "parent_checkpoint_id": config["configurable"].get("checkpoint_id"),
                "checkpoint": serialized_checkpoint,
                "metadata": clean_metadata,
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.conn[self.collection_name].insert_one(doc)
            
            return {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_id": checkpoint_id
                }
            }
        except Exception as e:
            print(f"Error saving checkpoint: {e}")
            raise

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None
    ) -> list[CheckpointTuple]:
        """체크포인트 목록 조회"""
        query = {}
        
        if config and "thread_id" in config.get("configurable", {}):
            query["thread_id"] = config["configurable"]["thread_id"]
            
        # before 파라미터 처리
        if before:
            before_checkpoint_id = before.get("configurable", {}).get("checkpoint_id")
            if before_checkpoint_id:
                before_doc = await self.conn[self.collection_name].find_one(
                    {"checkpoint_id": before_checkpoint_id}
                )
                if before_doc:
                    query["created_at"] = {"$lt": before_doc["created_at"]}
        
        cursor = self.conn[self.collection_name].find(
            query,
            sort=[("created_at", -1)],
            limit=limit or 10
        )
        
        results = []
        async for doc in cursor:
            try:
                checkpoint = self.serde.loads(doc["checkpoint"])
                
                parent_config = None
                if doc.get("parent_checkpoint_id"):
                    parent_config = {
                        "configurable": {
                            "thread_id": doc["thread_id"],
                            "checkpoint_id": doc["parent_checkpoint_id"]
                        }
                    }
                
                results.append(CheckpointTuple(
                    config={
                        "configurable": {
                            "thread_id": doc["thread_id"],
                            "checkpoint_id": doc["checkpoint_id"]
                        }
                    },
                    checkpoint=checkpoint,
                    metadata=doc.get("metadata", {}),
                    parent_config=parent_config
                ))
            except Exception as e:
                print(f"Error deserializing checkpoint in list: {e}")
                continue
            
        return results

    # 동기 메서드들 (필수)
    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        raise NotImplementedError("Use async methods")
        
    def list(self, *args, **kwargs) -> list[CheckpointTuple]:
        raise NotImplementedError("Use async methods")
        
    def put(self, *args, **kwargs) -> RunnableConfig:
        raise NotImplementedError("Use async methods")