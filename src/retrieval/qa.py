from __future__ import annotations

from dataclasses import dataclass
import re

from langchain_core.messages import HumanMessage

from core.config import Settings
from retrieval.index import LocalEmbeddingIndex, SearchResult
from retrieval.llm import build_llm


@dataclass(frozen=True)
class AnswerResult:
    question: str
    answer: str
    retrieved_doc_ids: list[str]
    retrieved_contexts: list[str]
    retrieved_titles: list[str]


def answer_question(question: str, settings: Settings, index: LocalEmbeddingIndex, top_k: int | None = None) -> AnswerResult:
    title_match = re.search(r"'([^']+)'", question)
    exact = index.lookup(title_match.group(1)) if title_match else None
    retrieved = index.search(question, top_k=top_k)
    
    if exact:
        exact_result = SearchResult(
            paper_id=exact["paper_id"],
            title=exact["title"],
            score=1.0,
            content=exact["content"],
            metadata=exact["metadata"],
        )
        deduped = [exact_result] + [item for item in retrieved if item.paper_id != exact_result.paper_id]
        retrieved = deduped[: (top_k or settings.top_k)]
        
    if not retrieved:
        answer = "I don't know from the indexed corpus."
    else:
        llm = build_llm(settings=settings, temperature=0.0)
        
        context_parts = []
        for i, item in enumerate(retrieved):
            meta = item.metadata
            part = (
                f"--- Document {i+1} ---\n"
                f"Title: {meta.get('title', 'N/A')}\n"
                f"Authors: {meta.get('authors_joined', 'N/A')}\n"
                f"Published Date: {meta.get('published', 'N/A')}\n"
                f"Summary: {item.content}"
            )
            context_parts.append(part)
        
        context_str = "\n\n".join(context_parts)
        
        prompt = f"""
You are an expert AI research assistant. Your task is to answer the user's question accurately based ONLY on the provided context documents.
Do not use any external knowledge. If the answer cannot be found in the context, say "I don't know from the indexed corpus."

Context Documents:
{context_str}

Question: {question}

Answer concisely and accurately based on the context above.
""".strip()

        response = llm.invoke([HumanMessage(content=prompt)])
        answer = getattr(response, "content", str(response)).strip()

    return AnswerResult(
        question=question,
        answer=answer,
        retrieved_doc_ids=[item.paper_id for item in retrieved],
        retrieved_contexts=[item.content for item in retrieved],
        retrieved_titles=[item.title for item in retrieved],
    )
