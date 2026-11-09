---
name: github-actions
description: Builds fast, secure GitHub Actions CI/CD workflows with least-privilege permissions, SHA-pinned actions, caching, matrices, concurrency control, OIDC cloud auth and safe handling of pull requests from forks. Use when the user asks to set up CI, write or fix a GitHub Actions workflow, speed up a pipeline, add a release or deploy job, or harden workflows.
---

# GitHub Actions

## 1. Discover
- Existing workflows in `.github/workflows/`; reuse their conventions.
- Language, package manager, test/lint/build commands (from manifests and scripts), supported runtime versions.
- Deploy target and how it authenticates.

## 2. Baseline CI template
```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read            # least privilege; grant more per job only when needed

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  test:
    runs-on: ubuntu-latest
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        node: [20, 22]
    steps:
      - uses: actions/checkout@v4          # pin to a full commit SHA in production
        with:
          persist-credentials: false
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: npm
      - run: npm ci
      - run: npm run lint
      - run: npm test -- --coverage
      - run: npm run build
```

Equivalent setup actions with built-in caching: `actions/setup-python` (`cache: pip`), `actions/setup-go` (cache on by default), `actions/setup-java` (`cache: gradle|maven`). For others, use `actions/cache` keyed on the lockfile hash.

## 3. Security hardening (non-negotiable)
- **Pin third-party actions to a full commit SHA** with a version comment: `uses: org/action@3f1c2b...  # v2.1.0`. Let Dependabot update them:
  ```yaml
  # .github/dependabot.yml
  version: 2
  updates:
    - package-ecosystem: github-actions
      directory: /
      schedule: { interval: weekly }
  ```
- Top-level `permissions: contents: read`; elevate per job (`packages: write`, `id-token: write`) only where needed.
- **Never** use `pull_request_target` together with checking out and running the PR's code. Fork PRs get no secrets on `pull_request`; that is a feature.
- **Script injection:** never interpolate untrusted context directly into `run:`. Pass it through `env`:
  ```yaml
  - env:
      TITLE: ${{ github.event.pull_request.title }}
    run: echo "$TITLE"
  ```
- Cloud deploys: use **OIDC** (`aws-actions/configure-aws-credentials`, `google-github-actions/auth`, `azure/login`) instead of long-lived keys.
- Protect deploy jobs with `environment:` (required reviewers, branch rules) and scope secrets to environments.
- `persist-credentials: false` on checkout unless a later step must push.

## 4. Speed
- Cache dependencies (above); cache build outputs (Turbo, Nx, Gradle, ccache) where supported.
- Split independent jobs (lint, unit, e2e) so they run in parallel; use `needs:` only for real dependencies.
- `paths` / `paths-ignore` filters to skip CI for docs-only changes (but keep required checks satisfiable).
- Shard slow test suites with a matrix; set `timeout-minutes` on every job.

## 5. Common add-ons
- **Release on tag:** `on: push: tags: ['v*']` → build → `gh release create "$GITHUB_REF_NAME" --generate-notes` with `permissions: contents: write`.
- **Docker publish:** `docker/setup-buildx-action`, `docker/login-action` to GHCR with `GITHUB_TOKEN` and `packages: write`, `docker/build-push-action` with `cache-from/cache-to: type=gha`.
- **Reusable workflows** (`workflow_call`) to share CI across repos.

## 6. Validate
- Lint locally if available: `actionlint`, and `zizmor` for security issues.
- After pushing, check the run: `gh run list --limit 5`, `gh run view <id> --log-failed`.
- Report: what each job does, expected duration, and required repository settings (secrets, environments, branch protection checks).
