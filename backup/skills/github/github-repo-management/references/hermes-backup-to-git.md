# Backing Up Hermes Config/State to GitHub

Use this workflow when the user wants a portable backup of Hermes configuration and non-secret state in a GitHub repo.

## Goal

Back up the live Hermes setup without leaking credentials or transient runtime data.

## Include

- `~/.hermes/config.yaml`
- `~/.hermes/channel_directory.json`
- `~/.hermes/gateway_state.json`
- `~/.hermes/context_length_cache.yaml`
- `~/.hermes/SOUL.md`
- non-secret operational folders such as `cron/`, `memories/`, `sessions/`, and `skills/`

## Exclude

Never copy these into the repo:

- `~/.hermes/.env`
- `~/.hermes/auth.json`
- `~/.hermes/shared/nous_auth.json`
- `~/.hermes/state.db*`
- logs, caches, locks, pid files, and other transient artifacts

## Recommended repository layout

```text
repo/
  backup/
    README.md
    config.yaml
    channel_directory.json
    gateway_state.json
    context_length_cache.yaml
    SOUL.md
    cron/
    memories/
    sessions/
    skills/
```

## Workflow

1. Clone or create the target repo.
2. Copy only the allowed files/folders into a dedicated `backup/` directory.
3. Add a `.gitignore` that excludes secrets and runtime noise.
4. Add a short `README.md` explaining what is included and excluded.
5. Commit with a clear message.
6. Push to the repo and verify the remote matches the local commit.

## Verification

- Check that the repo contains no `.env`, `auth.json`, or `state.db` files.
- Confirm the pushed branch matches the local HEAD.
- If credentials were used temporarily in a remote URL, remove them from the remote after pushing.

## Notes

- Prefer a dedicated backup repo or dedicated `backup/` subdirectory instead of mixing backup files with unrelated project code.
- Keep the backup focused on durable configuration and user-generated state, not raw secret stores.
