# Enterprise RAG Knowledge Assistant

A deployable FastAPI website for source-aware search over policy and technical PDFs. It parses PDFs, chunks them with LangChain, creates embeddings, stores vectors in Pinecone, applies metadata filters, optionally reranks retrieved passages, and generates citation-grounded answers.

## Stack

- Python
- FastAPI
- LangChain
- Pinecone
- Docker
- Cloudflare Tunnel

## Local Setup

1. Create an environment file:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and set:

   ```bash
   PINECONE_API_KEY=your-pinecone-key
   PINECONE_INDEX_NAME=enterprise-rag
   OPENAI_API_KEY=optional-for-generated-answers
   ```

3. Run the service:

   ```bash
   docker compose up --build
   ```

4. Open:

   ```text
   http://localhost:8000
   ```

Without `OPENAI_API_KEY`, the app still retrieves and cites the most relevant passages. With `OPENAI_API_KEY`, it generates a grounded answer from retrieved context.

## Cloudflare Tunnel Deployment

1. On your home server, install Docker and Docker Compose.

2. In Cloudflare Zero Trust, create a tunnel and add a public hostname, for example:

   ```text
   kb.yourdomain.com -> http://rag-assistant:8000
   ```

3. Copy the tunnel token into `.env`:

   ```bash
   CLOUDFLARE_TUNNEL_TOKEN=your-cloudflare-tunnel-token
   ```

4. Start the app and tunnel containers:

   ```bash
   docker compose --profile tunnel up -d --build
   ```

Cloudflare will route your public hostname to the FastAPI container through the `cloudflared` service on the same Docker network.

## API

### Upload and Index a PDF

```bash
curl -X POST http://localhost:8000/api/ingest \
  -F "file=@policy.pdf" \
  -F "department=HR" \
  -F "doc_type=Policy"
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the password rotation policy?","department":"HR"}'
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Notes

- `storage/` is mounted as a Docker volume path and stores uploaded PDFs plus the local document manifest.
- Pinecone stores vectors and searchable metadata.
- The default embedding model is `sentence-transformers/all-MiniLM-L6-v2`, which uses `EMBEDDING_DIM=384`.
- If you change `EMBEDDING_MODEL`, update `EMBEDDING_DIM` and recreate or use a new Pinecone index.
