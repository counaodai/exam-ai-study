"""
提问有效性校验模块

对用户输入进行多层过滤，拦截无效提问（纯社交问候、与公考无关的闲聊等），
防止无效数据污染思维导图和统计分析。
"""
import asyncio
import json
import logging
import re
from dataclasses import dataclass, field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings

logger = logging.getLogger(__name__)

VALIDATOR_LLM_TIMEOUT = 15

# ============================================================
# 第一层：基础关键词/模式过滤规则
# ============================================================

# 纯社交问候/告别/闲聊关键词（命中任一即判定无效）
INVALID_GREETING_PATTERNS = [
    # 问候
    r"^(你好|您好|hi|hello|嗨|哈喽|早上好|中午好|下午好|晚上好|晚安|早安|午安)[\s!！。.]*$",
    r"^(在吗|在不在|在不|有人在吗|有人吗)[\s?？。.]*$",
    # 告别
    r"^(再见|拜拜|bye|bye-bye|88|回头见|下次见|先这样|就这样)[\s!！。.]*$",
    # 感谢
    r"^(谢谢|感谢|多谢|thanks|thank you|3q|三克油)[\s!！。.]*$",
    # 闲聊
    r"^(你叫什么|你是谁|你是什么|你是机器人|你是AI|你是人工智能)[\s?？。.]*$",
    r"^(今天天气|天气怎么样|今天几号|今天星期几|现在几点)",
    r"^(讲个笑话|说个笑话|讲个故事|唱首歌|放首歌)[\s!！。.]*$",
    r"^(你吃饭了吗|你睡了吗|你累不累|你困不困)[\s?？。.]*$",
    r"^(你能做什么|你有什么功能|你会什么|你懂什么)[\s?？。.]*$",
    # 纯表情/无意义字符
    r"^[😀-🙏👀-👃👆-👇👌-🙏🚀-🛿]+$",
    r"^[\s!！。.,，?？;；:：、""''（）()【】\[\]{}]+$",
]

# 纯数字/单字/过短输入
MIN_VALID_QUESTION_LENGTH = 3  # 最少有效字符数（去除标点空格后）

# 与公考明显无关的话题关键词（命中后需要 LLM 二次确认）
SUSPICIOUS_TOPICS = [
    "天气", "吃饭", "睡觉", "游戏", "电影", "音乐", "明星", "娱乐",
    "股票", "基金", "比特币", "区块链", "炒币",
    "恋爱", "表白", "分手", "相亲",
    "外卖", "快递", "购物", "淘宝", "京东",
    "王者荣耀", "吃鸡", "原神", "LOL", "DOTA",
    "旅游", "景点", "酒店", "机票",
    "做饭", "菜谱", "食谱",
    "健身", "减肥", "瑜伽",
]


def _strip_punctuation(text: str) -> str:
    """去除标点符号和空白字符"""
    return re.sub(r"[\s!！。.,，?？;；:：、""''（）()【】\[\]{}《》<>/\\|@#$%^&*+=~`\-_]", "", text)


def check_by_keyword_rules(question_text: str) -> tuple[bool, str]:
    """
    第一层：关键词/模式过滤
    返回 (is_invalid, reason)
    """
    text = question_text.strip()

    # 空输入
    if not text:
        return True, "输入为空"

    # 纯表情/无意义字符
    if re.match(r"^[\s!！。.,，?？;；:：、""''（）()【】\[\]{}<>/\\|@#$%^&*+=~`\-_😀-🙏👀-👃👆-👇👌-🙏🚀-🛿]+$", text):
        return True, "输入为纯符号或表情"

    # 过短输入
    stripped = _strip_punctuation(text)
    if len(stripped) < MIN_VALID_QUESTION_LENGTH:
        return True, f"输入过短（有效字符数: {len(stripped)}）"

    # 纯数字
    if re.match(r"^[\d\s.]+$", stripped):
        return True, "输入为纯数字"

    # 社交问候/告别/闲聊模式匹配
    for pattern in INVALID_GREETING_PATTERNS:
        if re.match(pattern, text, re.IGNORECASE):
            return True, "纯社交问候/闲聊，与公考学习无关"

    return False, ""


# ============================================================
# 第二层：LLM 语义相关性校验
# ============================================================

RELEVANCE_CHECK_PROMPT = """你是一个公考学习助手的输入过滤器。请判断用户的输入是否与"公务员考试/事业单位考试学习"相关。

## 判定标准
- **有效提问**：与公考科目（行测、申论、面试）学习相关的问题，包括但不限于：
  - 具体题目求解（言语理解、数量关系、判断推理、资料分析、常识判断）
  - 解题方法、技巧、策略咨询
  - 考试政策、备考规划咨询
  - 知识点概念解释
  - 对之前题目答案的追问或澄清

- **无效提问**：与公考学习完全无关的内容，包括但不限于：
  - 纯社交问候（你好、再见、谢谢）
  - 日常闲聊（天气、吃饭、娱乐八卦）
  - 其他领域的专业问题（编程、医学、金融投资等）
  - 无意义的测试输入

## 用户输入
{question_text}

## 输出要求
请严格按以下JSON格式输出，不要输出其他内容：
```json
{{
  "is_valid": true,
  "reason": "判定理由简述"
}}
```

注意：
- is_valid 为 true 表示与公考学习相关，false 表示无关
- 对于边界情况（如"考试"相关但不确定是否公考），倾向于判定为有效
"""


@dataclass
class ValidationResult:
    """校验结果"""
    is_valid: bool
    reason: str
    filter_layer: str = ""  # "keyword" | "llm" | "passed"
    suggested_action: str = ""  # "block" | "warn" | "allow"


async def validate_question(question_text: str) -> ValidationResult:
    """
    多层校验入口：先关键词过滤，再 LLM 语义校验

    返回 ValidationResult：
    - is_valid=True: 有效提问，可进入后续分类流程
    - is_valid=False: 无效提问，应拦截
    """
    # 第一层：关键词/模式过滤
    is_invalid, reason = check_by_keyword_rules(question_text)
    if is_invalid:
        logger.info(f"关键词过滤拦截无效提问: {reason} | 输入: {question_text[:50]}")
        return ValidationResult(
            is_valid=False,
            reason=reason,
            filter_layer="keyword",
            suggested_action="block",
        )

    # 第二层：检查是否包含可疑话题关键词
    text_lower = question_text.lower()
    has_suspicious = any(topic in text_lower for topic in SUSPICIOUS_TOPICS)

    # 如果包含可疑话题，使用 LLM 进行语义相关性校验
    if has_suspicious:
        try:
            llm_result = await _llm_relevance_check(question_text)
            if not llm_result.get("is_valid", True):
                reason = llm_result.get("reason", "LLM 判定与公考学习无关")
                logger.info(f"LLM 语义校验拦截无效提问: {reason} | 输入: {question_text[:50]}")
                return ValidationResult(
                    is_valid=False,
                    reason=reason,
                    filter_layer="llm",
                    suggested_action="block",
                )
        except Exception as e:
            logger.warning(f"LLM 语义校验异常，放行: {e}")
            # LLM 异常时放行，避免阻塞正常提问

    # 通过所有校验
    return ValidationResult(
        is_valid=True,
        reason="通过关键词和语义校验",
        filter_layer="passed",
        suggested_action="allow",
    )


async def _llm_relevance_check(question_text: str) -> dict:
    """调用 LLM 进行语义相关性判断"""
    try:
        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.0,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
        )

        prompt = ChatPromptTemplate.from_template(RELEVANCE_CHECK_PROMPT)
        chain = prompt | llm | StrOutputParser()

        result_text = await asyncio.wait_for(
            chain.ainvoke({"question_text": question_text}),
            timeout=VALIDATOR_LLM_TIMEOUT,
        )

        json_match = re.search(r"\{[^{}]+\}", result_text, re.DOTALL)
        if not json_match:
            logger.warning(f"LLM 相关性校验结果无法解析: {result_text}")
            return {"is_valid": True, "reason": "解析失败，默认放行"}

        return json.loads(json_match.group())

    except asyncio.TimeoutError:
        logger.warning(f"LLM 相关性校验超时（{VALIDATOR_LLM_TIMEOUT}s），默认放行")
        return {"is_valid": True, "reason": "校验超时，默认放行"}
    except Exception as e:
        logger.warning(f"LLM 相关性校验失败: {e}，默认放行")
        return {"is_valid": True, "reason": f"校验异常: {str(e)}，默认放行"}
