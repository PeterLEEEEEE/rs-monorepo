from typing_extensions import (
    Any,
    AsyncGenerator,
    AsyncIterator,
    Optional,
)

from contextlib import asynccontextmanager

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    WRITES_IDX_MAP,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    PendingWrite,
    get_checkpoint_id,
)


class AsyncPostgresSaver(BaseCheckpointSaver):
    pass