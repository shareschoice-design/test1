# Competitor monitoring and scorecard

This repository contains a lightweight static dashboard for competitor monitoring in the Czech retail electricity and gas market.

## Dashboard

Open `index.html` through GitHub Pages or a local web server (for example `python -m http.server`) so the browser can fetch the JSON files. The dashboard reads the competitor matrix, scorecard, actions, news, jobs, regulatory signals, knowledge graph, sources, and scorecard history.

The action overview presents the recommended work as a step-by-step workflow with owner, due date, evidence links, and a defined deliverable. Checklist progress is stored in the browser's local storage on the current device; it is not synchronized or written back to the repository. Competitor cards separate directional assessments from collected signals. The scorecard includes a heatmap and average-score chart; scores remain unverified hypotheses, and no weighted winner is calculated.

The news and job feeds show a rolling two-calendar-month window ending on the dashboard's `as_of` date. Job posting dates come from Jobs.cz search results; `observed_at` records when the listing was checked, and the listing's current availability should be verified before use. A company with no matching job result is not necessarily inactive.

## Updating the timeline

After reviewing the scorecard, append a new dated entry to `scorecard_history.json` using the same structure as the baseline. Add the exact scores for each company and dimension; use `null` for `NA`. Keep old snapshots so the dashboard can compare changes over time.

## Caution

The scorecard contains preliminary directional ratings, not a verified ranking. Check the `methodology` and `limitations` in `competitor_scorecard.json` before relying on scores.

## YouTube dashboard (`yt-dashboard/`)

Automatic overview of all your YouTube channels: subscribers, views, public and non-public (private, unlisted, scheduled) videos, uploads and comments in the last 48 hours, 30-day YouTube Analytics and subscriber history.

- `yt-dashboard/connect.html` – one-time setup wizard (Google OAuth client, connect each channel, copy one secret to GitHub).
- `.github/workflows/youtube-dashboard.yml` – runs every hour, executes `yt-dashboard/fetch.py` (Python stdlib only) with the `YT_DASHBOARD` secret and force-pushes the encrypted result to the `yt-data` branch (always a single commit).
- `yt-dashboard/index.html` – the dashboard; loads `data.enc` from the `yt-data` branch and decrypts it in the browser with your password (AES-256-CBC, PBKDF2-SHA256, 100 000 iterations). The repository is public, so the data is only ever stored encrypted.

The OAuth app must be set to "In production" in Google Cloud, otherwise Google revokes access after 7 days. If a channel shows "připojit znovu", reconnect it in `connect.html` and update the secret.
