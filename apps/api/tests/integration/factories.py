"""테스트 데이터 생성용 Factory"""
import factory
import uuid

from src.domain.user.models import User
from src.domain.user.service import hash_password


class UserFactory(factory.Factory):
    """User 테스트 데이터 Factory"""

    class Meta:
        model = User

    # id는 DB가 자동 생성하도록 지정하지 않음
    username = factory.LazyFunction(lambda: f"testuser_{uuid.uuid4().hex[:8]}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@test.com")
    hashed_password = factory.LazyFunction(lambda: hash_password("password123"))
    role = "USER"
    is_active = True


class AdminUserFactory(UserFactory):
    """Admin User Factory"""

    username = factory.Sequence(lambda n: f"admin{n}")
    role = "ADMIN"


class InactiveUserFactory(UserFactory):
    """비활성화된 User Factory"""

    is_active = False
