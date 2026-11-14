# Competitor Monitoring Repo

This repository is a lightweight static tracker for monitoring competitor activity in the Czech retail electricity and gas market, with focus on:

- competitor news
- job postings
- regulatory updates
- source tracking

## Structure

- `index.html` — dashboard for browsing all records
- `sources.json` — official news, career, and regulatory sources
- `data/news.json` — competitor news items
- `data/jobs.json` — job postings and vacancies
- `data/regulatory.json` — regulatory updates
- `rodokmen.html` — existing file kept as-is

## Recommended workflow

1. Keep a list of official sources in `sources.json`.
2. Add new items to `data/news.json`, `data/jobs.json`, and `data/regulatory.json`.
3. Use `index.html` to review and analyze the latest developments.
4. Update records regularly with fields like:
   - company
   - title
   - publication_date
   - source_url
   - summary
   - tags

## Example record schema

### News

```json
{
  "company": "ČEZ Group",
  "title": "Q3 results update",
  "publication_date": "2026-11-11",
  "source_url": "https://www.cez.cz/en/media/press-releases",
  "summary": "Short summary of the item.",
  "tags": ["financials", "energy", "retail"]
}
```

### Jobs

```json
{
  "company": "PRE",
  "title": "Customer Care Specialist",
  "published_at": "2026-11-08",
  "source_url": "https://www.pre.cz/kariera/",
  "location": "Praha",
  "department": "Customer Operations",
  "summary": "Short summary of role."
}
```

### Regulatory

```json
{
  "authority": "OTE",
  "title": "Changes to DUFVO and DUFMO",
  "publication_date": "2026-11-11",
  "source_url": "https://www.ote-cr.cz/en/about-ote/news",
  "summary": "Summary of regulatory update.",
  "tags": ["market rules", "balancing"]
}
```

## Notes

The current data is a starter dataset and should be expanded with fresh scrapes or manual updates from official sources.
