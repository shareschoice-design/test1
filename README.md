# Competitor monitoring and scorecard

This repository contains a lightweight static dashboard for competitor monitoring in the Czech retail electricity and gas market.

## Dashboard

Open `index.html` through GitHub Pages or a local web server (for example `python -m http.server`) so the browser can fetch the JSON files. The dashboard reads `competitor_matrix.json`, `competitor_scorecard.json`, and `scorecard_history.json`.

It includes an average-score bar chart, a score heatmap, and a selectable-dimension timeline. The history file currently contains one initial baseline snapshot only, so the timeline will show meaningful change after subsequent dated snapshots are added. No earlier values have been fabricated.

The news and job feeds show a rolling two-calendar-month window ending on the dashboard's `as_of` date. Job posting dates come from Jobs.cz search results; `observed_at` records when the listing was checked, and the listing's current availability should be verified before use. A company with no matching job result is not necessarily inactive.

## Updating the timeline

After reviewing the scorecard, append a new dated entry to `scorecard_history.json` using the same structure as the baseline. Add the exact scores for each company and dimension; use `null` for `NA`. Keep old snapshots so the dashboard can compare changes over time.

## Caution

The scorecard contains preliminary directional ratings, not a verified ranking. Check the `methodology` and `limitations` in `competitor_scorecard.json` before relying on scores.
