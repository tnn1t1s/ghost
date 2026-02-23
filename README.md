# Ghost CMS Client

Publish to a self-hosted Ghost CMS from any agent or script. Python client + shell tools + Docker deployment.

## 30-Second Setup

```bash
git clone git@github.com:tnn1t1s/ghost.git
cd ghost
just setup-venv
cp .env.example .env
```

Edit `.env` — you need exactly two values:

```
GHOST_URL=http://localhost:2368
GHOST_ADMIN_API_KEY=64char_id:64char_secret_hex
```

Get the API key from Ghost Admin → Settings → Integrations → Add custom integration.

Test it works:

```bash
just list-posts
```

## Tools (for agents and scripts)

Standalone shell scripts in `tools/bin/` — no Justfile needed, auto-load `.env`.

### Publish

```bash
# Draft from string
tools/bin/ghost-publish "My Title" "<p>Hello world</p>"

# Draft from file
tools/bin/ghost-publish "My Title" --file /tmp/article.html

# Publish immediately
tools/bin/ghost-publish "My Title" "<p>Hello</p>" --status published

# With tags
tools/bin/ghost-publish "My Title" --file /tmp/post.html --tags "ai,agents"

# From stdin (pipe from another tool)
echo "<p>Generated content</p>" | tools/bin/ghost-publish "My Title" --stdin
```

### List & Read

```bash
tools/bin/ghost-list              # All posts
tools/bin/ghost-list drafts       # Drafts only
tools/bin/ghost-list published    # Published only
tools/bin/ghost-get <post_id>     # Full post JSON
```

### Upload Image

```bash
tools/bin/ghost-upload photo.png              # Returns hosted URL
tools/bin/ghost-upload hero.jpg --ref "hero"  # With reference name
```

## Python API

```python
from src.ghost_client import GhostClient

client = GhostClient()

# Create draft
post = client.create_post("Title", "<p>HTML body</p>", status="draft")

# Publish
client.publish_post(post["id"])

# List
for p in client.list_posts(status="draft"):
    print(f"{p['id']}  {p['title']}")

# Upload image
url = client.upload_image("photo.png")
```

## Justfile Commands

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

# GCE Infrastructure (requires GCE_* env vars)
just ssh-tunnel                # localhost:2368 access
just check-ghost-health
just view-ghost-logs
just restart-ghost-containers
just deploy-compose
```

## Integration with Other Agents

Point your agent at this repo and use `tools/bin/` scripts. They:
- Auto-source `.env` from the repo root
- Need only `GHOST_URL` and `GHOST_ADMIN_API_KEY`
- Exit non-zero on failure with stderr message
- Return JSON on success

Example — an agent publishes a daily report:

```bash
GHOST_DIR="/path/to/ghost"
"$GHOST_DIR/tools/bin/ghost-publish" "Daily Report $(date +%F)" --file /tmp/report.html --tags "reports,daily"
```

Or import directly in Python:

```python
import sys
sys.path.insert(0, "/path/to/ghost/src")
from ghost_client import GhostClient

client = GhostClient()  # reads GHOST_URL + GHOST_ADMIN_API_KEY from env
post = client.create_post("Agent Output", html, status="draft", tags=["agent", "automated"])
```

## Configuration Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `GHOST_URL` | Yes | Ghost instance URL (e.g., `http://localhost:2368`) |
| `GHOST_ADMIN_API_KEY` | Yes | Admin API key — format `id:secret_hex` |
| `GCE_PROJECT` | GCE only | GCP project ID |
| `GCE_ZONE` | GCE only | GCE zone (default: `us-central1-a`) |
| `GCE_INSTANCE` | GCE only | GCE instance name |

## Architecture

```
src/
├── ghost_api.py       # Abstract CMS interface (CMSBackend ABC)
└── ghost_client.py    # Ghost Admin API v5 implementation + CLI

tools/bin/
├── ghost-publish      # Create draft or post (string, file, or stdin)
├── ghost-list         # List posts by status
├── ghost-get          # Get post by ID (full JSON)
└── ghost-upload       # Upload image, return URL
```

## Docker Deployment

Ghost 5 + MySQL 8 via Docker Compose:

```bash
# Set MySQL passwords
cp deploy/.env.gce.example deploy/.env.gce
# Edit deploy/.env.gce

# Deploy to GCE
just deploy-compose
just restart-ghost-containers
```

## License

MIT
