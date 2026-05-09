SAMPLE_TOPIC = "Cloudflare Tunnel Home Server Deployment"

SAMPLE_PROMPTS = [
    "What is the safest way to expose the app from a home server?",
    "Which environment variables do I need before running Docker Compose?",
    "How do I update the app after pushing a new GitHub commit?",
    "Why should I keep Pinecone enabled on the server?",
]

SAMPLE_DOCUMENTS = [
    {
        "page_content": (
            "A home-server deployment should run the Enterprise RAG Knowledge Assistant as a Docker Compose "
            "service on an internal port such as 8000. The public internet should not connect directly to the "
            "FastAPI container. Cloudflare Tunnel should be used as the public entrypoint, with a hostname such "
            "as kb.example.com routing to http://rag-assistant:8000 inside the Docker network."
        ),
        "metadata": {
            "source_id": "sample-cloudflare-home-server",
            "source": "sample-cloudflare-home-server.md",
            "department": "Operations",
            "doc_type": "Runbook",
            "page": 0,
            "sample": "true",
        },
    },
    {
        "page_content": (
            "Before starting the stack, copy .env.example to .env and set GEMINI_API_KEY for answer generation. "
            "For persistent retrieval, set PINECONE_API_KEY and keep PINECONE_INDEX_NAME consistent across "
            "deployments. CLOUDFLARE_TUNNEL_TOKEN is only required when starting the tunnel profile with "
            "docker compose --profile tunnel up -d --build."
        ),
        "metadata": {
            "source_id": "sample-cloudflare-home-server",
            "source": "sample-cloudflare-home-server.md",
            "department": "Operations",
            "doc_type": "Runbook",
            "page": 1,
            "sample": "true",
        },
    },
    {
        "page_content": (
            "A normal update flow is: push code to GitHub, SSH into the home server, run git pull in the project "
            "directory, then run docker compose --profile tunnel up -d --build. The command rebuilds the FastAPI "
            "image, recreates changed containers, and leaves the tunnel attached to the app service."
        ),
        "metadata": {
            "source_id": "sample-cloudflare-home-server",
            "source": "sample-cloudflare-home-server.md",
            "department": "Operations",
            "doc_type": "Runbook",
            "page": 2,
            "sample": "true",
        },
    },
    {
        "page_content": (
            "Local demo mode can run without Pinecone by using an in-memory vector store, but that index is reset "
            "whenever the server restarts. A server deployment should use Pinecone so uploaded document chunks, "
            "metadata filters, and retrieval results survive container rebuilds and machine restarts."
        ),
        "metadata": {
            "source_id": "sample-cloudflare-home-server",
            "source": "sample-cloudflare-home-server.md",
            "department": "Operations",
            "doc_type": "Runbook",
            "page": 3,
            "sample": "true",
        },
    },
]

SAMPLE_DOCUMENT_SUMMARY = {
    "source_id": "sample-cloudflare-home-server",
    "filename": "sample-cloudflare-home-server.md",
    "chunks": len(SAMPLE_DOCUMENTS),
    "metadata": {
        "department": "Operations",
        "doc_type": "Runbook",
        "topic": SAMPLE_TOPIC,
    },
}
