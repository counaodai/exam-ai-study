import asyncio
import json
import logging
import re
from dataclasses import dataclass
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.prompts.classifier import CLASSIFIER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

CLASSIFIER_LLM_TIMEOUT = 30

CLASSIFICATION_RULES = {
    "言语理解与表达": {
        "逻辑填空": ["填入", "最恰当", "依次填入", "词语", "填入画横线处", "选词填空", "依次填入下列"],
        "片段阅读": ["这段文字", "主旨", "意在说明", "概括", "这段话", "主要强调", "意在强调", "旨在说明", "意在表达"],
        "语句表达": ["语句排序", "排序", "语序", "衔接", "下文推断", "填入横线处", "排列组合"],
    },
    "数量关系": {
        "数学运算": [
            "甲乙", "甲单独", "乙单独", "合做", "合作", "若干", "至少", "最多", "总共",
            "公里", "小时", "速度", "距离", "工作效率", "工程问题", "完成", "需要多少天",
            "需要多少小时", "甲乙丙", "利润", "折扣", "成本", "售价", "打折", "概率",
            "排列", "组合", "比例", "分数", "百分比", "年龄", "鸡兔同笼", "追及",
            "相遇", "路程", "时间", "甲地", "乙地", "出发", "到达", "剩余", "分给",
        ],
        "数字推理": ["数列", "下一个数", "空缺项", "规律", "填入空缺", "数字推理"],
    },
    "判断推理": {
        "图形推理": ["图形", "下一个图形", "规律", "折叠", "展开", "旋转", "对称", "平移"],
        "定义判断": ["符合定义", "不属于", "属于", "最符合", "最不符合", "定义判断", "以下哪项"],
        "类比推理": ["之于", "相当于", "类比", "逻辑关系", "类比推理"],
        "逻辑判断": ["削弱", "质疑", "反驳", "加强", "支持", "最能支持", "前提", "假设", "必要条件", "结论推出", "逻辑判断"],
    },
    "资料分析": {
        "_keywords": [
            "增长率", "比重", "倍数", "同比", "环比", "百分比", "增长量", "基期", "现期",
            "同比增长", "同比增长率", "同比下降", "环比增长", "环比下降", "增长最快",
            "增长最慢", "比重变化", "平均数", "中位数",
        ],
    },
    "常识判断": {
        "_keywords": [
            "下列说法正确", "下列说法错误", "常识", "下列哪项", "正确的是", "错误的是",
            "下列正确", "下列错误", "以下说法", "以下哪项", "下列说法中",
        ],
    },
}


@dataclass
class ClassificationResult:
    primary_module: str
    secondary_module: str | None = None
    tertiary_module: str | None = None
    confidence: float = 0.0
    method: str = "rule"
    reason: str = ""


def classify_by_rules(question_text: str) -> ClassificationResult | None:
    text_lower = question_text.lower()

    for module_name, sub_rules in CLASSIFICATION_RULES.items():
        if isinstance(sub_rules, dict):
            if "_keywords" in sub_rules:
                keywords = sub_rules["_keywords"]
                match_count = sum(1 for kw in keywords if kw in text_lower)
                if match_count > 0:
                    confidence = min(0.5 + match_count * 0.15, 0.9)
                    matched = [kw for kw in keywords if kw in text_lower]
                    return ClassificationResult(
                        primary_module=module_name,
                        confidence=confidence,
                        method="rule",
                        reason=f"命中关键词：{', '.join(matched)}",
                    )
            else:
                for sub_name, keywords in sub_rules.items():
                    match_count = sum(1 for kw in keywords if kw in text_lower)
                    if match_count > 0:
                        confidence = min(0.5 + match_count * 0.15, 0.9)
                        matched = [kw for kw in keywords if kw in text_lower]
                        return ClassificationResult(
                            primary_module=module_name,
                            secondary_module=sub_name,
                            confidence=confidence,
                            method="rule",
                            reason=f"命中关键词：{', '.join(matched)}",
                        )

    return None


def _format_module_tree() -> str:
    return """一级模块：言语理解与表达、数量关系、判断推理、资料分析、常识判断
二级分类：
- 言语理解与表达：逻辑填空、片段阅读、语句表达
- 数量关系：数学运算、数字推理
- 判断推理：图形推理、定义判断、类比推理、逻辑判断
- 资料分析：增长率、增长量、比重、倍数、平均数、综合分析
- 常识判断：政治、法律、经济、历史、地理、科技、文学"""


async def classify_by_llm(question_text: str) -> ClassificationResult:
    try:
        llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.1,
            openai_api_key=settings.OPENAI_API_KEY,
            openai_api_base=settings.OPENAI_BASE_URL,
        )

        prompt = ChatPromptTemplate.from_template(CLASSIFIER_PROMPT_TEMPLATE)
        chain = prompt | llm | StrOutputParser()

        result_text = await asyncio.wait_for(
            chain.ainvoke({
                "question_text": question_text,
                "module_tree": _format_module_tree(),
            }),
            timeout=CLASSIFIER_LLM_TIMEOUT,
        )

        json_match = re.search(r'\{[^{}]+\}', result_text, re.DOTALL)
        if not json_match:
            logger.warning(f"LLM 分类结果无法解析 JSON: {result_text}")
            return ClassificationResult(
                primary_module="未分类",
                confidence=0.0,
                method="llm",
                reason="LLM 返回格式异常",
            )

        data = json.loads(json_match.group())
        return ClassificationResult(
            primary_module=data.get("primary_module", "未分类"),
            secondary_module=data.get("secondary_module"),
            tertiary_module=data.get("tertiary_module"),
            confidence=float(data.get("confidence", 0.5)),
            method="llm",
            reason=data.get("reason", ""),
        )
    except asyncio.TimeoutError:
        logger.error(f"LLM 分类超时（{CLASSIFIER_LLM_TIMEOUT}s）")
        return ClassificationResult(
            primary_module="未分类",
            confidence=0.0,
            method="llm",
            reason="LLM 分类超时",
        )
    except Exception as e:
        logger.error(f"LLM 分类失败: {e}")
        return ClassificationResult(
            primary_module="未分类",
            confidence=0.0,
            method="llm",
            reason=f"LLM 分类异常: {str(e)}",
        )


async def classify_question(question_text: str) -> ClassificationResult:
    rule_result = classify_by_rules(question_text)
    if rule_result and rule_result.confidence >= 0.6:
        logger.info(f"规则分类命中: {rule_result.primary_module} - {rule_result.secondary_module}")
        return rule_result

    logger.info("规则未命中或置信度不足，调用 LLM 分类")
    llm_result = await classify_by_llm(question_text)
    return llm_result
