# Radarr metadata outage: api.radarr.video refused

## Symptom
`POST /api/v3/movie` or `/api/v3/movie/lookup` fails with:
```
Connection refused (api.radarr.video:443)
```
DNS resolves normally, but TCP connect to `188.114.97.7:443` is refused.

## What this means
Radarr refuses to enrich metadata from TMDB/TheMovieDB when the SkyHook metadata endpoint is unreachable. This is an upstream connectivity issue, not a local API key problem. The local API works fine for most operations; only metadata lookups fail.

## Workaround
1. Resolve the TMDB ID via an alternate source.
2. Add the movie using `tmdbId` in the POST payload.
3. Expect add-by-`tmdbId` can still fail with 500 if Radarr insists on fetching metadata at creation time during the outage.
4. If it still fails, report:
   - TMDB ID
   - title/year
   - intended `qualityProfileId`
   - intended `rootFolderPath`
   and fall back to UI manual add.

## Verified facts for this environment
- Radarr base URL: `http://127.0.0.1:7878`
- Quality profile `HD-1080p`: `qualityProfileId = 4`
- Root folder `Movies_6`: `/mnt/8000_Seagate/Movies_6`

## Error signature
- Exception term: `SkyHookException`
- Host refused: `api.radarr.video:443`
- Endpoints affected: `/api/v3/movie/lookup`, and indirectly `/api/v3/movie`