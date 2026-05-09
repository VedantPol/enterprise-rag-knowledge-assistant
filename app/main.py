from functools import lru_cache
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import Settings, get_settings
from app.rag import RagService
from app.schemas import AskRequest, AskResponse, DocumentSummary, IngestResponse


@lru_cache
def get_rag_service() -> RagService:
    return RagService(get_settings())


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(static_dir / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": settings.app_name}


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest(
    file: UploadFile = File(...),
    department: str | None = Form(default=None),
    doc_type: str | None = Form(default=None),
    service: RagService = Depends(get_rag_service),
) -> IngestResponse:
    filename = file.filename or "upload.pdf"
    if file.content_type not in {"application/pdf", "application/x-pdf"} and not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported.")

    try:
        with NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(await file.read())
            temp_path = Path(temp_file.name)
        return service.ingest_pdf(
            temp_path,
            filename,
            {"department": department, "doc_type": doc_type},
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        if "temp_path" in locals():
            temp_path.unlink(missing_ok=True)


@app.post("/api/ask", response_model=AskResponse)
def ask(payload: AskRequest, service: RagService = Depends(get_rag_service)) -> AskResponse:
    try:
        return service.ask(
            question=payload.question,
            filters={
                "department": payload.department,
                "doc_type": payload.doc_type,
                "source": payload.source,
            },
            top_k=payload.top_k,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/api/documents", response_model=list[DocumentSummary])
def documents(service: RagService = Depends(get_rag_service)) -> list[DocumentSummary]:
    return service.documents()
