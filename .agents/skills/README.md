# 📚 SKILL — Hospital-AI Skills Library

Thư mục này chứa các **Skill** (tài liệu hướng dẫn kỹ thuật) được tùy chỉnh
riêng cho dự án `hospital-ai`. Mỗi Skill là một bộ best practices, code patterns
và checklist để phát triển và mở rộng hệ thống.

---

## 🗂️ Danh sách Skills đã cài

| Skill | Mô tả | Áp dụng cho |
|-------|--------|-------------|
| [`fastapi-pro`](./fastapi-pro/SKILL.md) | FastAPI async patterns, dependency injection, error handling | Tất cả `routers/*.py` |
| [`rag-implementation`](./rag-implementation/SKILL.md) | Tích hợp RAG với FAISS + Gemini Embeddings | `routers/ai.py`, `rag_service.py` |
| [`pydantic-models-py`](./pydantic-models-py/SKILL.md) | Multi-model Pydantic pattern (Create/Update/Response) | `schemas.py` |
| [`llm-prompt-optimize`](./llm-prompt-optimize/SKILL.md) | Tối ưu System Prompt, Guardrails y tế, giảm hallucination | `routers/ai.py` |
| [`gemini-api-integration`](./gemini-api-integration/SKILL.md) | Gemini API: retry logic, streaming, safety settings | `routers/ai.py` |

---

## 🚀 Cách sử dụng

Khi làm việc với một phần của dự án, **đọc Skill tương ứng trước**:

```
Thêm endpoint mới    → Đọc fastapi-pro/SKILL.md
Tích hợp RAG         → Đọc rag-implementation/SKILL.md
Thêm schema mới      → Đọc pydantic-models-py/SKILL.md
Cải thiện AI prompt  → Đọc llm-prompt-optimize/SKILL.md
Fix Gemini API lỗi   → Đọc gemini-api-integration/SKILL.md
```

---

## 📁 Cấu trúc dự án liên quan

```
hospital-ai/
├── SKILL/                          ← Skills library (thư mục này)
│   ├── fastapi-pro/
│   ├── rag-implementation/
│   ├── pydantic-models-py/
│   ├── llm-prompt-optimize/
│   └── gemini-api-integration/
├── routers/
│   ├── ai.py          ← Liên quan: rag, llm-prompt, gemini, fastapi
│   ├── admin.py       ← Liên quan: fastapi-pro, pydantic
│   ├── auth.py        ← Liên quan: fastapi-pro
│   ├── benh_nhans.py  ← Liên quan: fastapi-pro, pydantic
│   ├── lich_khams.py  ← Liên quan: fastapi-pro, pydantic
│   ├── phieu_khams.py ← Liên quan: fastapi-pro, pydantic
│   └── hoa_dons.py    ← Liên quan: fastapi-pro, pydantic
├── schemas.py         ← Liên quan: pydantic-models-py
├── models.py
├── database.py
└── main.py
```

---

## 📝 Ghi chú

- Tất cả Skills đã được tùy chỉnh cho **bối cảnh y tế** của dự án
- Code examples trong Skills dùng tiếng Việt cho comment và biến tên
- Guardrails y tế (**không chẩn đoán, không kê thuốc**) được nhấn mạnh trong mọi AI Skill
- Cập nhật Skills khi có thay đổi kiến trúc lớn
