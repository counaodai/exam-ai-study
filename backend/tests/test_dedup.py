"""去重逻辑单元测试"""

import pytest
from app.core.mindmap.dedup import normalize_text


class TestNormalizeText:
    """文本标准化测试"""

    def test_remove_whitespace(self):
        result = normalize_text("题目  内容  \n 测试")
        assert " " not in result
        assert "\n" not in result

    def test_unify_punctuation(self):
        result = normalize_text("题目．内容，测试：结果")
        assert "．" not in result
        assert "，" not in result
        assert "：" not in result

    def test_unify_brackets(self):
        result = normalize_text("（题目）内容")
        assert "（" not in result
        assert "）" not in result

    def test_case_insensitive(self):
        result = normalize_text("ABC题目")
        assert result == "abc题目"

    def test_identical_after_normalization(self):
        a = "题目  内容\nA. 选项"
        b = "题目内容\nA．选项"
        assert normalize_text(a) == normalize_text(b)
