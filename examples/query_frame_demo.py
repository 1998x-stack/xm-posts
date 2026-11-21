"""A deliberately small, deterministic Query Understanding contract demo."""
from __future__ import annotations

from dataclasses import dataclass
import json


@dataclass(frozen=True)
class QueryFrame:
    raw_query: str
    intent: str
    entities: tuple[str, ...]
    constraints: tuple[str, ...]
    unresolved: tuple[str, ...]

    @property
    def needs_clarification(self) -> bool:
        return bool(self.unresolved)


def parse_query_demo(raw_query: str) -> QueryFrame:
    """Parse a tiny supported vocabulary; abstain outside that vocabulary."""
    if not raw_query.strip():
        raise ValueError("raw_query must not be empty")

    text = raw_query.casefold()
    intent = (
        "research_search"
        if "paper" in text or "论文" in raw_query
        else "unknown"
    )

    entities: list[str] = []
    if "llm inference" in text or "大模型推理" in raw_query:
        entities.append("LLM inference")
    if "kv cache" in text or "kv缓存" in raw_query:
        entities.append("KV Cache")

    constraints: list[str] = []
    unresolved: list[str] = []
    if "recent" in text or "近期" in raw_query:
        constraints.append("time:recent")
        unresolved.append("recent 的时间窗口尚未定义")

    if "reduce" in text and "memory" in text:
        constraints.append("objective:reduce_memory")

    if intent == "unknown":
        unresolved.append("意图超出本演示规则覆盖范围")

    return QueryFrame(
        raw_query=raw_query,
        intent=intent,
        entities=tuple(entities),
        constraints=tuple(constraints),
        unresolved=tuple(unresolved),
    )


if __name__ == "__main__":
    example = (
        "Find recent papers about efficient LLM inference, "
        "especially methods that reduce KV cache memory."
    )
    frame = parse_query_demo(example)
    print(json.dumps(frame.__dict__, ensure_ascii=False, indent=2))
    print("needs_clarification:", frame.needs_clarification)
