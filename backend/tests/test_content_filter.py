"""内容审核过滤器单元测试"""

import pytest
from app.core.ai.content_filter import (
    validate_question_content,
    validate_batch_size,
    sanitize_text,
)


class TestValidateQuestionContent:
    """题目内容审核测试"""

    def test_valid_content(self):
        ok, reason = validate_question_content("这是一道关于数量关系的题目，请计算甲乙两人的速度")
        assert ok is True
        assert reason is None

    def test_too_short_content(self):
        ok, reason = validate_question_content("短")
        assert ok is False
        assert "过短" in reason

    def test_empty_content(self):
        ok, reason = validate_question_content("")
        assert ok is False

    def test_too_long_content(self):
        ok, reason = validate_question_content("x" * 5001)
        assert ok is False
        assert "过长" in reason

    def test_blocked_ad_content(self):
        ok, reason = validate_question_content("加微信xxx免费领取公考资料")
        assert ok is False
        assert "不适宜" in reason

    def test_blocked_gambling_content(self):
        ok, reason = validate_question_content("赌博网站推荐，请访问")
        assert ok is False
        assert "不适宜" in reason

    def test_blocked_loan_content(self):
        ok, reason = validate_question_content("无抵押贷款请联系")
        assert ok is False

    def test_max_length_boundary(self):
        ok, reason = validate_question_content("x" * 5000)
        assert ok is True


class TestValidateBatchSize:
    """批量导入数量验证测试"""

    def test_valid_batch_size(self):
        ok, reason = validate_batch_size(10)
        assert ok is True

    def test_zero_count(self):
        ok, reason = validate_batch_size(0)
        assert ok is False

    def test_exceed_max(self):
        ok, reason = validate_batch_size(51)
        assert ok is False
        assert "50" in reason

    def test_max_boundary(self):
        ok, reason = validate_batch_size(50)
        assert ok is True


class TestSanitizeText:
    """文本清理测试"""

    def test_remove_html_tags(self):
        result = sanitize_text("<p>题目内容</p>")
        assert "<p>" not in result
        assert "题目内容" in result

    def test_remove_script_tags(self):
        result = sanitize_text("<script>alert('xss')</script>题目内容")
        assert "alert" not in result
        assert "题目内容" in result

    def test_remove_style_tags(self):
        result = sanitize_text("<style>body{color:red}</style>题目内容")
        assert "body" not in result
        assert "题目内容" in result

    def test_remove_javascript_protocol(self):
        result = sanitize_text("javascript:void(0)题目内容")
        assert "javascript" not in result.lower()
        assert "题目内容" in result
