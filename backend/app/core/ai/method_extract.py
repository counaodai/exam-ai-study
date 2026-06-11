import asyncio
import json
import logging
from typing import Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings
from app.prompts.method import METHOD_GENERATION_PROMPT

logger = logging.getLogger(__name__)

METHOD_LLM_TIMEOUT = 45


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        openai_api_key=settings.OPENAI_API_KEY,
        openai_api_base=settings.OPENAI_BASE_URL,
        temperature=0.3,
        max_tokens=4096,
    )


def _parse_llm_json(text: str) -> dict[str, Any]:
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        json_str = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        json_str = text[start:end].strip()
    else:
        json_str = text.strip()

    return json.loads(json_str)


def _build_default_result(module_name: str) -> dict[str, Any]:
    return {
        "method_name": f"{module_name}解题方法",
        "recognition": {
            "title": "识别特征",
            "content": f"识别{module_name}相关题目的关键特征",
        },
        "steps": [
            {
                "step": 1,
                "title": "审题",
                "description": "仔细阅读题目，提取关键信息",
                "example": "",
            },
            {
                "step": 2,
                "title": "分析",
                "description": "分析题目考查的知识点和解题方向",
                "example": "",
            },
            {
                "step": 3,
                "title": "解答",
                "description": "运用方法和技巧进行解答",
                "example": "",
            },
        ],
        "traps": [
            {
                "trap": "审题不仔细，遗漏关键条件",
                "solution": "养成标记关键词的习惯",
            },
        ],
        "quick_tips": ["仔细审题，标记关键信息", "排除法辅助验证"],
        "key_formulas": [],
        "summary": f"{module_name}题目需要系统的方法和大量的练习来掌握",
    }


async def extract_method(
    module_name: str,
    questions: list[dict[str, str]],
) -> dict[str, Any]:
    questions_text = ""
    for i, q in enumerate(questions, 1):
        questions_text += f"\n### 题目 {i}\n{q.get('content', '')}\n"
        if q.get("answer"):
            questions_text += f"答案：{q['answer']}\n"
        if q.get("explanation"):
            questions_text += f"解析：{q['explanation']}\n"

    prompt = METHOD_GENERATION_PROMPT.format(
        module_name=module_name,
        questions_text=questions_text,
    )

    try:
        llm = _get_llm()
        messages = [
            SystemMessage(content="你是一位专业的公考培训专家，擅长总结解题方法论。请严格按照 JSON 格式输出。"),
            HumanMessage(content=prompt),
        ]
        response = await asyncio.wait_for(
            llm.ainvoke(messages),
            timeout=METHOD_LLM_TIMEOUT,
        )
        result = _parse_llm_json(response.content)
        logger.info(f"方法论生成成功: {result.get('method_name', '未知')}")
        return result
    except asyncio.TimeoutError:
        logger.error(f"方法论 LLM 超时（{METHOD_LLM_TIMEOUT}s）")
        return _build_default_result(module_name)
    except json.JSONDecodeError as e:
        logger.error(f"方法论 LLM 输出 JSON 解析失败: {e}")
        return _build_default_result(module_name)
    except Exception as e:
        logger.error(f"方法论生成失败: {e}")
        return _build_default_result(module_name)
