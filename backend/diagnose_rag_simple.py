"""
RAG 深度诊断脚本：检查 Prompt 中 context 是否被正确传递

问题排查清单：
1. 向量数据库中是否有数据
2. 检索是否返回了结果
3. _format_docs 是否正确格式化
4. Prompt 模板中 {context} 是否被填充
5. LLM 是否真正使用了上下文
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.core.rag.vector_store import search_similar
from app.core.rag.retriever import _format_docs
from app.prompts.chat import RAG_PROMPT_TEMPLATE


def check_rag_context_flow():
    print("=" * 70)
    print("RAG 上下文传递深度诊断")
    print("=" * 70)

    # 测试问题
    test_question = "如何解答图形推理题"
    print(f"\n测试问题: {test_question}\n")

    # Step 1: 检索向量数据库
    print("【Step 1】检索向量数据库...")
    sources = search_similar(test_question, k=5)
    print(f"  检索到 {len(sources)} 条结果")
    
    if not sources:
        print("  ✗ 未检索到任何结果！RAG 无法工作")
        print("  解决方案：")
        print("    1. 上传 PDF 文档到系统")
        print("    2. 等待文档解析完成")
        print("    3. 确认 chroma_data 目录下有数据")
        return
    
    print(f"  ✓ 检索成功")
    for idx, src in enumerate(sources, 1):
        print(f"    [{idx}] 相似度: {src['score']:.4f} | 来源: {src['source'][:50]}")

    # Step 2: 格式化上下文
    print("\n【Step 2】格式化上下文...")
    formatted_context = _format_docs(sources)
    print(f"  格式化后长度: {len(formatted_context)} 字符")
    print(f"  格式化后行数: {len(formatted_context.split(chr(10)))} 行")
    
    if not formatted_context or len(formatted_context) < 10:
        print("  ✗ 上下文为空或过短！")
        return
    print("  ✓ 上下文格式化成功")

    # Step 3: 检查 Prompt 模板
    print("\n【Step 3】检查 RAG Prompt 模板...")
    print(f"  模板内容:")
    print(f"  {'─' * 70}")
    for line_num, line in enumerate(RAG_PROMPT_TEMPLATE.split('\n'), 1):
        print(f"    {line_num:2d}. {line}")
    print(f"  {'─' * 70}")
    
    # 检查模板是否有 {context} 和 {question} 占位符
    has_context = "{context}" in RAG_PROMPT_TEMPLATE
    has_question = "{question}" in RAG_PROMPT_TEMPLATE
    
    print(f"\n  模板检查:")
    print(f"    {'✓' if has_context else '✗'} 包含 {{context}} 占位符: {has_context}")
    print(f"    {'✓' if has_question else '✗'} 包含 {{question}} 占位符: {has_question}")
    
    if not has_context or not has_question:
        print("  ✗ Prompt 模板缺少必要的占位符！")
        return

    # Step 4: 模拟 Prompt 构建
    print("\n【Step 4】模拟 Prompt 构建...")
    final_prompt = RAG_PROMPT_TEMPLATE.format(
        context=formatted_context,
        question=test_question
    )
    
    print(f"  最终 Prompt 长度: {len(final_prompt)} 字符")
    print(f"  最终 Prompt 行数: {len(final_prompt.split(chr(10)))} 行")
    
    # 检查 context 是否被正确填充
    context_position = final_prompt.find("【片段1】")
    if context_position >= 0:
        print(f"  ✓ 上下文已正确填充到 Prompt")
        print(f"    上下文开始位置: 第 {context_position} 字符")
        print(f"    上下文预览:")
        context_preview = final_prompt[context_position:context_position + 200]
        for preview_line in context_preview.split('\n'):
            print(f"      {preview_line}")
    else:
        print(f"  ✗ 上下文未正确填充！")
        return

    # Step 5: 检查 LLM 接收的输入
    print("\n【Step 5】检查 LLM 接收的输入...")
    print(f"  用户问题在 Prompt 中的位置:")
    question_position = final_prompt.find(test_question)
    if question_position >= 0:
        print(f"    问题位置: 第 {question_position} 字符")
        print(f"    问题周围上下文:")
        start = max(0, question_position - 50)
        end = min(len(final_prompt), question_position + len(test_question) + 50)
        context_before = final_prompt[start:question_position]
        context_after = final_prompt[question_position + len(test_question):end]
        print(f"      前置: ...{context_before}")
        print(f"      问题: {test_question}")
        print(f"      后置: {context_after}...")
    
    # Step 6: 总结
    print("\n" + "=" * 70)
    print("诊断总结")
    print("=" * 70)
    print()
    print("  ✓ 向量检索: 返回了 {} 条结果".format(len(sources)))
    print("  ✓ 上下文格式化: 生成了 {} 字符的上下文".format(len(formatted_context)))
    print("  ✓ Prompt 模板: 包含 {context} 和 {question} 占位符")
    print("  ✓ 最终 Prompt: 生成了 {} 字符的完整 Prompt".format(len(final_prompt)))
    print()
    print("  下一步:")
    print("    1. 如果检索结果不相关 → 检查嵌入模型和分块质量")
    print("    2. 如果 LLM 回答未引用资料 → 检查 Prompt 模板中的指令")
    print("    3. 如果 LLM 回答不准确 → 增加检索数量或优化分块策略")
    print()


if __name__ == "__main__":
    check_rag_context_flow()
