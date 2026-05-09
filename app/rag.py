import hashlib
import os
import shutil
from pathlib import Path
from typing import Any

from app.config import Settings
from app.manifest import ManifestStore
from app.schemas import AskResponse, Citation, DocumentSummary, IngestResponse


class RagService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.manifest = ManifestStore(settings.manifest_path)
        self._embeddings: Any | None = None
        self._vector_store: Any | None = None
        self._reranker: Any | None = None

    @property
    def embeddings(self) -> Any:
        if self._embeddings is None:
            from langchain_huggingface import HuggingFaceEmbeddings

            self._embeddings = HuggingFaceEmbeddings(model_name=self.settings.embedding_model)
        return self._embeddings

    def _pinecone(self) -> Any:
        if not self.settings.pinecone_api_key:
            raise RuntimeError("PINECONE_API_KEY is required for ingestion and retrieval.")
        from pinecone import Pinecone

        return Pinecone(api_key=self.settings.pinecone_api_key)

    def _ensure_index(self) -> Any:
        pc = self._pinecone()
        indexes = pc.list_indexes()
        if hasattr(indexes, "names"):
            existing = set(indexes.names())
        else:
            existing = {index["name"] for index in indexes}
        if self.settings.pinecone_index_name not in existing:
            from pinecone import ServerlessSpec

            pc.create_index(
                name=self.settings.pinecone_index_name,
                dimension=self.settings.embedding_dim,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=self.settings.pinecone_cloud,
                    region=self.settings.pinecone_region,
                ),
            )
        return pc.Index(self.settings.pinecone_index_name)

    @property
    def vector_store(self) -> Any:
        if self._vector_store is None:
            from langchain_pinecone import PineconeVectorStore

            index = self._ensure_index()
            self._vector_store = PineconeVectorStore(
                index=index,
                embedding=self.embeddings,
                namespace=self.settings.pinecone_namespace,
            )
        return self._vector_store

    @property
    def reranker(self) -> Any | None:
        if not self.settings.rerank_model:
            return None
        if self._reranker is None:
            from sentence_transformers import CrossEncoder

            self._reranker = CrossEncoder(self.settings.rerank_model)
        return self._reranker

    def ingest_pdf(
        self,
        upload_path: Path,
        filename: str,
        metadata: dict[str, str | None],
    ) -> IngestResponse:
        from langchain_community.document_loaders import PyPDFLoader
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        source_id = self._source_id(upload_path)
        saved_name = f"{source_id[:12]}-{Path(filename).name}"
        saved_path = self.settings.upload_dir / saved_name
        shutil.copyfile(upload_path, saved_path)

        docs = PyPDFLoader(str(saved_path)).load()
        for doc in docs:
            doc.metadata.update(
                {
                    "source_id": source_id,
                    "source": filename,
                    "stored_path": str(saved_path),
                    **{key: value for key, value in metadata.items() if value},
                }
            )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
        )
        chunks = splitter.split_documents(docs)
        ids = [f"{source_id}:{i}" for i in range(len(chunks))]
        self.vector_store.add_documents(chunks, ids=ids)

        clean_metadata = {key: value for key, value in metadata.items() if value}
        self.manifest.upsert(
            source_id,
            {
                "filename": filename,
                "stored_path": str(saved_path),
                "chunks": len(chunks),
                "metadata": clean_metadata,
            },
        )

        return IngestResponse(
            source_id=source_id,
            filename=filename,
            chunks_indexed=len(chunks),
            metadata=clean_metadata,
        )

    def ask(
        self,
        question: str,
        filters: dict[str, str | None],
        top_k: int | None = None,
    ) -> AskResponse:
        pinecone_filter = {key: {"$eq": value} for key, value in filters.items() if value}
        results = self.vector_store.similarity_search_with_score(
            query=question,
            k=top_k or self.settings.retrieval_top_k,
            filter=pinecone_filter or None,
        )
        reranked = self._rerank(question, results)[: self.settings.rerank_top_k]
        docs = [doc for doc, _score in reranked]

        answer, used_llm = self._generate_answer(question, docs)
        citations = [
            Citation(
                source=doc.metadata.get("source", "unknown"),
                page=self._page_number(doc.metadata),
                score=float(score) if score is not None else None,
                snippet=self._snippet(doc.page_content),
                metadata=doc.metadata,
            )
            for doc, score in reranked
        ]
        return AskResponse(answer=answer, citations=citations, used_llm=used_llm)

    def documents(self) -> list[DocumentSummary]:
        records = self.manifest.all()
        return [
            DocumentSummary(
                source_id=source_id,
                filename=record.get("filename", "unknown"),
                chunks=int(record.get("chunks", 0)),
                metadata=record.get("metadata", {}),
            )
            for source_id, record in records.items()
        ]

    def _rerank(
        self,
        question: str,
        results: list[tuple[Any, float]],
    ) -> list[tuple[Any, float]]:
        if not results:
            return []
        reranker = self.reranker
        if reranker is None:
            return sorted(results, key=lambda item: item[1], reverse=True)

        pairs = [(question, doc.page_content) for doc, _score in results]
        scores = reranker.predict(pairs)
        enriched = [(doc, float(score)) for (doc, _old_score), score in zip(results, scores)]
        return sorted(enriched, key=lambda item: item[1], reverse=True)

    def _generate_answer(self, question: str, docs: list[Any]) -> tuple[str, bool]:
        if not docs:
            return (
                "I could not find relevant passages in the indexed knowledge base for that question.",
                False,
            )

        context = "\n\n".join(
            f"[{i + 1}] {doc.metadata.get('source', 'unknown')} page {self._page_number(doc.metadata) or '?'}\n"
            f"{doc.page_content}"
            for i, doc in enumerate(docs)
        )

        if self.settings.openai_api_key:
            from langchain_openai import ChatOpenAI

            os.environ["OPENAI_API_KEY"] = self.settings.openai_api_key
            llm = ChatOpenAI(model=self.settings.openai_model, temperature=0)
            response = llm.invoke(
                [
                    (
                        "system",
                        "You are a source-aware enterprise knowledge assistant. "
                        "Answer only from the provided context. Include bracketed citation numbers "
                        "for every factual claim. If the answer is not in the context, say so.",
                    ),
                    ("human", f"Question: {question}\n\nContext:\n{context}"),
                ]
            )
            return str(response.content), True

        extractive = "\n\n".join(
            f"[{i + 1}] {self._snippet(doc.page_content, limit=420)}"
            for i, doc in enumerate(docs[:3])
        )
        return (
            "No LLM key is configured, so here are the most relevant cited passages:\n\n"
            f"{extractive}",
            False,
        )

    @staticmethod
    def _source_id(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for block in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    @staticmethod
    def _page_number(metadata: dict) -> int | None:
        page = metadata.get("page")
        return int(page) + 1 if isinstance(page, int) else None

    @staticmethod
    def _snippet(text: str, limit: int = 320) -> str:
        cleaned = " ".join(text.split())
        if len(cleaned) <= limit:
            return cleaned
        return f"{cleaned[: limit - 3]}..."
