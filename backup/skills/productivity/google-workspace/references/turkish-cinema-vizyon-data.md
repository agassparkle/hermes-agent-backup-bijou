# Turkish cinema vizyon takvimi — Beyazperde scraping

When the user asks for "all movies releasing in Turkey" or to populate a
calendar from the TR cinema release schedule, the canonical source is
**Beyazperde.com** (the TR allocine/filmstarts sibling).

## Why Beyazperde, not paribucineverse / boxofficeturkiye

| Source | Pros | Cons |
|--------|------|------|
| **beyazperde.com/filmler/takvim/** | Full weekly grid, all dates to 2027, structured HTML, no auth | Dates loaded via JS-encoded dropdown |
| paribucineverse.com/gelecek-filmler | Simple list | ~20 items, no dates past late August 2026 |
| boxofficeturkiye.com/takvim/ | Authoritative | Login-walled, JS-rendered, inaccessible without session |
| sinemalar.com/filmler/pekyakinda | Has dates | Layout inconsistent, scattered across pages |

Beyazperde is the only one with a clean full-week grid that scrapes
deterministically with `urllib`.

## The base64-encoded date trick

The takvim page dropdown looks like a normal `<select>`:

```html
<option value="ACrL2ZACrpbG1sZXIvdGFrdmltL3dlZWstMjAyNi0wNi0xOS8=">19 Haziran 2026</option>
```

But each `value` is a base64-encoded path. The decode needs a 2-char
prefix `"ab"` prepended first — without it you get "Invalid base64"
because the string is 49 chars (needs 52 for a multiple of 4):

```python
import base64, re

sample = 'ACrL2ZACrpbG1sZXIvdGFrdmltL3dlZWstMjAyNi0wNi0xOS8='
decoded = base64.b64decode('ab' + sample).decode('utf-8', errors='ignore')
# Strip control chars from the padding
clean = ''.join(c for c in decoded if c.isprintable())
# -> 'ab*lmler/takvim/week-2026-06-19/'
# Strip the leading garbage
m = re.search(r'(filmler/takvim/week-\d{4}-\d{2}-\d{2}/)', clean)
# -> 'filmler/takvim/week-2026-06-19/'
```

So the URL is `https://www.beyazperde.com/filmler/takvim/week-YYYY-MM-DD/`
(NO leading slash — the path is relative). Iterate over the 132 dropdown
options (March 2026 → June 2027) and filter to the date range the user
asks for.

## Parsing a week page

Each film is a card anchored by `<h2 class="meta-title">`. The most
reliable fields:

```python
blocks = re.split(r'<h2 class="meta-title">', html)
for blk in blocks[1:]:
    title_m  = re.search(r'<a[^>]+>([^<]+)</a>', blk)
    date_m   = re.search(r'<span class="date">([^<]+)</span>', blk)
    orig_m   = re.search(r'Orijinal adı\s*</[^>]+>\s*([^<\n]+)', blk)
    # genres: any of the known list
    genres_m = re.findall(r'>(Aile|Animasyon|Komedi|Aksiyon|Gerilim|'
                          r'Macera|Dram|Korku|Bilim Kurgu|Fantastik|'
                          r'Dedektif|Romantik|Belgesel|Savaş|Tarih|'
                          r'Gizem|Suç|Müzikal)<', blk)
```

## Gotcha: sidebar pulls in old library entries

The week page includes a "currently in theaters" sidebar with old movies
(Matrix from 1999, Avengers: Endgame from 2019, etc.). **Always filter
to the user's actual date range** before showing — otherwise you'll
present 60+ "releases" that include re-releases and library titles.

```python
MONTHS = {"Ocak":1,"Şubat":2,"Mart":3,"Nisan":4,"Mayıs":5,"Haziran":6,
          "Temmuz":7,"Ağustos":8,"Eylül":9,"Ekim":10,"Kasım":11,"Aralık":12}
def parse_tr(s):
    d, m, y = s.split()
    from datetime import date
    return date(int(y), MONTHS[m], int(d))

start = date(2026, 6, 19)
end   = date(2026, 10, 31)
filtered = [f for f in films if start <= parse_tr(f['date']) <= end]
```

## Output shape — confirmed for "Esnek ile Gevsek" calendar

For the user's "Esnek ile Gevsek" calendar (id
`3drf7ff25s8cr7dsnkccjltbfc@group.calendar.google.com`), the expected
post-filter count for "19 Haziran – 31 Ekim 2026" was **65 unique films
across 21 Friday release dates**. The October 30 week has no scheduled
release — leave it empty.

## Getting English (original) titles — TWO sources, use both

The week-page card parser only catches "Orijinal adı" when TR title
differs from the original. For films where the Turkish release title
IS the English title (e.g. *Moana*, *Supergirl*, *The Odyssey*,
*Spider-Man: Brand New Day*, *Street Fighter*, *Resident Evil*,
*Coyote vs Acme*, *Animal Farm*, *Verity*, *Digger*, *Other Mommy*,
*Clayface*, *Gupi*, *Wife And Dog*, *Groove Tails*, *The Red Mask*,
*Ustoppelig*, *River*, *Super Troopers 3*, *Fall*, *Fall 2*,
*Charlie Harper*, *Victorian Psycho*, *7 Dogs*, *Normal*, *Cinhar*,
*Dakhul*, *Her Private Hell*, *The Social Reckoning*, *Sense and
Sensibility*, *Yugly*, *Are You There?*, *The Birthday Party*),
the field is OMITTED — leaving you with the Turkish title only.

Fallback: hit each film's detail page (`/filmler/film-XXXXX/`) and pull
the English name from the OG meta tag, which is always populated:

```python
om = re.search(r'og:title"\s*content="([^"]+)"', html)
# og:title for /filmler/film-314942/ -> "Moana"
```

Order of attempts per film detail page:
1. `Orijinal\s*ad[ıi]\s*</span>\s*<span[^>]*>([^<]+)</span>` — present when TR ≠ original
2. `og:title"\s*content="([^"]+)"` — always present, gives canonical English title

For some Turkish-only titles (e.g. *Mecruh: Cin Mührü*, *Tadeo Jones y la
lámpara maravillosa*, *Cin Hikayeleri: Zulman*, *Dondurmam Gaymak: Gapital*,
*Kuzular Firarda: Gizemli Canavar*) even `og:title` returns the local
title. Accept this — these films genuinely have no English release name
in Beyazperde's database.

If the user wants **English names only** for the calendar events, run
the lookup. If they're fine with TR titles, skip it (saves ~65 detail-page
fetches and ~10s wall time).

## HTML entity cleanup in titles

Beyazperde titles contain raw HTML entities that look ugly in a calendar
event summary. Always run:

```python
title = title.replace('&#039;', "'").replace('&amp;', '&')
```

Known offenders in the 2026 vizyon dataset: `Minions &amp; Monsters`,
`Robin Hood&#039;un Ölümü`, `Oak Caddesi&#039;nin Sonu`.

## Bulk add workflow — confirm BEFORE adding

The user pattern: "add all releases to my calendar" → fetch → show full
list with date groupings → **wait for explicit "yes"** → bulk POST.

Always:
1. Filter to the date range FIRST (drop sidebar/library contamination).
2. Dedup by (date, title) — Beyazperde occasionally lists the same film
   twice within a week page.
3. Present the list as a Telegram-safe table (under ~15 rows per message;
   split if larger — Rule 6 of the parent skill).
4. After "yes", POST in a single `execute_code` loop using the same
   `~/.hermes/google_token.json` access token. Don't make 65 separate
   API calls — the loop runs in ~40s end-to-end.
5. Report success: added/total, error count, link to calendar.

All-day event payload shape (start.date / end.date = next day):

```python
payload = {
    "summary": title,
    "description": f"TR: {tr}\nOriginal: {en}\nhttps://www.beyazperde.com{url}",
    "start": {"date": d.isoformat()},           # e.g. "2026-07-17"
    "end":   {"date": (d + timedelta(days=1)).isoformat()},
    "reminders": {"useDefault": False, "overrides": [
        {"method": "popup", "minutes": 24 * 60}  # 1 day before
    ]}
}
```

Turkish vizyon releases are **always Fridays** — `parse_tr(d).weekday() == 4` is a useful sanity check.

## When to use this skill

- "Add all Turkey movie releases to my calendar"
- "What's playing next month in Turkish cinemas"
- "Schedule the TR release calendar"

Do NOT use this skill for:
- Streaming releases (Netflix/Disney+ has its own release surface, not
  in Beyazperde)
- Festival lineups (Antalya Altın Portakal etc. — separate sources)