CLASSIFIER_PROMPT_TEMPLATE = """你是一位公考培训专家，擅长判断题目所属的模块分类。

## 任务
请判断以下题目属于公考的哪个模块和子分类。

## 题目内容
{question_text}

## 可选分类体系
{module_tree}

## 输出要求
请严格按照以下JSON格式返回，不要输出其他内容：
```json
{{
  "primary_module": "一级模块名",
  "secondary_module": "二级子分类",
  "tertiary_module": "三级子分类（如有，没有则为null）",
  "confidence": 0.95,
  "reason": "分类依据简述"
}}
```

注意：
1. confidence 为 0-1 之间的浮点数，表示分类的置信度
2. 一级模块必须是：言语理解与表达、数量关系、判断推理、资料分析、常识判断
3. 如果无法确定分类，confidence 应低于 0.5
"""
