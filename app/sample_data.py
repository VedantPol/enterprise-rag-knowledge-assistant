SAMPLE_TOPIC = "Cloudflare Tunnel Home Server Deployment"

SAMPLE_PROMPTS = [
    "What is the safest way to expose the app from a home server?",
    "Which environment variables do I need before running Docker Compose?",
    "How do I update the app after pushing a new GitHub commit?",
    "What happens to uploaded PDFs when the page refreshes?",
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
            "PINECONE_API_KEY can stay blank when the app should avoid persistent user-document storage. "
            "CLOUDFLARE_TUNNEL_TOKEN is only required when starting the tunnel profile with docker compose "
            "--profile tunnel up -d --build."
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
            "Without Pinecone, the app keeps only the small built-in dummy knowledge base resident in memory. "
            "Uploaded PDFs are temporary: the backend does not persist the PDF file or manifest entry, and the "
            "browser clears temporary upload chunks whenever the page loads or refreshes."
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
