---
name: servarr-management
description: Manage Radarr/Sonarr-style media automation via API, UI, and safe fallback workflows.
---

# Servarr management

Use this skill when the user wants to add, verify, or troubleshoot media items in *Radarr*, *Sonarr*, *Prowlarr*, or related Servarr apps.

## When to use
- Add a movie/series to Radarr or Sonarr
- Verify whether a title already exists
- Inspect available root folders or quality profiles
- Diagnose add/search failures, especially lookup/API failures
- Fall back to local database repair only when the API path is blocked and you can verify the schema first

## Core workflow
1. **Identify the exact title and year**
   - Resolve ambiguous titles before making changes.
   - Prefer the platform's canonical metadata source when possible.

2. **Check the running app and basic health**
   - Query the local API status endpoint.
   - Confirm the service is reachable and note the base URL.

3. **Look up candidates before adding**
   - Search by title/year in the app's lookup endpoint.
   - Verify the correct external ID before adding anything.

4. **Choose storage and quality defaults intentionally**
   - Inspect root folders and free space.
   - Inspect quality profiles and pick the intended one rather than assuming a default.

5. **Add through the API first**
   - Use the app's POST add endpoint with monitored/search options when available.
   - Verify the created record with a follow-up GET.

6. **Only use a database fallback as a last resort**
   - First confirm the local DB schema matches the expected app version.
   - Insert both metadata and movie/series rows consistently.
   - Verify the item afterward via the API so the record is not just present in SQL, but actually recognized by the app.

## Radarr-specific notes
- `/api/v3/system/status` confirms the app is alive and exposes the base runtime state.
- `/api/v3/rootfolder` is the authoritative source for usable library paths and free space.
- `/api/v3/qualityprofile` provides the real profile IDs; do not guess IDs.
- `/api/v3/movie/lookup?term=...` is the best first step for title resolution.
- `/api/v3/movie` POST is the normal add path.
- If an add request fails because Radarr is trying to fetch remote metadata and returns a SkyHook-style connection error, treat it as an upstream metadata lookup problem rather than a bad local API key.
- For ambiguous or similar titles, scope discovery with `term=Title%20Year` first, then pick the exact tmdbId from the lookup results instead of selecting from a broad title-only search.
- If add/lookup fails with `SkyHookException` / `api.radarr.video:443`, treat it as an upstream metadata outage. Resolve the TMDB ID externally, but expect add-by-`tmdbId` can still fail if Radar insists on fetching metadata at creation time.
- When the API path is blocked by this outage, report the TMDB ID, title/year, intended profile, and root folder, then offer UI fallback instead of retrying the same external-metadata path.

## Direct DB fallback
Use this only when the user clearly wants the item added and the API path is blocked.

- Inspect the current SQLite schema first.
- Insert a matching metadata row and the media row together in one transaction.
- Use a valid path under an existing root folder.
- Mark the item monitored only if that matches the request.
- Verify the result by querying the app API afterward.

See `references/radarr-direct-add.md` for the condensed Radarr fallback recipe and verification checklist.

## Confirmed failure pattern
If Radarr returns a SkyHook-style error like `Search for '<term>' failed. Invalid response received from RadarrAPI. Connection refused (api.radarr.video:443)`, lookup, add-by-title, and add-by-`tmdbId` can all fail. Validated workaround from `Masters of the Universe (2026)`:
1. Confirm the exact `tmdbId` from a reliable source.
2. Insert the movie directly into `MovieMetadata` and `Movies` in `/var/lib/radarr/radarr.db`.
3. Always follow with API verification with `GET /api/v3/movie/{id}`.
4. Do not rely on `/api/v3/movie` POST or `/api/v3/command` search requests to bootstrap metadata in this outage.

## Pitfalls
- Do not guess quality profile IDs or root folder IDs.
- Do not assume a lookup failure means the title is invalid; it can also be an upstream metadata outage.
- Do not leave a DB write unverified.
- Do not use direct DB writes when the normal API path works.
- Do not store secrets in notes, skill files, or logs.

## Verification
After any add:
- Confirm the item appears in the app's movie/series listing
- Confirm the title, year, root folder, monitored state, and quality profile
- Confirm the request did not silently create a duplicate
- If a fallback was used, confirm the app itself recognizes the item, not just the database
