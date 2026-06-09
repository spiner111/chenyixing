"""
学业预警知识问答系统 - Gradio Web UI
提供交互式问答界面，支持示例问题一键提问
"""

import gradio as gr
from rag_system import AcademicWarningRAG

# 示例问题
EXAMPLE_QUESTIONS = [
    "学业预警工作由谁负责？",
    "什么情况下会被黄色预警？",
    "红色预警的条件是什么？绩点低于多少算红色预警？",
    "绩点1.7，2门必修不及格会收到什么预警？",
    "如果一学期挂了4门必修课，会收到什么预警？会有哪些措施？",
    "我有3门选修课没过，会预警吗？",
]


def build_ui(rag: AcademicWarningRAG):
    """构建 Gradio Web UI"""

    def chat_fn(question: str, history: list):
        """核心问答处理函数"""
        if not question or not question.strip():
            return history, ""

        try:
            answer, sources = rag.ask_with_sources(question.strip())

            # 构建来源信息
            source_text = ""
            seen = set()
            for j, doc in enumerate(sources[:5], 1):
                p = doc.metadata.get("page", "?")
                if p not in seen:
                    preview = doc.page_content[:80].replace("\n", " ")
                    source_text += f"\n📄[第{p}页] {preview}..."
                    seen.add(p)

            new_history = history + [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer + source_text},
            ]
            return new_history, ""

        except Exception as e:
            new_history = history + [
                {"role": "user", "content": question},
                {"role": "assistant", "content": f"⚠️ 问答出错: {str(e)}"},
            ]
            return new_history, ""

    def make_example_fn(q):
        """创建示例问题点击处理函数"""
        def handler(hist):
            return chat_fn(q, hist)
        return handler

    with gr.Blocks(title="学业预警知识问答系统", theme=gr.themes.Soft()) as demo:
        gr.Markdown(
            """
            # 📚 学业预警知识问答系统
            **基于 LangChain + RAG 技术** | 知识来源：《软件与人工智能学院本科生学业预警实施办法》
            """
        )

        # 状态栏
        status = gr.Textbox(
            label="系统状态",
            value="✅ 系统已就绪，请直接提问！",
            interactive=False,
        )

        with gr.Row():
            clear_btn = gr.Button("🗑️ 清空对话", variant="secondary")

        # 示例问题区域
        gr.Markdown("### 💡 示例问题（点击即可提问）")
        example_btns = []
        for i in range(0, len(EXAMPLE_QUESTIONS), 3):
            with gr.Row():
                for q in EXAMPLE_QUESTIONS[i:i+3]:
                    btn = gr.Button(q, size="sm")
                    example_btns.append((btn, q))

        # 对话区
        chatbot = gr.Chatbot(
            label="问答对话",
            type="messages",
            height=450,
            bubble_full_width=False,
        )

        # 输入区
        with gr.Row():
            msg_input = gr.Textbox(
                label="请输入你的问题",
                placeholder="例如：红色预警的条件是什么？",
                scale=9,
            )
            submit_btn = gr.Button("发送", variant="primary", scale=1)

        # 技术栈说明
        gr.Markdown(
            """
            ---
            ### 🔧 技术栈
            | 模块 | 技术方案 |
            |------|----------|
            | 文档加载 | PyPDFLoader |
            | 文档切分 | RecursiveCharacterTextSplitter (chunk=500, overlap=80) |
            | Embedding | BAAI/bge-small-zh-v1.5 |
            | 向量数据库 | Chroma |
            | 关键词检索 | BM25 |
            | 混合检索 | EnsembleRetriever (加权融合) |
            | 重排序 | Cross-Encoder (BAAI/bge-reranker-base) |
            | 大模型 | Ollama + qwen3 |
            | 界面框架 | Gradio |
            """
        )

        # ---- 事件绑定 ----
        msg_input.submit(fn=chat_fn, inputs=[msg_input, chatbot], outputs=[chatbot, msg_input])
        submit_btn.click(fn=chat_fn, inputs=[msg_input, chatbot], outputs=[chatbot, msg_input])
        clear_btn.click(fn=lambda: [], outputs=[chatbot])

        # 示例按钮绑定
        for btn, q in example_btns:
            btn.click(
                fn=make_example_fn(q),
                inputs=[chatbot],
                outputs=[chatbot, msg_input],
            )

    return demo


if __name__ == "__main__":
    import sys

    # 初始化 RAG 系统
    rag = AcademicWarningRAG(
        pdf_path="data/软件与人工智能学院本科生学业预警实施办法.pdf",
        persist_dir="data/chroma_db",
    )

    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        # 命令行交互模式
        rag.initialize()
        print("\n" + "=" * 60)
        print("  学业预警知识问答系统 (CLI 模式)")
        print("  输入 'quit' 或 'exit' 退出")
        print("=" * 60 + "\n")

        while True:
            q = input("请输入问题: ").strip()
            if q.lower() in ("quit", "exit", "q"):
                print("再见！")
                break
            if not q:
                continue
            answer, sources = rag.ask_with_sources(q)
            print(f"\n>> 回答: {answer}\n")
            print("-" * 40)
    else:
        # Web UI 模式
        rag.initialize()
        demo = build_ui(rag)
        demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
