from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=4000)
    department: str | None = None
    doc_type: str | None = None
    source: str | None = None
    top_k: int | None = Field(default=None, ge=1, le=30)


class Citation(BaseModel):
    source: str
    page: int | None = None
    score: float | None = None
    snippet: str
    metadata: dict


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    used_llm: bool


class IngestResponse(BaseModel):
    source_id: str
    filename: str
    chunks_indexed: int
    metadata: dict


class DocumentSummary(BaseModel):
    source_id: str
    filename: str
    chunks: int
    metadata: dict
