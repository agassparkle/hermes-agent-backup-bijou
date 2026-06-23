# Home-server notes backup to GitHub

Use this when the user creates or updates human-readable server notes such as inventories, upgrade checklists, or change logs and wants them backed up to GitHub.

## Placement convention

- Keep the source note in `/home/agas/Hermes/home-server/`.
- Mirror it into the repository under `backup/home-server/` before committing.
- Keep the original filename unless the user asks to rename it.

Example:
- Source: `/home/agas/Hermes/home-server/ubuntu-server-inventory.md`
- Repo copy: `backup/home-server/ubuntu-server-inventory.md`

## Workflow

1. Write or update the Markdown note locally.
2. Read the file back to verify the content.
3. Copy it into the repo's `backup/home-server/` subtree.
4. Commit with a clear message.
5. Push the commit and verify the remote HEAD matches the local commit.

## Notes

- Treat these as durable operational docs, not app config.
- Keep the repo copy human-readable and easy to diff.
- Do not include secrets, auth tokens, or transient state.
