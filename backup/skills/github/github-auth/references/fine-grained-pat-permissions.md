# Fine-Grained PAT Permissions for Repo Operations

GitHub fine-grained personal access tokens need specific, separate permissions for different repo operations. Classic tokens just need `repo` scope — one checkbox.

## Required Permissions

| Operation | Permission | Level |
|---|---|---|
| Create repo (API) | **Administration** | Read and write |
| Push code | **Contents** | Read and write |
| Read repo | **Metadata** | Read-only (always on) |
| Manage issues/PRs | **Issues** / **Pull requests** | Read and write |

## Repository Access

Fine-grained tokens are scoped to specific repos by default. Even with correct permissions, operations fail if the repo isn't accessible:

- **All repositories** — recommended if you create repos programmatically
- **Only select repositories** — must manually add each new repo

## Common Failure Sequence

Creating and pushing to a new repo with a fine-grained token:

1. ✅ Token creates repo (Administration ✓, repo accessible during creation)
2. ❌ Push fails `403: Write access to repository not granted`
   - **Missing Contents permission** → add Contents: Read and write
3. ❌ Still fails after adding Contents
   - **Repo not in access list** → switch to "All repositories" or add the new repo
4. ✅ Push succeeds

## Token Type Detection

```python
# Call GET /user and inspect response headers
# Classic tokens: X-OAuth-Scopes header present (e.g., "repo, workflow")
# Fine-grained tokens: NO X-OAuth-Scopes header
```

Fine-grained PATs are typically 93+ characters. Classic PATs are ~40 characters.
