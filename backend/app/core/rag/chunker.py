import re
import uuid
import logging
from dataclasses import dataclass, field

from app.schemas.document import ChunkType, ChunkMetadata, DocumentChunk

logger = logging.getLogger(__name__)

DEFAULT_CHUNK_SIZE = 500
DEFAULT_CHUNK_OVERLAP = 100

QUESTION_PATTERNS = [
    # 行首题号：1. 1、 1．
    re.compile(r"(?m)^\s*(\d{1,3})[.、．]\s*[A-D\s]", re.MULTILINE),  # 题号紧跟选项（行测常见）
    re.compile(r"(?m)^\s*(\d{1,3})[.、．]\s*", re.MULTILINE),  # 标准题号
    # 括号题号：（1） (1)
    re.compile(r"(?m)^\s*（(\d{1,3})）\s*", re.MULTILINE),
    re.compile(r"(?m)^\s*\((\d{1,3})\)\s*", re.MULTILINE),
    # 第N题：第1题、第二题
    re.compile(r"(?m)^\s*第(\d{1,3})[一二三四五六七八九十百\d]*题[.、：:\s]*", re.MULTILINE),
    re.compile(r"(?m)^\s*第[一二三四五六七八九十百\d]+题[.、：:\s]*", re.MULTILINE),
]

# 选项模式：A. B. C. D.
OPTION_PATTERN = re.compile(r"^[A-D][.、．]\s*", re.MULTILINE)

# 答案/解析标记
ANSWER_PATTERN = re.compile(r"(答案[是为：:]|【解析】|参考答案|正确选项)", re.IGNORECASE)

CHAPTER_PATTERNS = [
    re.compile(r"^第[一二三四五六七八九十\d]+[章篇节部][.、：:\s]*(.*)", re.MULTILINE),
    re.compile(r"^(#{1,3})\s+(.+)", re.MULTILINE),
]

YEAR_PATTERN = re.compile(r"(20\d{2})[年届]")


@dataclass
class RawSection:
    text: str
    page_number: int | None = None
    chapter: str | None = None
    question_number: int | None = None


def _extract_year(text: str) -> str | None:
    match = YEAR_PATTERN.search(text)
    return match.group(1) if match else None


def _detect_chunk_type(text: str) -> ChunkType:
    question_indicators = [
        r"下列.*正确", r"下列.*错误", r"最能.*削弱", r"最能.*加强",
        r"以下.*属于", r"以下.*不属于", r"答案[是为：:]",
        r"【?解析】?", r"[A-D][.、]", r"选择题",
    ]
    for pattern in question_indicators:
        if re.search(pattern, text):
            return ChunkType.QUESTION

    method_indicators = [
        r"解[题方]法", r"技巧", r"步骤", r"方法论",
        r"常用.*公式", r"速算",
    ]
    for pattern in method_indicators:
        if re.search(pattern, text):
            return ChunkType.METHOD

    return ChunkType.KNOWLEDGE


def _split_by_questions(text: str) -> list[RawSection]:
    """按题目分割文本，确保每道题独立成块。
    
    策略：
    1. 找到所有题号位置
    2. 从题号开始，收集到下一题号之前
    3. 清理页眉页脚等噪声
    4. 保留题干、选项、答案、解析
    """
    all_matches: list[tuple[int, int, int | None]] = []

    for pattern in QUESTION_PATTERNS:
        for match in pattern.finditer(text):
            try:
                q_num = int(match.group(1))
                all_matches.append((match.start(), match.end(), q_num))
            except (ValueError, IndexError):
                continue

    if not all_matches:
        return []

    # 去重：如果两个匹配位置太近（< 20 字符），保留前面的
    all_matches.sort(key=lambda x: x[0])
    deduped: list[tuple[int, int, int]] = []
    last_end = -100
    for start, end, q_num in all_matches:
        if start - last_end >= 20:  # 避免重复匹配
            deduped.append((start, end, q_num))
            last_end = end
    
    if not deduped:
        return []

    # 构建题目块
    sections: list[RawSection] = []
    for i, (start, end, q_num) in enumerate(deduped):
        # 从题号开始，到下一题号之前（或文本末尾）
        if i + 1 < len(deduped):
            next_start = deduped[i + 1][0]
            chunk_text = text[start:next_start]
        else:
            chunk_text = text[start:]
        
        # 清理和验证
        cleaned = _clean_question_chunk(chunk_text)
        if cleaned and len(cleaned) >= 20:  # 题目至少 20 字符
            sections.append(RawSection(
                text=cleaned,
                question_number=q_num,
            ))

    return sections


def _clean_question_chunk(text: str) -> str:
    """清理题目 chunk，去除页眉页脚噪声，保留核心内容。"""
    lines = text.split('\n')
    cleaned_lines: list[str] = []
    is_in_question = False
    question_start_idx = -1
    
    for idx, line in enumerate(lines):
        stripped = line.strip()
        
        # 检查是否是题号行
        is_question_header = bool(re.search(r"(?m)^\s*(\d{1,3})[.、．]", stripped))
        
        if is_question_header and not is_in_question:
            is_in_question = True
            question_start_idx = idx
        
        # 保留题号行、选项行、答案/解析行、题干行
        if is_in_question:
            if (stripped and 
                not _is_noise_line(stripped) and
                len(stripped) > 3):  # 保留至少 3 字符的行
                cleaned_lines.append(stripped)
    
    result = '\n'.join(cleaned_lines)
    return result.strip()


def _is_noise_line(line: str) -> bool:
    """判断是否是非噪声行（页眉页脚、页码等）。"""
    # 页码模式：单独的阿拉伯数字或罗马数字
    if re.match(r"^\d+$", line.strip()) and len(line.strip()) <= 3:
        return True
    if re.match(r"^[IVXLC]+$", line.strip()):
        return True
    
    # 常见页眉页脚关键词
    noise_keywords = ["页共", "页，共", "第页", "网友回忆版", "整理", "生成"]
    for keyword in noise_keywords:
        if keyword in line:
            return True
    
    return False


def _split_by_chapters(text: str) -> list[RawSection]:
    all_matches: list[tuple[int, int, str]] = []

    for pattern in CHAPTER_PATTERNS:
        for match in pattern.finditer(text):
            if match.lastindex and match.lastindex >= 1:
                chapter_title = match.group(match.lastindex).strip()
            else:
                chapter_title = match.group(0).strip()
            all_matches.append((match.start(), match.end(), chapter_title))

    if not all_matches:
        return []

    all_matches.sort(key=lambda x: x[0])
    sections: list[RawSection] = []

    for i, (start, end, title) in enumerate(all_matches):
        if i + 1 < len(all_matches):
            next_start = all_matches[i + 1][0]
            chunk_text = text[start:next_start].strip()
        else:
            chunk_text = text[start:].strip()

        if chunk_text and len(chunk_text) > 20:
            sections.append(RawSection(
                text=chunk_text,
                chapter=title,
            ))

    return sections


def _split_by_paragraphs(text: str) -> list[RawSection]:
    paragraphs = re.split(r"\n\s*\n", text)
    sections: list[RawSection] = []

    for para in paragraphs:
        para = para.strip()
        # 关键改进：降低段落最小长度，从 30 降到 15
        if para and len(para) >= 15:
            sections.append(RawSection(text=para))

    return sections


def _split_fixed_length(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[RawSection]:
    sections: list[RawSection] = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = min(start + chunk_size, text_len)

        if end < text_len:
            break_pos = text.rfind("\n", start, end)
            if break_pos > start + chunk_size // 2:
                end = break_pos + 1

        chunk_text = text[start:end].strip()
        if chunk_text:
            sections.append(RawSection(text=chunk_text))

        start = end - overlap
        if start >= text_len:
            break

    return sections


def smart_chunk(
    text: str,
    source: str,
    module: str | None = None,
    page_number: int | None = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[DocumentChunk]:
    if not text.strip():
        return []

    sections = _split_by_questions(text)
    split_strategy = "question"

    if not sections:
        sections = _split_by_chapters(text)
        split_strategy = "chapter"

    if not sections:
        sections = _split_by_paragraphs(text)
        split_strategy = "paragraph"

    if not sections:
        sections = _split_fixed_length(text, chunk_size, chunk_overlap)
        split_strategy = "fixed_length"

    if not sections:
        return []

    logger.info(f"文档 [{source}] 使用 [{split_strategy}] 策略分块，共 {len(sections)} 个分块")

    chunks: list[DocumentChunk] = []
    year = _extract_year(source) or _extract_year(text[:500])

    for section in sections:
        chunk_text = section.text.strip()
        if not chunk_text or len(chunk_text) < 10:
            continue

        chunk_type = _detect_chunk_type(chunk_text)
        chunk_id = str(uuid.uuid4())

        metadata = ChunkMetadata(
            page=section.page_number or page_number,
            chapter=section.chapter,
            question_number=section.question_number,
            year=year,
            tags=[],
        )

        chunks.append(DocumentChunk(
            id=chunk_id,
            content=chunk_text,
            source=source,
            module=module,
            chunk_type=chunk_type,
            metadata=metadata,
        ))

    logger.info(f"文档 [{source}] 最终生成 {len(chunks)} 个有效分块")
    return chunks
