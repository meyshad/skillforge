---
name: dockerize
description: Containerizes an application with a small, secure, production-grade Dockerfile (multi-stage build, pinned base image, non-root user, layer caching, healthcheck) plus .dockerignore and an optional compose file for local development. Use when the user asks to dockerize, containerize, write or optimize a Dockerfile, shrink an image, or fix slow Docker builds.
---

# Dockerize

## 1. Understand the app first
- Language/runtime and version (`.nvmrc`, `engines`, `.python-version`, `go.mod`, `rust-toolchain`).
- Build command, start command, listening port, required env vars, writable paths, native dependencies.
- If a Dockerfile exists, review it against the checklist in step 4 instead of starting over.

## 2. Principles
1. **Multi-stage:** build tools live in the builder stage; the runtime stage gets only artifacts.
2. **Pin the base:** `node:22.11-bookworm-slim`, not `node:latest`. For maximum reproducibility pin the digest (`@sha256:...`).
3. **Cache-friendly order:** copy lockfiles → install deps → copy source → build.
4. **Non-root:** run as an unprivileged user; files owned by root and read-only where possible.
5. **Small runtime:** `-slim`, `distroless` or `alpine` (watch for musl issues with native modules).
6. **One process, exec form:** `CMD ["node", "server.js"]` so signals reach the app; add `tini` (or `--init`) if the app spawns children.
7. **Config through env**, secrets at runtime (never `COPY .env`, never `ARG` for secrets; use BuildKit `--mount=type=secret` for build-time secrets).

## 3. Templates

### Node.js
```dockerfile
# syntax=docker/dockerfile:1.7
FROM node:22-bookworm-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci

FROM deps AS build
COPY . .
RUN npm run build && npm prune --omit=dev

FROM node:22-bookworm-slim AS runtime
ENV NODE_ENV=production
WORKDIR /app
COPY --from=build --chown=node:node /app/node_modules ./node_modules
COPY --from=build --chown=node:node /app/dist ./dist
COPY --chown=node:node package.json ./
USER node
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD node -e "fetch('http://127.0.0.1:3000/health').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"
CMD ["node", "dist/server.js"]
```

### Python
```dockerfile
# syntax=docker/dockerfile:1.7
FROM python:3.12-slim AS build
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

FROM python:3.12-slim AS runtime
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 app
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY --chown=app:app . .
USER app
EXPOSE 8000
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
```

### Go (static binary, distroless)
```dockerfile
# syntax=docker/dockerfile:1.7
FROM golang:1.23 AS build
WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod go mod download
COPY . .
RUN --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o /out/app ./cmd/app

FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=build /out/app /app
EXPOSE 8080
ENTRYPOINT ["/app"]
```

### .dockerignore (always)
```
.git
node_modules
dist
build
__pycache__
.venv
*.log
.env
.env.*
coverage
Dockerfile*
docker-compose*.yml
```

## 4. Review checklist
- [ ] Base image pinned; no `latest`.
- [ ] Multi-stage; no compilers, package caches or source maps in runtime unless needed.
- [ ] Dependencies installed from the lockfile (`npm ci`, `pip install -r`, `go mod download`).
- [ ] `USER` is non-root; no `chmod 777`.
- [ ] No secrets in layers (`docker history --no-trunc <image>` is clean).
- [ ] `HEALTHCHECK` or orchestrator probes defined; app handles `SIGTERM` gracefully.
- [ ] `.dockerignore` present; build context is small.

## 5. Verify
```bash
docker build -t app:dev .
docker run --rm -p 3000:3000 --env-file .env.example app:dev
docker images app:dev                 # report the size
docker scout cves app:dev || trivy image app:dev   # if available
```
Report image size before and after, and any CVEs at high or critical severity.
