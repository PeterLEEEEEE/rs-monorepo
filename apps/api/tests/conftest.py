import pytest
import sys
import os
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# src 경로를 PYTHONPATH에 추가
api_root = Path(__file__).parent.parent
sys.path.insert(0, str(api_root))

# 테스트 환경 설정
os.environ["APP_ENV"] = "test"


@pytest.fixture(autouse=True)
def mock_db_session():
    """
    모든 테스트에서 get_session()을 mock.
    @transactional 데코레이터가 실제 DB 없이 동작하도록 함.
    """
    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.flush = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.execute = AsyncMock()
    mock_session.add = MagicMock()

    with patch("src.db.session.get_session", return_value=mock_session):
        with patch("src.db.transactional.get_session", return_value=mock_session):
            yield mock_session


@pytest.fixture
def jwt_secret():
    """테스트용 JWT secret"""
    return "test_secret_key_for_testing"


@pytest.fixture
def test_user_data():
    """테스트용 사용자 데이터"""
    return {
        "id": 1,
        "email": "test@test.com",
        "username": "testuser",
        "role": "USER",
        "password": "password123",
    }
