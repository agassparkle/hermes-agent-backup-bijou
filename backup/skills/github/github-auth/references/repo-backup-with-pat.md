# Repo backup with a fine-grained PAT

Use this when the user gives you a repository-scoped GitHub token and asks you to back up local Hermes state into that one repo.

## Safe pattern

1. Create the target repo clone/worktree locally.
2. Copy only non-secret Hermes data.
3. Add a `.gitignore` that excludes secrets and volatile runtime files.
4. Commit locally with a clear message.
5. Push with a tokenized HTTPS remote only for the push step.
6. Restore the remote URL to the clean, token-free HTTPS URL.
7. Verify the pushed branch matches the local commit SHA.

## Exclude by default

- `.env`
- `auth.json`
- `shared/nous_auth.json`
- `state.db*`
- logs, caches, locks, and PID files
- any file that can contain credentials, sessions, or transient runtime state

## Verification

- `git status` is clean after commit
- remote branch SHA equals local `HEAD`
- remote URL shown by `git remote -v` does not contain the token after cleanup
