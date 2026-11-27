# Travel site

Static site for sharing trip information with family, published with GitHub Pages. It is generated from the data files kept in each trip directory. Nothing on the site is edited by hand.

## Build and preview

Run all commands from the repository root. [`uv`](https://docs.astral.sh/uv/) installs the dependencies listed at the top of `site/build.py`.

```bash
uv run site/build.py
```

This writes the site to `_site/`, which git ignores. To preview it:

```bash
python3 -m http.server 8765 --directory _site
```

Then open <http://localhost:8765/>. The site must be served over HTTP, not opened as a file, because the map page fetches its data and the offline support needs a service worker.

Run the tests:

```bash
uv run --with pytest --with-requirements site/build.py pytest site/tests
```

## Layout

| Path | Purpose |
|---|---|
| `site/build.py` | Build entry point (dependencies declared inline) |
| `site/site.yaml` | Site title and the list of published trips |
| `site/sitegen/` | Data loading, day-file parsing, validation, rendering |
| `site/templates/` | Jinja2 page templates |
| `site/static/` | Styles, scripts, icons, vendored libraries |
| `site/tests/` | Tests and fixtures |

## Publishing

`.github/workflows/pages.yml` runs the tests and the build on every push to `main` and deploys `_site/` to GitHub Pages. If the tests or the build fail, nothing is deployed and the site already published stays as it was. You can also start the workflow by hand from the Actions tab.

### One-time repository setup

These steps are done by the repository owner in GitHub. They cannot be done from the code.

1. **Review what would become public.** GitHub Pages on a free plan needs a public repository. Making it public exposes every tracked file and the full git history, not only the site. Check both:

   ```bash
   git ls-files
   git log --stat
   ```

   At the time of writing, the only personal detail found is a first name in `2027-ireland/jens-ireland-cruise-itinerary.docx`.
2. **Choose one:**
   - make the repository public (Settings, General, Danger Zone, Change visibility), or
   - keep it private on a paid plan that allows Pages for private repositories.

   Either way, the published site is public to anyone with the link.
3. **Turn on Pages:** Settings, Pages, Build and deployment, Source: **GitHub Actions**.
4. **Deploy:** push to `main` (or run the workflow by hand), then share the URL from the workflow's deploy step with family. It is normally `https://<owner>.github.io/<repo>/`.

### Privacy

- Every page carries `<meta name="robots" content="noindex, nofollow">`, which keeps it out of search results.
- The site also ships a `robots.txt`, but crawlers only read that file at a domain's root. It takes effect only with a custom domain.
- The build copies only generated pages, `site/static/`, and the trip JSON into `_site/`. Source documents such as `.docx`, `.md` and `.csv` files are never published (a test checks this).

### Before the trip

Ask everyone to open the site on their phone, online, the day before departure, and to check that the header says **Available offline**. Phones, iOS in particular, can clear the saved copy of a site that hasn't been opened for a while. Adding it to the home screen (Share, then Add to Home Screen) makes it open like an app.

## Vendored libraries

| Library | Version | Location | Why vendored |
|---|---|---|---|
| Leaflet | 1.9.4 | `site/static/vendor/leaflet/` | Served from the site so the offline cache can store it. `VERSION` there records the npm tarball and checksum. |

Map tiles still load from OpenStreetMap, so the map itself needs a connection.

## Trip data

Each trip in `site.yaml` points at a data directory (e.g. `2027-ireland/`) containing:

| File | Used for |
|---|---|
| `places.geojson` | Day list (top-level `days`), route legs, port calls, places |
| `excursions.csv` | Excursion facts: price, duration, activity level, accessibility, source URL |
| `day-NN-*.md` | Port descriptions, excursion descriptions, and any notes you add |

### Day file format

The build reads the YAML front matter and these headings from each day file. For a day with one stop:

- `## About <port>`: the port description.
- `## Shore Excursions (N)`: the summary table under it is ignored.
- `### <excursion title>`: a facts table that must include an `| Excursion ID | ... |` row, followed by the description.

A day with several stops (day 9) uses a `## <stop name>` heading matching each front-matter stop. Under each one, the same sections appear one level deeper.

Any other heading starts a **note**, which is shown on the day page under "Notes". Add research under a new `## ...` heading at the end of a day file and it appears on the site after the next build.

### Validation

The build stops with a non-zero exit, deploying nothing, if:

- a day listed in `places.geojson` has no day file
- an excursion ID in a day file or in `places.geojson` is not in `excursions.csv`
- an excursion in `excursions.csv` is missing from its day file

Each error names the file (and line, for day files) and the ID.

### Editing map data

`places.geojson` is the source of map data. Places whose coordinates were not confirmed in OpenStreetMap have `"location_check": "approximate"`, and the map labels them as approximate. Each place gets a stable ID, `d<day>-<slug of name>`, which links from day pages to the map.
