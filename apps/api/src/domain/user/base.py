from typing_extensions import Any, Generic, Type, TypeVar
from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from dependency_injector.wiring import Provide, inject


ModelType = TypeVar("ModelType")

class BaseAlchemyRepository(Generic[ModelType]):
    """
    Base class for Alchemy repositories.
    """
    def __init__(
        self,
        model: Type[ModelType],
        session_factory,
    ):
        self.model = model
        self.session_factory = session_factory

    async def get_by_id(self, id: int) -> ModelType | None:
        if hasattr(self.model, "id"):
            async with self.session_factory() as session:
                query = select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
                result = await session.execute(query)
                return result.scalar_one_or_none()
        return None
    
    async def list_all(self) -> list[ModelType]:
        async with self.session_factory() as session:
            query = select(self.model)
            result = await session.execute(query)
            return result.scalars().all()

    async def add(self, obj: ModelType) -> ModelType:
        async with self.session_factory() as session:
            session.add(obj)
            await session.commit()
            await session.refresh(obj)
            return obj

    async def delete(self, obj: ModelType) -> None:
        async with self.session_factory() as session:
            if not obj:
                return
            await session.delete(obj)
            await session.commit()


class BaseService:    
    def __init__(self, repository: BaseAlchemyRepository):
        self.repository = repository