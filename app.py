import streamlit as st
import sys
import os
from pathlib import Path

# Thêm thư mục src vào PYTHONPATH để import được các module
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from core.config import load_settings
from retrieval.index import LocalEmbeddingIndex
from retrieval.embeddings import MiniLMEmbeddings
from retrieval.qa import answer_question

st.set_page_config(page_title="Team Balerion - Research QA", page_icon="🤖", layout="wide")

@st.cache_resource
def load_rag_components():
    settings = load_settings()
    # Khởi tạo embedder và index
    if not settings.paths.embeddings_json.exists():
        st.error("Không tìm thấy dữ liệu Index. Hãy chạy script/run_phase1.py trước!")
        st.stop()
    
    index = LocalEmbeddingIndex.load(settings)
    return settings, index

st.title("🤖 RAG Agent Demo - Team Balerion")
st.markdown("Hệ thống Hỏi-Đáp AI tự động trích xuất thông tin từ các bài báo khoa học. (Baseline Data)")

with st.spinner("Đang tải cơ sở dữ liệu Vector (ChromaDB)..."):
    settings, index = load_rag_components()

# Khởi tạo chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Chào bạn! Mình có thể giúp gì được về tập tài liệu bài báo khoa học?"}]

# Hiển thị lịch sử chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("contexts"):
            with st.expander("📄 Nguồn tài liệu (Retrieved Contexts)"):
                for i, ctx in enumerate(msg["contexts"]):
                    title = msg["titles"][i] if i < len(msg.get("titles", [])) else "N/A"
                    st.markdown(f"**Tài liệu {i+1}: {title}**")
                    st.caption(ctx)

if prompt := st.chat_input("Ví dụ: Tác giả của bài báo SafeRAG là ai?"):
    # 1. Hiện câu hỏi
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Xử lý câu trả lời
    with st.chat_message("assistant"):
        with st.spinner("Đang đọc tài liệu và suy luận..."):
            try:
                # Gọi hàm QA trong codebase
                result = answer_question(prompt, settings, index)
                
                # Hiển thị kết quả
                st.markdown(result.answer)
                
                # Hiển thị context
                if result.retrieved_contexts:
                    with st.expander("📄 Nguồn tài liệu (Retrieved Contexts)"):
                        for i, ctx in enumerate(result.retrieved_contexts):
                            title = result.retrieved_titles[i] if i < len(result.retrieved_titles) else "N/A"
                            st.markdown(f"**Tài liệu {i+1}: {title}**")
                            st.caption(ctx)
                
                # Lưu vào lịch sử
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": result.answer,
                    "contexts": result.retrieved_contexts,
                    "titles": result.retrieved_titles
                })
            except Exception as e:
                st.error(f"Lỗi: {e}")
