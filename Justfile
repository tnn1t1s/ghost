# Ghost CMS Publishing Platform

set dotenv-load

GCE_PROJECT := env_var("GCE_PROJECT")
GCE_ZONE := env_var("GCE_ZONE")
GCE_INSTANCE := env_var("GCE_INSTANCE")
PYTHON := "python3"

default:
    @just --list

# Publish a draft post (title, html, optional author email, optional comma-separated tags)
publish-draft title html author="" tags="":
    {{PYTHON}} src/ghost_client.py create-draft "{{title}}" "{{html}}" "{{author}}" "{{tags}}"

# Publish a draft from an HTML file
publish-draft-file title file author="" tags="":
    {{PYTHON}} src/ghost_client.py create-draft "{{title}}" "$(cat '{{file}}')" "{{author}}" "{{tags}}"

# Publish a post immediately (title, html, optional author email, optional tags)
publish-post title html author="" tags="":
    {{PYTHON}} src/ghost_client.py create-post "{{title}}" "{{html}}" "{{author}}" "{{tags}}"

# Publish a post from an HTML file
publish-post-file title file author="" tags="":
    {{PYTHON}} src/ghost_client.py create-post "{{title}}" "$(cat '{{file}}')" "{{author}}" "{{tags}}"

# Publish an existing draft by post ID
publish-existing-draft post_id:
    {{PYTHON}} src/ghost_client.py publish "{{post_id}}"

# Upload an image (returns URL)
upload-image file ref="":
    {{PYTHON}} src/ghost_client.py upload-image "{{file}}" "{{ref}}"

# List posts (status: all, draft, published; limit default 15)
list-posts status="all" limit="15":
    {{PYTHON}} src/ghost_client.py list "{{status}}" "{{limit}}"

# List draft posts
list-drafts:
    {{PYTHON}} src/ghost_client.py list draft

# List published posts
list-published:
    {{PYTHON}} src/ghost_client.py list published

# Get a specific post by ID
get-post post_id:
    {{PYTHON}} src/ghost_client.py get "{{post_id}}"

# Check Ghost health via SSH tunnel
check-ghost-health:
    gcloud compute ssh {{GCE_INSTANCE}} --project={{GCE_PROJECT}} --zone={{GCE_ZONE}} -- 'curl -s -o /dev/null -w "%{http_code}" http://localhost:2368/'

# SSH into Ghost instance
ssh-ghost-instance:
    gcloud compute ssh {{GCE_INSTANCE}} --project={{GCE_PROJECT}} --zone={{GCE_ZONE}}

# SSH tunnel for local access (localhost:2368)
ssh-tunnel:
    gcloud compute ssh {{GCE_INSTANCE}} --project={{GCE_PROJECT}} --zone={{GCE_ZONE}} -- -L 2368:localhost:2368

# View Ghost container logs
view-ghost-logs:
    gcloud compute ssh {{GCE_INSTANCE}} --project={{GCE_PROJECT}} --zone={{GCE_ZONE}} -- 'cd ~/ghost && sudo docker compose logs --tail=50'

# Deploy docker-compose.yml to GCE
deploy-compose:
    gcloud compute scp docker-compose.yml {{GCE_INSTANCE}}:~/ghost/docker-compose.yml --project={{GCE_PROJECT}} --zone={{GCE_ZONE}}

# Restart Ghost containers on GCE
restart-ghost-containers:
    gcloud compute ssh {{GCE_INSTANCE}} --project={{GCE_PROJECT}} --zone={{GCE_ZONE}} -- 'cd ~/ghost && sudo docker compose down && sudo docker compose up -d'

