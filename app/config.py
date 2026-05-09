from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Enterprise RAG Knowledge Assistant"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    pinecone_api_key: str = Field(default="", repr=False)
    pinecone_index_name: str = "enterprise-rag"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    pinecone_namespace: str = "default"

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    chunk_size: int = 1000
    chunk_overlap: int = 180

    retrieval_top_k: int = 6
    rerank_top_k: int = 3
    rerank_model: str = ""

    gemini_api_key: str = Field(default="", repr=False)
    gemini_model: str = "gemini-2.5-flash-lite"
    gemini_max_output_tokens: int = 700
    context_char_limit: int = 6000

    openai_api_key: str = Field(default="", repr=False)
    openai_model: str = "gpt-4o-mini"

    allowed_origins: str = "*"

    storage_dir: Path = Path("storage")
    upload_dir: Path = Path("storage/uploads")
    manifest_path: Path = Path("storage/manifest.json")

    @property
    def cors_origins(self) -> list[str]:
        if self.allowed_origins.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    return settings
