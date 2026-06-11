"""题目内容解析引擎 — 规则优先 + LLM兜底"""

import re
import json
import logging
from enum import Enum

from app.schemas.question_import import ParsedQuestionItem

logger = logging.getLogger(__name__)


class QuestionFormat(str, Enum):
    PLAIN = "plain"
    MARKDOWN = "markdown"


# 规则1：按题号分隔多道题目
QUESTION_SEPARATOR_PATTERNS = [
    r'(?:^|\n)\s*(\d+)[\.、．)\s]+',
    r'(?:^|\n)\s*第[一二三四五六七八九十\d]+题',
]

# 规则2：识别选项行
OPTION_PATTERNS = [
    r'^[A-J][\.、．)\s]+',
    r'^[（(][A-J][）)]',
]

# 规则3：识别答案行
ANSWER_PATTERNS = [
    r'(?:答案|正确选项|参考答案)[：:]\s*([A-J]+)',
    r'^答案[：:]\s*([A-J]+)',
]

# 规则4：识别解析行
EXPLANATION_PATTERNS = [
    r'(?:解析|答案解析|解题思路|分析)[：:]',
    r'^解析[：:]',
]

# 最小题目长度
MIN_QUESTION_LENGTH = 5


def _preprocess_text(content: str) -> str:
    """预处理：去除HTML标签、统一换行符、去除首尾空白"""
    content = re.sub(r'<[^>]+>', '', content)
    content = content.replace('\r\n', '\n').replace('\r', '\n')
    content = content.strip()
    return content


def _split_questions(content: str) -> list[str]:
    """按题号正则匹配分割为单题文本块"""
    # 先尝试数字题号
    pattern = r'(?:^|\n)\s*(\d+)[\.、．)\s]+'
    matches = list(re.finditer(pattern, content))

    if not matches:
        # 尝试中文题号
        pattern = r'(?:^|\n)\s*第[一二三四五六七八九十\d]+题'
        matches = list(re.finditer(pattern, content))

    if not matches:
        return [content]

    blocks = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        blocks.append(content[start:end].strip())

    return blocks if blocks else [content]


def _parse_single_question(text: str) -> ParsedQuestionItem | None:
    """规则解析单道题目"""
    lines = text.split('\n')
    if not lines:
        return None

    # 提取题干：第一行（去除题号前缀）
    stem = lines[0].strip()
    stem = re.sub(r'^\s*\d+[\.、．)\s]+', '', stem)

    # 提取选项
    options: dict[str, str] = {}
    option_start_idx = -1
    for i, line in enumerate(lines[1:], 1):
        for pat in OPTION_PATTERNS:
            m = re.match(pat, line.strip())
            if m:
                if option_start_idx == -1:
                    option_start_idx = i
                key = re.search(r'[A-J]', line.strip())
                if key:
                    val = re.sub(pat, '', line.strip()).strip()
                    options[key.group()] = val
                break
        else:
            if option_start_idx != -1:
                break

    # 如果题干太短，尝试合并后续非选项行
    if len(stem) < MIN_QUESTION_LENGTH and option_start_idx > 1:
        stem = ' '.join(l.strip() for l in lines[:option_start_idx])
        stem = re.sub(r'^\s*\d+[\.、．)\s]+', '', stem)

    # 提取答案
    answer = None
    answer_line_idx = -1
    for i, line in enumerate(lines):
        for pat in ANSWER_PATTERNS:
            m = re.search(pat, line.strip())
            if m:
                answer = m.group(1).strip()
                answer_line_idx = i
                break
        if answer:
            break

    # 提取解析
    explanation = None
    for i, line in enumerate(lines):
        for pat in EXPLANATION_PATTERNS:
            if re.search(pat, line.strip()):
                expl_lines = []
                for j in range(i, len(lines)):
                    l = lines[j].strip()
                    if j == i:
                        l = re.sub(pat, '', l).strip()
                    if l:
                        expl_lines.append(l)
                explanation = '\n'.join(expl_lines)
                break
        if explanation:
            break

    if not stem or len(stem) < MIN_QUESTION_LENGTH:
        return None

    confidence = 0.5
    if options:
        confidence += 0.15
    if answer:
        confidence += 0.2
    if explanation:
        confidence += 0.15

    return ParsedQuestionItem(
        content=stem,
        options=options if options else None,
        answer=answer,
        explanation=explanation,
        parse_confidence=min(confidence, 1.0),
    )


async def _parse_by_llm(content: str) -> list[ParsedQuestionItem]:
    """LLM兜底解析"""
    try:
        from langchain_openai import ChatOpenAI
        from app.config import settings

        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_BASE_URL,
            temperature=0.1,
        )

        prompt = f"""请将以下文本解析为结构化题目。对于每道题目，提取题干、选项（A/B/C/D）、答案、解析。
返回JSON数组格式，每个元素包含 content, options, answer, explanation 字段。
如果无法识别为题目，返回空数组。

文本内容：
{content}

请只返回JSON，不要包含其他文字。"""

        import asyncio
        response = await asyncio.wait_for(
            llm.ainvoke(prompt),
            timeout=30.0,
        )

        text = response.content if hasattr(response, 'content') else str(response)
        # 清理可能的markdown代码块标记
        text = re.sub(r'^```(?:json)?\s*', '', text.strip())
        text = re.sub(r'\s*```$', '', text.strip())

        data = json.loads(text)
        if not isinstance(data, list):
            data = [data]

        results = []
        for item in data:
            results.append(ParsedQuestionItem(
                content=item.get('content', ''),
                options=item.get('options'),
                answer=item.get('answer'),
                explanation=item.get('explanation'),
                parse_confidence=0.7,
            ))
        return results

    except Exception as e:
        logger.warning(f"LLM解析失败: {e}")
        return []


async def parse_questions(
    content: str,
    format: str = "plain",
) -> tuple[list[ParsedQuestionItem], list[dict]]:
    """
    解析粘贴的题目文本，识别题目结构。
    策略：规则优先 + LLM兜底。

    返回: (解析成功的题目列表, 解析错误列表)
    """
    content = _preprocess_text(content)

    if not content:
        return [], [{"error": "内容为空", "message": "请粘贴题目内容后再识别"}]

    # 多题拆分
    blocks = _split_questions(content)

    questions: list[ParsedQuestionItem] = []
    errors: list[dict] = []

    for i, block in enumerate(blocks):
        parsed = _parse_single_question(block)
        if parsed and parsed.parse_confidence >= 0.5:
            questions.append(parsed)
        else:
            errors.append({
                "index": i,
                "content_preview": block[:100],
                "message": "未能识别有效的题目结构",
                "confidence": parsed.parse_confidence if parsed else 0.0,
            })

    # 如果规则解析全部失败，尝试LLM兜底
    if not questions and blocks:
        logger.info("规则解析全部失败，尝试LLM兜底解析")
        llm_results = await _parse_by_llm(content)
        if llm_results:
            questions = llm_results
            errors = []

    return questions, errors
