import pytest
import sys
import os
from pathlib import Path

# src 경로를 PYTHONPATH에 추가
api_root = Path(__file__).parent.parent
sys.path.insert(0, str(api_root))

# 테스트 환경 설정
os.environ["APP_ENV"] = "test"


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
