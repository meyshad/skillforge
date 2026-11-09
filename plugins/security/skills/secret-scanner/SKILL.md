---
name: secret-scanner
description: Detects hard-coded credentials (cloud keys, tokens, private keys, passwords, credentials in URLs) in the working tree and full git history using a bundled zero-dependency scanner, then guides safe rotation and history cleanup. Use before publishing a repo, before a push, after a suspected leak, or when the user asks to check for secrets or API keys.
---

# Secret Scanner

## 1. Scan

The bundled scanner needs only Python 3.8+:

```bash
# Working tree
python3 scripts/scan_secrets.py .

# Working tree + every commit on every branch (do this before making a repo public)
python3 scripts/scan_secrets.py . --history

# CI-friendly
python3 scripts/scan_secrets.py . --json
```

`scripts/` is relative to this skill's directory. Exit code `1` means findings, so it works as a pre-commit hook or CI gate.

If `gitleaks` or `trufflehog` is installed, run it as a second opinion: `gitleaks detect --source . -v` or `trufflehog git file://. --only-verified`.

## 2. Triage every finding
For each hit, open the file and decide:

| Verdict | Signal | Action |
|---|---|---|
| **Real secret** | Valid format, plausible entropy, used in code/config | Go to step 3 immediately |
| **Test fixture** | Clearly fake value in tests/docs | Replace with an obvious placeholder or add `secretscan:ignore` to the line |
| **False positive** | Hash, UUID, public key, base64 asset | Add `secretscan:ignore` with a short reason |

Never print a full secret back to the user. Refer to it by file, line and the masked preview.

## 3. Respond to a real leak (order matters)
1. **Rotate/revoke first.** Assume it's compromised the moment it was pushed anywhere. Generate a new key in the provider console and revoke the old one. Deleting the commit does **not** un-leak it.
2. **Check for abuse:** provider audit logs, billing spikes, unknown resources.
3. **Move the secret out of code:** environment variables, a `.env` file that is git-ignored, or a secret manager (AWS Secrets Manager, GCP Secret Manager, Vault, Doppler, 1Password, GitHub Actions secrets).
4. **Add prevention:**
   ```gitignore
   .env
   .env.*
   !.env.example
   *.pem
   *.key
   ```
   Commit a `.env.example` with placeholder values.
5. **Clean history only if needed** (and with the user's explicit approval, since it rewrites history and requires a force push):
   ```bash
   # Preferred tool: https://github.com/newren/git-filter-repo
   git filter-repo --replace-text <(echo 'THE_OLD_SECRET==>REMOVED')
   ```
   Then every collaborator must re-clone. On GitHub, ask support to purge cached views if the repo was public.

## 4. Prevent recurrence
Suggest a pre-commit hook:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```
and enable GitHub **secret scanning + push protection** in repository settings.

## Report format
```markdown
## Secret scan: <N> findings (<critical> critical)
| Severity | Rule | Location | Verdict | Action |
|---|---|---|---|---|
| critical | aws-access-key-id | config/prod.js:12 | Real | Rotate, move to env |
```
