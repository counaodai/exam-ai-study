METHOD_GENERATION_PROMPT = """你是一位资深公考培训专家。请根据以下{module_name}分类下的题目，总结出一套系统的解题方法论。

## 题目列表
{questions_text}

## 输出要求
请严格按照以下 JSON 格式输出，不要输出其他内容：

```json
{{
  "method_name": "方法论名称（如：工程问题万能解法）",
  "recognition": {{
    "title": "识别特征",
    "content": "如何快速识别这类题目（关键词、题型特征等）"
  }},
  "steps": [
    {{
      "step": 1,
      "title": "步骤标题",
      "description": "详细描述这一步的操作",
      "example": "结合题目的具体示例"
    }}
  ],
  "traps": [
    {{
      "trap": "常见陷阱描述",
      "solution": "避免陷阱的方法"
    }}
  ],
  "quick_tips": [
    "速记技巧1",
    "速记技巧2"
  ],
  "key_formulas": [
    "关键公式或规律1",
    "关键公式或规律2"
  ],
  "summary": "方法论总结（一段话概括核心思路）"
}}
```

## 注意事项
1. steps 数组至少包含 3 个步骤，最多 6 个
2. traps 至少包含 2 个常见陷阱
3. quick_tips 至少包含 2 个速记技巧
4. 所有内容必须基于提供的题目，不要编造
5. 示例要具体，最好引用题目中的数据
"""
