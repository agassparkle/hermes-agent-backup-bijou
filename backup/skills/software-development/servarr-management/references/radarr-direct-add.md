# Radarr direct-add fallback (verified pattern)

Use this only when the normal `POST /api/v3/movie` path fails because Radarr cannot reach its upstream metadata service during add.

## What happened in this session
- Local Radarr API was reachable at `http://127.0.0.1:7878`.
- `GET /api/v3/system/status` returned `200`.
- `GET /api/v3/movie/lookup?term=Digger%202026` returned `503` once, then TMDb lookup was used externally to identify the movie.
- `POST /api/v3/movie` failed with `500` and the message `Connection refused (api.radarr.video:443)`.
- A verified local DB fallback succeeded by inserting matching rows into `MovieMetadata` and `Movies` in one transaction.
- The resulting item was then confirmed via `GET /api/v3/movie`.

## Safe decision tree
1. Check `/api/v3/system/status`.
2. Query `/api/v3/rootfolder` and `/api/v3/qualityprofile`.
3. Try `/api/v3/movie/lookup?term=<title year>`.
4. Try `POST /api/v3/movie`.
5. If the POST fails specifically because Radarr cannot reach its upstream metadata source, consider the DB fallback *only if*:
   - the local database is accessible,
   - the schema matches what you expect,
   - and you can verify the item afterward through the API.

## Schema notes from this install
Current SQLite tables used by the fallback:
- `MovieMetadata`
- `Movies`

Useful columns observed:
- `MovieMetadata`: `Id`, `TmdbId`, `ImdbId`, `Images`, `Genres`, `Title`, `SortTitle`, `CleanTitle`, `OriginalTitle`, `CleanOriginalTitle`, `OriginalLanguage`, `Status`, `LastInfoSync`, `Runtime`, `InCinemas`, `PhysicalRelease`, `DigitalRelease`, `Year`, `SecondaryYear`, `Ratings`, `Recommendations`, `Certification`, `YouTubeTrailerId`, `Studio`, `Overview`, `Website`, `Popularity`, `CollectionTmdbId`, `CollectionTitle`, `Keywords`
- `Movies`: `Id`, `Path`, `Monitored`, `QualityProfileId`, `Added`, `Tags`, `AddOptions`, `MovieFileId`, `MinimumAvailability`, `MovieMetadataId`, `LastSearchTime`

## Minimal fallback recipe
- Insert `MovieMetadata` first.
- Insert `Movies` referencing the new metadata row.
- Use a valid path under an accessible root folder.
- Keep `AddOptions` and `Tags` JSON-formatted.
- Set `Monitored` and `MinimumAvailability` deliberately.
- Commit both rows together.

## Verification checklist
After the write:
- `GET /api/v3/movie` contains the new title.
- The record shows the expected year and TMDb ID.
- Root folder and profile match the intended values.
- The movie is not duplicated.

## Pitfalls
- Do not guess IDs.
- Do not leave the DB write unverified.
- Do not use the fallback when the API add path works.
- Do not store API keys or other secrets in the DB recipe or skill files.
