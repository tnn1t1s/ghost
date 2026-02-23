# Developing

## Submodule Usage

This repo is used as a git submodule in [LifeResearch](https://github.com/tnn1t1s/LifeResearch) at the `ghost/` path.

### How It Works

LifeResearch doesn't contain a copy of these files. It stores two things:

- `.gitmodules` — maps the `ghost/` path to `git@github.com:tnn1t1s/ghost.git`
- A pinned commit SHA — the exact version of this repo that LifeResearch uses

On disk, `ghost/src/ghost_client.py` exists at the same path as before. But git treats `ghost/` as a separate repo inside the parent.

### Cloning LifeResearch

A plain `git clone` gives an empty `ghost/` directory. To get the files:

```bash
# Option A: clone with submodules
git clone --recurse-submodules git@github.com:tnn1t1s/LifeResearch.git

# Option B: init after cloning
git clone git@github.com:tnn1t1s/LifeResearch.git
cd LifeResearch
git submodule update --init
```

### Updating the Ghost Client in LifeResearch

After pushing changes to this repo, pull them into LifeResearch:

```bash
cd LifeResearch/ghost
git pull origin main

# Parent repo now shows ghost as modified (new commit SHA)
cd ..
git add ghost
git commit -m "Update ghost submodule"
```

### Making Changes

Changes to the Ghost client go in this repo, not LifeResearch:

```bash
cd LifeResearch/ghost
# edit files
git add -p && git commit -m "Fix something"
git push origin main

# Then pin the new version in LifeResearch
cd ..
git add ghost
git commit -m "Update ghost submodule"
```

### .env Files

The `.env` file lives inside `ghost/` on disk but is excluded by `.gitignore` in both repos. It is never tracked. When setting up LifeResearch, copy `.env.example` and fill in your values:

```bash
cp ghost/.env.example ghost/.env
# Add: GHOST_URL, GHOST_ADMIN_API_KEY, GCE_PROJECT, GCE_ZONE, GCE_INSTANCE
```

### Why Submodule

- File paths stay identical — `athena_adk/tools/ghost.py` imports from `ghost/src/` unchanged
- The Justfile reads GCE vars from `.env` via `env_var()` — works in both standalone and submodule contexts
- The Ghost client can be used independently without LifeResearch
