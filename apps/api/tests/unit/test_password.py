"""비밀번호 해싱 및 검증 유닛 테스트"""
import pytest

from src.domain.user.service import hash_password, check_password


class TestPasswordHashing:
    """비밀번호 해싱 테스트"""

    def test_hash_password_returns_string(self):
        """해싱된 비밀번호가 문자열로 반환되는지 확인"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_different_from_original(self):
        """해싱된 비밀번호가 원본과 다른지 확인"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password

    def test_hash_password_produces_different_hashes(self):
        """같은 비밀번호도 매번 다른 해시 생성 (salt)"""
        password = "test_password_123"

        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2  # salt로 인해 매번 다른 해시

    def test_hash_password_with_special_characters(self):
        """특수문자 포함 비밀번호 해싱"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_with_unicode(self):
        """유니코드 비밀번호 해싱"""
        password = "비밀번호123"
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_hash_password_with_empty_string(self):
        """빈 문자열 해싱"""
        password = ""
        hashed = hash_password(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0


class TestPasswordVerification:
    """비밀번호 검증 테스트"""

    def test_check_password_correct(self):
        """올바른 비밀번호 검증 성공"""
        password = "correct_password"
        hashed = hash_password(password)

        result = check_password(hashed, password)

        assert result is True

    def test_check_password_incorrect(self):
        """잘못된 비밀번호 검증 실패"""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = hash_password(password)

        result = check_password(hashed, wrong_password)

        assert result is False

    def test_check_password_case_sensitive(self):
        """비밀번호 대소문자 구분"""
        password = "Password123"
        hashed = hash_password(password)

        assert check_password(hashed, "Password123") is True
        assert check_password(hashed, "password123") is False
        assert check_password(hashed, "PASSWORD123") is False

    def test_check_password_with_special_characters(self):
        """특수문자 포함 비밀번호 검증"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)

        assert check_password(hashed, password) is True
        assert check_password(hashed, "P@ssw0rd!#$%^&*()X") is False

    def test_check_password_with_unicode(self):
        """유니코드 비밀번호 검증"""
        password = "비밀번호123"
        hashed = hash_password(password)

        assert check_password(hashed, password) is True
        assert check_password(hashed, "비밀번호124") is False

    def test_check_password_whitespace_matters(self):
        """공백 포함 비밀번호 검증"""
        password = "pass word"
        hashed = hash_password(password)

        assert check_password(hashed, "pass word") is True
        assert check_password(hashed, "password") is False
        assert check_password(hashed, "pass  word") is False

    def test_check_password_empty_string(self):
        """빈 문자열 검증"""
        password = ""
        hashed = hash_password(password)

        assert check_password(hashed, "") is True
        assert check_password(hashed, " ") is False
