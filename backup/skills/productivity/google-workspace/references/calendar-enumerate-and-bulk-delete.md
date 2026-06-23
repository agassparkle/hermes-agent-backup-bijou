# Calendar: enumerate by name, list events, bulk delete

The bundled `google_api.py` only exposes `calendar list|create|delete` — there
is no `calendar calendars` subcommand. When the user refers to a non-primary
calendar by name, use the direct API pattern below. Documented from a real
session where the user asked "can you see the events in calendar named
'Esnek ile Gevşek'?"

## Enumerate calendars

```python
import sys
sys.path.insert(0, '/home/agas/.hermes/skills/productivity/google-workspace/scripts')
from google_api import build_service

cal = build_service('calendar', 'v3')
result = cal.calendarList().list().execute()
for c in result.get('items', []):
    print(c['summary'], '|', c['id'])
```

Returns each calendar's display name (`summary`) and ID. Use the ID
(not the name) for all subsequent `events()` calls.

## Diacritic gotcha

The Calendar API returns display names with **ASCII-folded diacritics** by
default. A user-created calendar named "Esnek ile Gevşek" comes back as
"Esnek ile Gevsek". Never match on the user's literal spelling — list first,
print the actual `summary`, and ask for confirmation if there's ambiguity.

## List events with expanded window

Default `events().list()` only spans 7 days forward from "now". For "all
events" queries, expand explicitly:

```python
from datetime import datetime, timedelta

now = datetime.utcnow()
start = (now - timedelta(days=30)).isoformat() + 'Z'
end   = (now + timedelta(days=365)).isoformat() + 'Z'

events = cal.events().list(
    calendarId=CAL_ID,
    timeMin=start, timeMax=end,
    maxResults=250,
    singleEvents=True,        # expand recurring events
    orderBy='startTime',      # chronological
).execute()
```

`singleEvents=True` is required to get individual instances of recurring
events; otherwise you get one RRULE blob per series.

## Bulk delete with confirmation gate

When the user says "delete all X", **never delete inline**. Print the full
list with indices/counts and ask for explicit "yes" first. Then loop:

```python
for eid, title in matching_ids:
    try:
        cal.events().delete(calendarId=CAL_ID, eventId=eid).execute()
    except Exception as ex:
        failed.append((title, str(ex)))
```

`events().delete()` is irreversible — there is no "trash" concept for
calendar events (unlike Drive's trash). Make this clear in the confirmation
prompt.

## Telegram output gotcha

Long Markdown tables (15+ rows) frequently get truncated in Telegram,
causing the user to reply "prompt not finished" multiple times. For
multi-row results:

- Print count + first 10–15 + "...and X more"
- Or split across multiple shorter messages
- For destructive confirmations, ALWAYS show the full list (better to
  truncate the intro than the deletion preview)

## Bulk CREATE from external data (cinema release calendars, sports, etc.)

The bulk-delete gate above covers the destructive case. The **create** case
is symmetric — same confirmation gate, opposite direction. When the user
asks to add many events from an outside source (cinema vizyon takvimi,
sports fixtures, conference schedules), the workflow is:

1. **Confirm target calendar by ID** — list first, get exact `summary`, use
   the `id` (not the name) for inserts. The user may spell the name with
   diacritics (e.g. "Esnek ile Gevşek") but the API returns the
   ASCII-folded form ("Esnek ile Gevsek").
2. **Source the data** — for Turkey cinema releases see
   `references/turkish-cinema-vizyon-data.md` (Beyazperde scraping
   pattern).
3. **Filter & dedup by date range** — many calendar pages pull in
   sidebar content from old library entries. Always filter to the
   user's actual date range before showing.
4. **Show the FULL list BEFORE any write** — the user has explicitly
   stated "show me the list before you add". Match each event to its
   date and present as a table grouped by date. Ask which fields to
   include (title, description, location, reminders).
5. **All-day events for calendar-style releases** — Turkish vizyon
   takvimi releases are always on Fridays, no specific showtime. Use
   `date` (not `dateTime`) and put one event per film per date. End
   date MUST be > start date for all-day events:

   ```python
   from datetime import date, timedelta

   iso = '2026-06-19'
   event = {
       'summary': 'Oyuncak Hikayesi 5',
       'description': 'Toy Story 5\nhttps://www.beyazperde.com/...',
       'start': {'date': iso},
       'end':   {'date': (date.fromisoformat(iso) + timedelta(days=1)).isoformat()},
       'reminders': {
           'useDefault': False,
           'overrides': [{'method': 'popup', 'minutes': 24*60}],  # 1 day before
       },
   }
   cal.events().insert(calendarId=CAL_ID, body=event).execute()
   ```

6. **For 50+ events, batch the inserts**:

   ```python
   batch = cal.new_batch_http_request()
   for film in films:
       batch.add(cal.events().insert(calendarId=CAL_ID, body=build(film)))
   batch.execute()
   ```

7. **Report counts**: inserted / skipped (duplicate) / failed (with the
   failure reason for each).
