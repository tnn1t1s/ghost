# Ghost Admin API Client

Python client for the Ghost CMS Admin API with Docker Compose deployment and Justfile commands.

## Features

- ABC-based CMS backend interface (`CMSBackend`)
- Ghost Admin API implementation with JWT auth
- CLI for creating, publishing, listing, and managing posts
- Image upload support
- Docker Compose for self-hosted Ghost + MySQL
- GCE deployment commands via `gcloud`

## Setup

```bash
# Clone
git clone git@github.com:tnn1t1s/ghost.git
cd ghost

# Python environment
just setup-venv

# Configure
cp .env.example .env
# Edit .env with your Ghost URL and Admin API key
```

## Configuration

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|----------|-------------|
| `GHOST_URL` | Ghost instance URL (e.g., `http://localhost:2368`) |
| `GHOST_ADMIN_API_KEY` | Admin API key in `id:secret` format |
| `GCE_PROJECT` | GCP project ID (for GCE deployment) |
| `GCE_ZONE` | GCE zone (default: `us-central1-a`) |
| `GCE_INSTANCE` | GCE instance name |

Get your Admin API key from Ghost Admin > Settings > Integrations > Add custom integration.

## Usage

### Justfile Commands

```bash
# Publishing
just publish-draft "Title" "<p>Content</p>"
just publish-draft-file "Title" /tmp/article.html
just publish-post "Title" "<p>Content</p>"
just publish-post-file "Title" /tmp/article.html
just publish-existing-draft <post_id>

# Management
just list-posts
just list-drafts
just list-published
just get-post <post_id>
just upload-image photo.png

# GCE Infrastructure
just ssh-tunnel              # Local access at localhost:2368
just check-ghost-health
just view-ghost-logs
just restart-ghost-containers
just deploy-compose
```

### Python API

```python
from ghost_client import GhostClient

client = GhostClient()

# Create a draft
post = client.create_post("My Post", "<p>Hello</p>", status="draft")

# Publish it
client.publish_post(post["id"])

# List all posts
for p in client.list_posts():
    print(f"{p['id']}  {p['status']}  {p['title']}")
```

## Docker Deployment

```bash
# Set MySQL passwords in deploy/.env.gce
# Deploy to GCE
just deploy-compose
just restart-ghost-containers
```

## License

MIT
