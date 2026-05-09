# Enterprise RAG Knowledge Assistant

A sample source-aware RAG web app for searching policy and technical documents. It parses PDFs, chunks text with LangChain, embeds content, stores vectors in Pinecone for production, supports local in-memory demo mode, reranks results, and generates citation-grounded answers with Gemini.

## What You Can Try First

The app ships with a built-in dummy topic:

```text
Cloudflare Tunnel Home Server Deployment
```

After starting the website, click one of the suggested prompts in the left panel. You can test the full ask flow before uploading your own PDF.

## Stack

- Python
- FastAPI
- LangChain
- Pinecone for persistent vector search
- In-memory vector search for local sample mode
- Gemini API
- Docker
- Cloudflare Tunnel

## Run Locally

1. Create and activate a virtual environment.

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install dependencies.

   ```powershell
   pip install -r requirements.txt
   ```

3. Create your local environment file.

   ```powershell
   copy .env.example .env
   ```

4. Open `.env` and set your Gemini key.

   ```env
   GEMINI_API_KEY=your-free-tier-gemini-key
   ```

   You may leave `PINECONE_API_KEY` blank for the sample demo. The app will use an in-memory vector index. That means uploaded PDFs reset when the server restarts.

5. Start the website.

   ```powershell
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

6. Open the site.

   ```text
   http://127.0.0.1:8000
   ```

## Suggested Prompts

Try these with the built-in sample data:

- What is the safest way to expose the app from a home server?
- Which environment variables do I need before running Docker Compose?
- How do I update the app after pushing a new GitHub commit?
- Why should I keep Pinecone enabled on the server?

## Upload Your Own PDF

1. Use the **Ingest PDF** panel.
2. Choose a PDF.
3. Optionally add metadata like department and document type.
4. Click **Index document**.
5. Ask a question about the PDF.

The loading bar shows the active work: upload, parsing, chunking, embeddings, retrieval, reranking, Gemini API call, and citation formatting.

## Run With Docker

1. Make sure Docker is installed.
2. Create `.env` from `.env.example`.
3. Set `GEMINI_API_KEY`.
4. Start the app.

```bash
docker compose up -d --build
```

Then open:

```text
http://localhost:8000
```

## Deploy With Cloudflare Tunnel

For a home server, use Pinecone so vectors survive restarts:

```env
PINECONE_API_KEY=your-pinecone-key
PINECONE_INDEX_NAME=enterprise-rag
GEMINI_API_KEY=your-gemini-key
CLOUDFLARE_TUNNEL_TOKEN=your-cloudflare-tunnel-token
```

In Cloudflare Zero Trust, map your public hostname to:

```text
http://rag-assistant:8000
```

Start the app and tunnel:

```bash
docker compose --profile tunnel up -d --build
```

## Update On Your Server

After pushing changes to GitHub:

```bash
cd /opt/enterprise-rag-knowledge-assistant
git pull
docker compose --profile tunnel up -d --build
```

## Useful Checks

```bash
curl http://localhost:8000/health
docker compose logs -f rag-assistant
docker compose --profile tunnel logs -f cloudflared
```

## Notes

- Local sample mode uses in-memory vectors and resets on restart.
- Server mode should use Pinecone for persistence.
- Default embeddings use `sentence-transformers/all-MiniLM-L6-v2` with `EMBEDDING_DIM=384`.
- If you change the embedding model, update `EMBEDDING_DIM` and use a new Pinecone index.
