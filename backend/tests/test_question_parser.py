"""题目解析引擎单元测试"""

import pytest
from app.core.ai.question_parser import (
    _preprocess_text,
    _split_questions,
    _parse_single_question,
    parse_questions,
)


class TestPreprocessText:
    """文本预处理测试"""

    def test_remove_html_tags(self):
        result = _preprocess_text("<p>这是一道题目</p>")
        assert result == "这是一道题目"

    def test_unify_newlines(self):
        result = _preprocess_text("第一行\r\n第二行\r第三行")
        assert "\r" not in result

    def test_strip_whitespace(self):
        result = _preprocess_text("  题目内容  \n")
        assert result == "题目内容"


class TestSplitQuestions:
    """多题拆分测试"""

    def test_split_by_number(self):
        content = "1. 第一道题目\nA. 选项A\nB. 选项B\n2. 第二道题目\nA. 选项A\nB. 选项B"
        blocks = _split_questions(content)
        assert len(blocks) == 2
        assert "第一道题目" in blocks[0]
        assert "第二道题目" in blocks[1]

    def test_split_by_chinese_number(self):
        content = "第一题 题目内容很长\n第二题 题目内容也很长"
        blocks = _split_questions(content)
        assert len(blocks) == 2

    def test_single_question_no_split(self):
        content = "这是一道没有题号的题目"
        blocks = _split_questions(content)
        assert len(blocks) == 1
        assert blocks[0] == content


class TestParseSingleQuestion:
    """单题解析测试"""

    def test_parse_complete_question(self):
        text = """1. 某公司计划在三个城市开设分公司
A. 方案一
B. 方案二
C. 方案三
D. 方案四
答案：B
解析：本题考查排列组合的基本原理"""
        result = _parse_single_question(text)
        assert result is not None
        assert "某公司计划" in result.content
        assert result.options is not None
        assert len(result.options) == 4
        assert result.answer == "B"
        assert result.explanation is not None
        assert "排列组合" in result.explanation
        assert result.parse_confidence >= 0.7

    def test_parse_question_no_options(self):
        text = """1. 下列说法正确的是哪一项
答案：C"""
        result = _parse_single_question(text)
        assert result is not None
        assert result.answer == "C"
        assert result.options is None or len(result.options) == 0

    def test_parse_question_no_answer(self):
        text = """1. 某题目内容较长
A. 选项A
B. 选项B"""
        result = _parse_single_question(text)
        assert result is not None
        assert result.answer is None
        assert result.options is not None
        assert len(result.options) == 2

    def test_parse_too_short_content(self):
        text = "1. 短"
        result = _parse_single_question(text)
        assert result is None

    def test_parse_with_bracket_options(self):
        text = """1. 这是一道测试题目
（A）选项A
（B）选项B
答案：A"""
        result = _parse_single_question(text)
        assert result is not None
        assert result.options is not None
        assert "A" in result.options
        assert result.options["A"] == "选项A"


class TestParseQuestionsAsync:
    """异步解析主函数测试"""

    @pytest.mark.asyncio
    async def test_parse_empty_content(self):
        questions, errors = await parse_questions("")
        assert len(questions) == 0
        assert len(errors) > 0

    @pytest.mark.asyncio
    async def test_parse_valid_content(self):
        content = """1. 某公司计划在三个城市开设分公司
A. 方案一
B. 方案二
C. 方案三
D. 方案四
答案：B
解析：本题考查排列组合"""
        questions, errors = await parse_questions(content)
        assert len(questions) >= 1
        assert questions[0].content is not None

    @pytest.mark.asyncio
    async def test_parse_multiple_questions(self):
        content = """1. 第一道题目内容较长
A. 选项A
B. 选项B
答案：A

2. 第二道题目内容较长
A. 选项A
B. 选项B
答案：B"""
        questions, errors = await parse_questions(content)
        assert len(questions) >= 1
