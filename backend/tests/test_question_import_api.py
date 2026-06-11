"""题目导入 API 集成测试"""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestParseAPI:
    """题目解析 API 测试"""

    @pytest.mark.asyncio
    async def test_parse_empty_content(self, client: AsyncClient):
        response = await client.post("/api/questions/parse", json={
            "content": "",
            "format": "plain",
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["questions"]) == 0
        assert len(data["parse_errors"]) > 0

    @pytest.mark.asyncio
    async def test_parse_valid_question(self, client: AsyncClient):
        response = await client.post("/api/questions/parse", json={
            "content": """1. 某公司计划在三个城市开设分公司
A. 方案一
B. 方案二
C. 方案三
D. 方案四
答案：B
解析：本题考查排列组合""",
            "format": "plain",
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["questions"]) >= 1

    @pytest.mark.asyncio
    async def test_parse_blocked_content(self, client: AsyncClient):
        response = await client.post("/api/questions/parse", json={
            "content": "加微信免费领取公考资料",
            "format": "plain",
        })
        assert response.status_code == 200
        data = response.json()
        assert len(data["questions"]) == 0
        assert len(data["parse_errors"]) > 0


class TestCheckDuplicateAPI:
    """去重检查 API 测试"""

    @pytest.mark.asyncio
    async def test_check_duplicate_invalid_mindmap(self, client: AsyncClient):
        response = await client.post("/api/questions/check-duplicate", json={
            "content": "测试题目",
            "mindmap_id": "00000000-0000-0000-0000-000000000000",
        })
        # 思维导图不存在也应该正常返回（不是404）
        assert response.status_code == 200
        data = response.json()
        assert data["is_duplicate"] is False


class TestQuestionListAPI:
    """题目列表 API 测试"""

    @pytest.mark.asyncio
    async def test_get_question_list(self, client: AsyncClient):
        response = await client.get("/api/questions?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert data["page"] == 1
        assert data["page_size"] == 10

    @pytest.mark.asyncio
    async def test_get_question_list_with_keyword(self, client: AsyncClient):
        response = await client.get("/api/questions?keyword=测试")
        assert response.status_code == 200
