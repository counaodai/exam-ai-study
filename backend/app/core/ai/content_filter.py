"""题目内容审核过滤器"""

import re
import logging

logger = logging.getLogger(__name__)

# 敏感词库
BLOCKED_PATTERNS = [
    r'(广告|推广|加微信|扫码|免费领取|点击链接)',
    r'(赌博|博彩|彩票|赌场)',
    r'(色情|淫秽|成人|裸聊)',
    r'(贷款|网贷|借钱|信用卡套现)',
    r'(兼职|刷单|日赚|月入过万)',
]

# 最小题目长度
MIN_QUESTION_LENGTH = 10

# 最大题目长度
MAX_QUESTION_LENGTH = 5000

# 单次最大题目数
MAX_QUESTIONS_PER_BATCH = 50


def validate_question_content(content: str) -> tuple[bool, str | None]:
    """
    审核题目内容。
    返回: (是否通过, 拒绝原因)
    """
    if not content or len(content.strip()) < MIN_QUESTION_LENGTH:
        return False, "题目内容过短，请检查后重试"

    if len(content) > MAX_QUESTION_LENGTH:
        return False, f"题目内容过长（超过{MAX_QUESTION_LENGTH}字符），请拆分后导入"

    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            logger.warning(f"内容审核拦截: 匹配敏感词模式 '{pattern}'")
            return False, "内容包含不适宜信息，无法导入"

    return True, None


def validate_batch_size(count: int) -> tuple[bool, str | None]:
    """验证批量导入数量"""
    if count <= 0:
        return False, "请至少选择一道题目"
    if count > MAX_QUESTIONS_PER_BATCH:
        return False, f"单次最多导入{MAX_QUESTIONS_PER_BATCH}道题目，当前选择了{count}道"
    return True, None


def sanitize_text(content: str) -> str:
    """清理文本：去除HTML标签、脚本标记"""
    content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.IGNORECASE | re.DOTALL)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'javascript\s*:', '', content, flags=re.IGNORECASE)
    return content.strip()
