# Tasks

## 1. Build scaffolding

- [x] 1.1 Create `site/` with `build.py` (PEP 723 inline deps: jinja2, markdown, pyyaml), `templates/`, `static/`, and `site.yaml` listing the 2027 Ireland trip (slug, title, dates, data dir); verify `uv run site/build.py` creates an empty `_site/` without errors
- [x] 1.2 Add `_site/` to `.gitignore` and verify `git status` stays clean after a build
- [x] 1.3 Add `site/tests/` with a pytest setup runnable via `uv run --with pytest --with-requirements site/build.py pytest site/tests`; verify an initial smoke test passes

## 2. Data loading and validation

- [x] 2.1 Implement loading of `places.geojson` (days, routes, ports, places) and `excursions.csv`, deriving stable place IDs `d<day>-<slug>`; verify with a test that 12 days, 10 ports, 9 legs and 327 places load and that place IDs are unique
- [x] 2.2 Implement the day Markdown parser: front matter, per-stop port description, excursions keyed by Excursion ID with description Markdown, and unknown sections captured as notes; verify with tests on day 3, day 9 (two stops, duplicate excursion titles) and a fixture with an extra notes section
- [x] 2.3 Implement build validation (missing day file, excursion ID in GeoJSON or Markdown absent from CSV, CSV excursion absent from its day file) that exits non-zero with the file and ID named; verify with tests using broken fixtures, and confirm the real data passes
- [x] 2.4 Document the data sources, the parser's heading expectations and the build command in `site/README.md`; verify the documented command runs as written

## 3. Design tokens and base layout

- [x] 3.1 Create `site/static/tokens.css` (color, type scale, spacing, radius, category palette; light and dark) and `base.css` following `docs/ui-design-principles.md`; verify body and muted text pairs meet WCAG AA 4.5:1 in both themes with a small contrast-check test
- [x] 3.2 Create the base Jinja template: header with trip title and back link, robots `noindex, nofollow` meta, manifest link, "data as of" build date, and offline status slot; verify a rendered page contains the meta tag and passes an HTML parse check
- [x] 3.3 Render the root trip list page from `site.yaml` and write `robots.txt` disallowing all crawling; verify `_site/index.html` links to `2027-ireland/` and `_site/robots.txt` content in a test

## 4. Day pages

- [x] 4.1 Render `/<trip>/day/<n>/` for all days with the summary first (day, date, port, arrive, depart, notes); sea days show "At sea" without times; verify tests for day 2 and day 5 summaries
- [x] 4.2 Render the port description and the places grouped by type, each linking to `../../?place=<id>`; verify the day 3 page lists Callanish under its type with a correct link
- [x] 4.3 Render excursions as `<details id="exc-<id>">` with a summary (title, price, duration, activity) and a body (all facts, description, Holland America link); verify day 4 renders 18 collapsed excursions and both day 9 Connemara entries have distinct IDs
- [x] 4.4 Add the fragment script that opens and scrolls to the targeted excursion, plus previous, next and map navigation; verify in a browser that `day/9/#exc-99011` opens that excursion, and that day 1 has no previous link and day 12 no next link
- [x] 4.5 Render the notes block for extra Markdown sections; verify with a fixture-based build test

## 5. Map page

- [x] 5.1 Vendor Leaflet 1.9.4 (JS, CSS, images, license) into `site/static/vendor/leaflet/`; verify the files are present and the version is noted in `site/README.md`
- [x] 5.2 Emit `/<trip>/trip.json` (GeoJSON with place IDs, days, excursions keyed by ID); verify a test loads it and finds every excursion referenced by places
- [x] 5.3 Port `2027-ireland/map.html` logic into `site/static/map.js` and a map template that uses the shared tokens; pop-up and day list links go to day page URLs and `#exc-<id>` anchors; verify in a browser that no link targets a `.md` file
- [x] 5.4 Support `?place=<id>` to zoom to a place and open its pop-up, and hide filters with no matching data; verify in a browser with the Giant's Causeway ID and confirm the wheelchair filter is hidden
- [x] 5.5 Show the "map needs a connection" notice when tiles fail while offline, keeping the day list usable; verify with the browser's offline mode
- [x] 5.6 Verify the phone layout at 375 px wide: no horizontal scroll, and the day list collapses to enlarge the map

## 6. Offline support and installability

- [x] 6.1 Generate `manifest.webmanifest` (name, start URL to the trip, standalone display, theme colors) and 192 px and 512 px icons; verify the manifest validates in browser devtools
- [x] 6.2 Generate `sw.js` from the build with the full precache list and a content-hash version; cache-first for site files, network-only for cross-origin; navigation miss falls back to `/offline/`; verify a test that the precache list includes every day page, `trip.json` and the Leaflet files
- [x] 6.3 Render the `/offline/` fallback page linking to the cached trip pages; verify it is in the precache list
- [x] 6.4 Register the worker from every page, show "Available offline" only once the current version's cache is complete, and show "Updated" after a new version activates; verify in a browser: load the map online, go offline, and open the day 10 page in full
- [x] 6.5 Verify updates: rebuild with a changed excursion price, reload online, and confirm the day page shows the new price while an offline load before that still shows the old one without errors

## 7. Deployment

- [x] 7.1 Add `.github/workflows/pages.yml` (push to main and manual dispatch: checkout, setup-uv, tests, build, upload-pages-artifact, deploy-pages) with Pages permissions; verify the workflow file passes `actionlint` or a dry review, and that a deliberately broken fixture fails the test step
- [x] 7.2 Verify the build output allowlist: `_site/` contains no `.docx`, `.md`, `.csv` or `scripts/` files
- [x] 7.3 Document the manual repository steps in `site/README.md`: review tracked files and history, then choose public visibility or a paid plan, then set Pages source to GitHub Actions; include the advice to open the site the day before departure; verify the README renders these steps

## 8. Retire the standalone map and integrate

- [x] 8.1 Remove `2027-ireland/map.html`, `map-data.js` and `scripts/build_map_data.py`, and update `2027-ireland/itinerary.md` and the root `README.md` to link to the site and the local build; verify no remaining references with `grep -r "map-data.js\|map.html"`
- [x] 8.2 Full local check: serve `_site/`, then walk trip list to map to day page to excursion to back, in light and dark themes on phone and desktop widths, with no console errors
- [ ] 8.3 After the repository owner completes the manual Pages setup, confirm the first workflow deploy succeeds and the public URL loads the trip map and a day page

## Workflow follow-up

- Archive the change after the site is deployed and reviewed by the repository owner.
