"""最小 LangGraph：单 LLM 节点 + 简单条件边，跑通一次 Agent 调用链路。"""

from __future__ import annotations

from typing import Annotated, Literal, TypedDict

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from hello_agent.config import get_llm


class HelloState(TypedDict):
    messages: Annotated[list, add_messages]
    ok: bool


def call_llm(state: HelloState) -> dict:
    """唯一业务节点：调用 LLM，写回消息与是否成功。"""
    llm = get_llm()
    messages = state.get("messages") or [
        HumanMessage(content="用一句话打个招呼，说明你是环境验证探针。")
    ]
    resp = llm.invoke(messages)
    content = str(getattr(resp, "content", "") or "").strip()
    return {"messages": [resp], "ok": bool(content)}


def route_after_llm(state: HelloState) -> Literal["success", "fallback"]:
    """条件边：有有效回复 → success，否则 → fallback。"""
    return "success" if state.get("ok") else "fallback"


def success_node(state: HelloState) -> dict:
    """成功分支：保持状态，便于在 Studio 里看见路径。"""
    return {}


def fallback_node(state: HelloState) -> dict:
    """失败分支：写入提示，方便现场排查 Key / 模型。"""
    return {
        "messages": [
            AIMessage(
                content="[fallback] LLM 未返回有效内容，请检查 API Key / 模型配置。"
            )
        ],
        "ok": False,
    }


_builder = StateGraph(HelloState)
_builder.add_node("call_llm", call_llm)
_builder.add_node("success", success_node)
_builder.add_node("fallback", fallback_node)
_builder.add_edge(START, "call_llm")
_builder.add_conditional_edges(
    "call_llm",
    route_after_llm,
    {"success": "success", "fallback": "fallback"},
)
_builder.add_edge("success", END)
_builder.add_edge("fallback", END)

# langgraph.json / Studio 入口：编译后的图
graph = _builder.compile()


def run_hello(
    prompt: str = "用一句话打个招呼，说明你是环境验证探针。",
) -> dict:
    """供 notebook / 命令行直接 invoke 一次完整链路。"""
    return graph.invoke(
        {"messages": [HumanMessage(content=prompt)], "ok": False}
    )
