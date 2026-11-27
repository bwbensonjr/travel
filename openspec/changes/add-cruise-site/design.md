# Design

## Context

See proposal.md for motivation. Current state of `2027-ireland/`:

- **`day-NN-*.md`:** 12 files. Each has YAML front matter (day, date, stops with port code, times, flags and excursion count), then a consistent body. That body has a stop table, `## About <port>`, `## Shore Excursions (N)` with a summary table, and one `###`/`####` section per excursion: a facts table, including Excursion ID, then the description.
- **`excursions.csv`:** 131 excursions with price, duration, activity level, wheelchair access, meals, minimum age and source URL.
- **`places.geojson`:** 9 route legs, 10 port features (with `calls`), and 327 place features (day, category, excursion IDs, visit, note, `location_check`). It also has a top-level `days` member listing every day and its stops.
- **`map.html` + `map-data.js` + `scripts/build_map_data.py`:** a working single-file Leaflet map that loads Leaflet from cdnjs. Its links point at the `.md` files.

Constraints:
- **Repository:** private today. Pages must deploy from GitHub Actions.
- **Phones:** family use phones on ship Wi-Fi.
- **UI guidelines:** `docs/ui-design-principles.md` applies. Use tokenized styles, minimal text, progressive disclosure, WCAG contrast, and light and dark themes.

## Goals / Non-Goals

**Goals:**
- The site builds from committed data with one command, locally and in CI.
- No framework or bundler on the client. Plain HTML, CSS and a small amount of JavaScript keep it fast on slow links and easy to maintain.
- Adding a second trip later means adding a data directory and one config entry.

**Non-Goals:**
- **Offline map tiles:** prefetching OpenStreetMap tiles in bulk is against OSM's tile usage policy, and a self-hosted tile set is a separate project.
- **Client-side search across trips:** not needed yet.
- **Editing in the browser and per-user state:** both arrive later with family plans.
- **Changing the scraped source data or the day Markdown format:** the site reads them as they are.

## Decisions

### 1. Python static generator run with `uv`
The source is a `site/build.py` script with PEP 723 inline dependencies: Jinja2 for templates, Python-Markdown for prose and PyYAML for front matter. It runs as `uv run site/build.py` and writes to `_site/`. Templates go in `site/templates/` and static assets in `site/static/`.

- **Why:** The repository already uses Python scripts, and the user's tooling prefers `uv`. Inline metadata keeps the dependency list next to the script without a separate project file.
- **Alternatives considered:**
  - Jekyll, which GitHub Pages runs natively. Rejected: Liquid makes it awkward to join the GeoJSON, CSV and Markdown data, and it gives less control over the service worker and the precache list.
  - A Node framework such as Eleventy or Astro. Rejected: it adds a second toolchain for a small site.
  - Hand-written HTML. Rejected: it would duplicate data.

### 2. Data sources and parsing
- **Day facts:** front matter in the day Markdown.
- **Excursion facts:** `excursions.csv`, keyed by ID.
- **Places, route and ports:** `places.geojson`.
- **Prose:** port descriptions and excursion descriptions are parsed from the day Markdown body. The parser splits on the known headings and reads the Excursion ID row from each excursion's facts table. Prose is rendered to HTML with Python-Markdown.
- **Extra headings:** any other sections a person later adds to a day file, such as research notes, are rendered as an extra "Notes" block. Future research appears on the site automatically.
- **Validation:** the build fails if:
  - a day file is missing
  - an excursion ID in the Markdown or the GeoJSON is not in the CSV
  - a CSV excursion does not appear in its day file
- **Why:** these files are the current source of truth. A separate JSON export would be a second copy that could drift.
- **Alternative considered:** re-scraping Holland America in CI. Rejected: it isn't reproducible and the site could break.

### 3. Site layout and URLs
```
/                         trip list (from site/site.yaml)
/2027-ireland/            map home
/2027-ireland/day/3/      day page
/2027-ireland/day/3/#exc-53205   excursion deep link
/2027-ireland/?place=d3-calanais-standing-stones   map deep link
/2027-ireland/trip.json   map data (GeoJSON + excursions)
/offline/                 offline fallback
/sw.js, /manifest.webmanifest, /robots.txt
```
- **Excursion anchors:** these use the excursion ID, which makes them unique even when two excursions share a title.
- **Place IDs:** these are `d<day>-<slug(name)>`, derived at build time. They stay stable while the name is unchanged.
- **`site/site.yaml`:** lists each trip's slug, title, dates and data directory.

### 4. Map page reuses the existing Leaflet code
The current `map.html` logic is split into `site/static/map.js`, which fetches `trip.json`, and a Jinja template that shares the site's tokens and header.

- **Leaflet:** 1.9.4 is vendored into `site/static/vendor/leaflet/`, with its license and version noted, instead of being loaded from cdnjs. That lets the service worker precache it and removes a third-party dependency.
- **Links:** pop-up links change from `.md` files to day page URLs and excursion anchors.
- **Offline notice:** the map shows it when the tile layer reports errors and `navigator.onLine` is false.
- **Alternative considered:** keeping the CDN. Rejected: offline loads of the page would fail before the offline notice could render.

### 5. Day pages use native disclosure
- **Disclosure:** each excursion is a `<details>` element. The `<summary>` holds the title, price, duration and activity level, and the body holds the full facts and description. This works without JavaScript and is accessible.
- **Deep links:** a few lines of script open the `<details>` targeted by the URL fragment.
- **Places:** each place links to `../../?place=<id>`.
- **Alternative considered:** a separate page per excursion. Rejected: more pages to cache and more navigation on a phone, where opening the item in place is quicker.

### 6. Hand-written service worker with a build-versioned precache
- **Precache list:** the build writes `sw.js` with a list of every output file for the trip (HTML, CSS, JS, `trip.json`, icons, Leaflet). It also writes a version string made from a hash of those files' contents.
- **Install:** the service worker caches the full list under `trip-cache-<version>`.
- **Serving:**
  - Pages and assets are served cache-first.
  - Map tiles and other cross-origin requests go to the network only.
  - A navigation that misses the cache falls back to `/offline/`.
- **Updates:** a redeploy changes the bytes of `sw.js`, so the browser installs the new worker on the next online visit. It activates with `skipWaiting` and `clients.claim`, deletes old caches, and shows "Updated" on the page.
- **Offline indicator:** the page asks the service worker whether the current version's cache is complete.
- **Alternative considered:** Workbox. Rejected: it adds a build dependency and abstraction for roughly 80 lines of worker code.

### 7. Design tokens and theming
- **Tokens:** `site/static/tokens.css` defines color, type scale, spacing scale, radius and the map's category palette as CSS custom properties. It has light values and dark values, the dark ones under `prefers-color-scheme: dark`.
- **Usage:** components use only tokens.
- **Contrast:** text pairs are checked against WCAG AA (4.5:1 for body text) in both themes.
- **Fonts:** none are loaded; the system font stack is used.

### 8. Deployment via GitHub Actions
`.github/workflows/pages.yml` runs on pushes to `main` and on manual dispatch. It:
1. checks out the repository
2. installs `uv`
3. runs the build
4. uploads `_site/` with `actions/upload-pages-artifact`
5. deploys with `actions/deploy-pages`

The build step fails the job on validation errors, so nothing is deployed. The job also runs `pytest` on the parser and validation tests.

- **Alternative considered:** committing the built output to a `gh-pages` branch. Rejected: generated files in history, and an extra step to remember.

### 9. Privacy controls
The build copies only an allowlist (generated pages, `site/static/`, the trip JSON) into `_site/`. Every template includes `<meta name="robots" content="noindex, nofollow">`. This tag is the effective control: under the default project URL (`/travel/`), crawlers only read `robots.txt` at the host root. The site still ships a `robots.txt` that disallows all crawling, which takes effect if a custom domain is added.

### 10. Retire the standalone map
`2027-ireland/map.html`, `map-data.js` and `scripts/build_map_data.py` are removed once the site map works. `itinerary.md` links to the published site instead. `places.geojson` remains the source of map data.

## Risks / Trade-offs

- **[Markdown parsing breaks when a day file is hand-edited]** → The parser keys only on the generated headings and the Excursion ID row, unknown sections become Notes, and the build fails loudly with the file and line rather than silently dropping content.
- **[Public site at a guessable URL]** → It is excluded from search engines and contains no personal data. Anyone with the link can still view it, which the user accepted.
- **[Making the repository public exposes its whole history]** → Before switching visibility, review `git log` and the tracked files. Known contents: scraped cruise data, a first name in a `.docx`, and a local preview config. Alternatively, keep it private on a paid plan.
- **[Stale cache shows outdated times on board]** → Every page shows a "data as of" build date, and updates apply on the next online visit.
- **[OSM tile policy and availability]** → Tiles load normally with attribution and no bulk prefetch. The day pages carry all the essential information without the map.
- **[iOS storage eviction of unused PWA caches]** → Opening the site within the last few days before departure refreshes the cache, which the offline indicator confirms. The README tells family to open it the day before.

## Migration Plan

1. Build and verify the site locally (`uv run site/build.py`, then serve `_site/`).
2. Repository owner decides on visibility: make the repository public after a review of tracked files and history, or upgrade the plan. Then set Settings → Pages → Source to "GitHub Actions".
3. Merge to `main`. The workflow deploys, and the deployment URL is shared with family.
4. Remove the standalone map files in the same change once the deployed map is confirmed.
5. **Rollback:** re-run the Pages workflow on an earlier commit, or disable Pages in repository settings. The source data is unaffected.

## Open Questions

- Custom domain versus the default `bwbensonjr.github.io/travel/` URL. Either works with the URL structure; the build uses relative links so the base path does not matter.
- Exact icon artwork for the home-screen app. A simple generated mark is fine to start.
