"""
RAG 诊断脚本：检查向量检索与 AI 问答的衔接问题

运行方式：python diagnose_rag.py
"""

import asyncio
import sys
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.core.rag.vector_store import search_similar, get_vector_store
from app.core.rag.retriever import _format_docs, _search_with_timeout, get_llm
from app.prompts.chat import RAG_PROMPT_TEMPLATE
from langchain_core.prompts import ChatPromptTemplate


async def diagnose_rag():
    print("=" * 60)
    print("RAG 检索诊断工具")
    print("=" * 60)

    # 测试用例：使用常见公考题目提问
    test_questions = [
        "下列选项中，属于言语理解与表达的是",
        "如何解答图形推理题",
        "数量关系中行程问题的解题技巧",
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'─' * 60}")
        print(f"测试 {i}/{len(test_questions)}: {question}")
        print(f"{'─' * 60}")

        # Step 1: 检查向量数据库状态
        print("\n[Step 1] 检查向量数据库...")
        try:
            store = get_vector_store()
            collection = store._collection
            total_count = collection.count()
            print(f"  ✓ 向量数据库集合 '{collection.name}' 中共有 {total_count} 条记录")
            
            if total_count == 0:
                print("  ⚠️ 警告：向量数据库为空！请先上传并解析文档")
                continue
        except Exception as e:
            print(f"  ✗ 向量数据库连接失败: {e}")
            continue

        # Step 2: 执行向量检索
        print("\n[Step 2] 执行向量检索 (k=5)...")
        try:
            sources = await _search_with_timeout(question, k=5)
            print(f"  ✓ 检索到 {len(sources)} 条相关片段")
            
            if not sources:
                print("  ✗ 未检索到任何结果！")
                print("  可能原因:")
                print("    1. 向量数据库中确实没有相关数据")
                print("    2. 相似度阈值太高")
                print("    3. 嵌入模型与数据不匹配")
                continue
            
            # Step 3: 分析检索结果
            print("\n[Step 3] 分析检索结果:")
            for idx, source in enumerate(sources, 1):
                content_preview = source.get("content", "")[:100]
                source_file = source.get("source", "未知")
                similarity = source.get("score", 0)
                chunk_type = source.get("chunk_type", "")
                
                print(f"\n  【片段 {idx}】相似度: {similarity:.4f}")
                print(f"    来源: {source_file}")
                print(f"    类型: {chunk_type}")
                print(f"    内容预览: {content_preview}...")
                
                # 检查内容是否相关
                if similarity < 0.3:
                    print(f"    ⚠️ 相似度较低，可能不相关")
            
            # Step 4: 检查 Prompt 格式化
            print("\n[Step 4] 检查 Prompt 上下文格式化...")
            formatted_context = _format_docs(sources)
            print(f"  ✓ 格式化后的上下文长度: {len(formatted_context)} 字符")
            print(f"  上下文预览 (前 300 字符):")
            print(f"    {formatted_context[:300]}...")
            
            # Step 5: 检查 Prompt 模板
            print("\n[Step 5] 检查 RAG Prompt 模板...")
            prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)
            messages = prompt.format_messages(context=formatted_context, question=question)
            print(f"  ✓ Prompt 构建成功")
            print(f"    系统消息长度: {len(messages[0].content)} 字符")
            print(f"    用户问题: {question}")
            
            # Step 6: 检查 LLM 连接
            print("\n[Step 6] 检查 LLM 连接...")
            try:
                llm = get_llm()
                print(f"  ✓ LLM 配置成功: model={llm.model_name}")
            except Exception as e:
                print(f"  ✗ LLM 连接失败: {e}")
                print("    请检查 .env 文件中的 OPENAI_API_KEY 和 OPENAI_BASE_URL")
                continue
            
            # Step 7: 完整测试（可选，会实际调用 LLM）
            print("\n[Step 7] 是否进行完整 LLM 测试？(y/n)")
            choice = input("  输入: ").strip().lower()
            if choice == 'y':
                print("\n  正在调用 LLM 生成回答...")
                try:
                    chain = prompt | llm
                    response = await chain.ainvoke({"context": formatted_context, "question": question})
                    print(f"\n  ✓ LLM 回答:")
                    print(f"  {'─' * 50}")
                    print(f"  {response.content[:500]}...")
                    print(f"  {'─' * 50}")
                    
                    # 检查回答是否引用了参考资料
                    if "参考资料" in response.content or "来源" in response.content:
                        print("\n  ✓ 回答引用了参考资料（RAG 工作正常）")
                    elif "非来自知识库" in response.content:
                        print("\n  ⚠️ 回答声明非来自知识库")
                        print("    说明：检索到的片段内容与问题不匹配")
                    else:
                        print("\n  ⚠️ 回答未明显引用参考资料")
                        print("    可能原因：Prompt 模板需要优化")
                        
                except Exception as e:
                    print(f"  ✗ LLM 调用失败: {e}")
            else:
                print("\n  跳过完整 LLM 测试")

        except Exception as e:
            print(f"  ✗ 检索失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(diagnose_rag())
