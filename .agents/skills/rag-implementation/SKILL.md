---
name: rag-implementation
description: >
  Tích hợp RAG (Retrieval-Augmented Generation) vào hospital-ai.
  Dùng để tra cứu kiến thức y tế, giao thức điều trị, và hướng dẫn từ tài liệu nội bộ
  thay vì chỉ dựa vào kiến thức tổng quát của LLM.
source: antigravity/personal
date_added: "2026-08-17"
project: hospital-ai
---

# RAG Implementation — Hospital-AI

## Khi nào dùng skill này

- Tích hợp tìm kiếm ngữ nghĩa trong dữ liệu bệnh án
- Cho phép AI tra cứu phác đồ điều trị nội bộ
- Xây dựng chatbot Q&A dựa trên tài liệu y tế
- Cải thiện độ chính xác của AI Summary bằng context cụ thể

## Kiến trúc RAG cho Hospital-AI

```
Bệnh nhân hỏi/Bác sĩ truy vấn
         │
         ▼
[Embedding Model] ──→ Vector (query)
         │
         ▼
[Vector DB / FAISS] ──→ Top-K chunks (phác đồ, bệnh án tương tự)
         │
         ▼
[Prompt Builder] ──→ Context + Query
         │
         ▼
[Gemini 1.5 Flash] ──→ Câu trả lời có căn cứ
```

## Cài đặt Dependencies

```bash
pip install langchain langchain-google-genai faiss-cpu sentence-transformers
```

## Implementation trong routers/ai.py

### Bước 1: Khởi tạo Vector Store

```python
# rag_service.py — tạo file mới
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

# Dùng Gemini Embeddings (cùng API key)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

def create_vector_store(documents: list[str]) -> FAISS:
    """Tạo FAISS vector store từ danh sách tài liệu y tế."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,      # Phù hợp với văn bản y tế
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.create_documents(documents)
    return FAISS.from_documents(chunks, embeddings)

# Load sẵn khi khởi động app
vector_store = None

def get_vector_store() -> FAISS:
    global vector_store
    if vector_store is None:
        # Load từ disk (đã index trước)
        vector_store = FAISS.load_local("data/medical_kb", embeddings)
    return vector_store
```

### Bước 2: RAG-Enhanced AI Summary

```python
# Trong routers/ai.py — thay thế call_llm_api
async def generate_rag_summary(benh_nhan_data: dict, history: str) -> str:
    """
    RAG-augmented summary: Tra cứu phác đồ + lịch sử → tóm tắt chính xác hơn.
    """
    vs = get_vector_store()
    
    # Tìm kiếm context y tế liên quan
    query = f"{benh_nhan_data.get('tien_su_benh', '')} {history}"
    relevant_docs = vs.similarity_search(query, k=3)
    context = "\n".join([doc.page_content for doc in relevant_docs])
    
    prompt = f"""
[NGỮ CẢNH Y TẾ THAM KHẢO]:
{context}

[THÔNG TIN BỆNH NHÂN (ẨN DANH)]:
{benh_nhan_data}

[LỊCH SỬ KHÁM]:
{history}

Dựa vào ngữ cảnh y tế trên, hãy tóm tắt hành chính hồ sơ bệnh nhân.
TUYỆT ĐỐI KHÔNG tự chẩn đoán hay kê đơn thuốc.
"""
    return await call_llm_api(prompt)
```

### Bước 3: Indexing Tài liệu Y tế

```python
# scripts/index_medical_docs.py
import os
from pathlib import Path

def index_documents():
    """Index các file PDF/TXT y tế vào vector store."""
    docs_path = Path("data/medical_docs")
    documents = []
    
    for file in docs_path.glob("*.txt"):
        with open(file, encoding="utf-8") as f:
            documents.append(f.read())
    
    vs = create_vector_store(documents)
    vs.save_local("data/medical_kb")
    print(f"✅ Đã index {len(documents)} tài liệu y tế")

if __name__ == "__main__":
    index_documents()
```

## Cấu trúc thư mục đề xuất

```
hospital-ai/
├── data/
│   ├── medical_docs/     ← Tài liệu y tế nguồn (.txt, .pdf)
│   └── medical_kb/       ← Vector store đã index (FAISS)
├── scripts/
│   └── index_medical_docs.py
├── rag_service.py        ← RAG service module
└── routers/
    └── ai.py             ← Sử dụng rag_service
```

## Quality Checklist

- [ ] Embedding model đã được chọn (Gemini embedding-001)
- [ ] Vector DB đã configure (FAISS local)
- [ ] Chunking strategy phù hợp (500 tokens, overlap 50)
- [ ] Retrieval hoạt động (top-3 relevant docs)
- [ ] LLM tích hợp với context RAG
- [ ] Guardrails giữ nguyên (không chẩn đoán, không kê thuốc)

## Giới hạn

- FAISS là local vector DB, phù hợp cho prototype. Production → dùng Chroma hoặc Weaviate
- Chất lượng RAG phụ thuộc vào chất lượng tài liệu y tế nguồn
- Cần đánh giá retrieval accuracy trước khi deploy
