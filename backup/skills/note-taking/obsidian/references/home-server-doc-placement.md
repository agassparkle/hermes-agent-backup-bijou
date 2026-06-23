# Home server doc placement

## Convention

When the user supplies a markdown document and asks for it to be stored under `/home/agas/Hermes/`, place it in a topic-named subdirectory and keep the original filename unless the user requests a rename.

Example:
- `/home/agas/Hermes/home-server/home-server-docs.md`

## Verification

After writing the file:
1. Read back the file with `read_file`.
2. Confirm the path and basic content match what was written.
3. Report the final absolute path to the user.
