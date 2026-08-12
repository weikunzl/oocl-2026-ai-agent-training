"""读取通用 OpenAI-compatible 环境变量并构造 ChatOpenAI。"""

from __future__ import annotations

from functools import lru_cache

from langchain_openai import ChatOpenAI
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """从 .env / 进程环境加载 LLM_*；不绑定具体供应商。"""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_llm(temperature: float = 0) -> ChatOpenAI:
    """构造可调用的 Chat 模型；缺少 BASE_URL/MODEL 时立刻报错便于现场排障。"""
    s = get_settings()
    missing = [
        name
        for name, value in {
            "LLM_BASE_URL": s.llm_base_url,
            "LLM_MODEL": s.llm_model,
        }.items()
        if not value.strip()
    ]
    if missing:
        raise ValueError(
            f"缺少配置: {', '.join(missing)}。"
            "请复制 .env.example 为 .env 并填写 OpenAI-compatible 入口。"
        )
    return ChatOpenAI(
        model=s.llm_model,
        # 本地不鉴权服务也需要非空占位；云服务请填真实 Key
        api_key=s.llm_api_key or "not-required",
        base_url=s.llm_base_url,
        temperature=temperature,
    )
