# Tasks

## 1. Places before excursions

- [x] 1.1 In `site/templates/day.html`, move each stop's places block (`{% if s.place_groups %}` ... `</details>`) above its excursions block, keeping both after the port description; verify with a new test in `site/tests/test_day_pages.py` that on day 4 the `class="places"` element comes after `class="prose about"` and before the "Shore excursions" heading
- [x] 1.2 Cover the multi-stop and no-places cases; verify with tests that on day 9 Galway's places precede Galway's excursions and the Cliffs of Moher stop renders places without an excursions heading, and that a fixture stop with excursions but no places renders excursions straight after the description

## 2. Price only in expanded details

- [x] 2.1 In `site/sitegen/trip.py`, build the excursion `summary` from duration and activity level only; keep `price_label` in the facts list ("Starting at"); verify with a test that no day 4 `<span class="exc-meta">` contains a `$`, and that the Giant's Causeway details body still contains "Starting at" and "$179"
- [x] 2.2 Update the existing `test_day4_excursions_collapsed` assertions if they depend on the old summary format, and run the full suite with `uv run --with pytest --with-requirements site/build.py pytest site/tests`; verify all tests pass

## 3. Check in the browser

- [x] 3.1 Rebuild with `uv run site/build.py`, serve `_site/`, and check day 4 and day 9 at phone width (375 px) and desktop width: Places sits above Shore excursions, collapsed rows show no price, and expanding an excursion shows "Starting at" with its price; verify there are no console errors

## Workflow follow-up

- Commit and push to `main` to redeploy the site, then confirm the live day 4 page shows the new layout after the "Updated, reload" prompt.
- Archive the change once it is deployed.
