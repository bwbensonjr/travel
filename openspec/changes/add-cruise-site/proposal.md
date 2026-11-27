# Proposal

## Why

Several family members are going on the June 2027 Ireland cruise. The itinerary, day details, excursions and map now live as Markdown, CSV and GeoJSON in a private repository that only one person can open. A simple shared website would let everyone browse the same information before the trip and look things up on a phone during the cruise, where ship internet is slow, expensive or unavailable.

## What Changes

- Publish a static website from this repository with GitHub Pages, at an unlisted public URL that is excluded from search engines.
- The trip's home page is the interactive map of the route, ports and excursion places, next to a list of the 12 days.
- Add one page per cruise day, generated from the existing data. Each shows the port, times, port notes and description, the places to see, and the shore excursions. Each excursion opens to show its full details.
- Map pop-ups and the day list link to the day pages on the site instead of to raw Markdown files.
- Make the site installable on a phone's home screen. After the first visit, every day page and excursion detail works offline. The interactive map still needs a connection and says so when offline.
- Generate the site from the repository's existing data files with a build script. A GitHub Actions workflow builds and deploys it on every push to `main`.
- Add a site-level landing page that lists trips, so later trips can be added without changing the URL structure.
- Use one shared set of design tokens (color, type, spacing, light and dark themes) that follows `docs/ui-design-principles.md`.

Out of scope for this change, but the structure should leave room for them later:
- Family-specific plans: who booked which excursion, meeting points, flights and hotels.
- A "today" view keyed to ship time during the cruise.
- Offline map tiles.
- Authentication or passphrase protection.

## Capabilities

### New Capabilities

- `site-publishing`: Building the static site from the repository data and deploying it to GitHub Pages. Covers URL structure, the trip index, search-engine exclusion and keeping personal data off the site.
- `trip-map`: The trip home page's interactive map: route, ports and places, the day list, filters, and links into day pages.
- `day-pages`: The per-day detail pages: port facts, port description, places, and shore excursions with expandable details.
- `offline-access`: Installing the site as a home-screen app, caching pages for offline reading, and how the site behaves when there is no connection.

### Modified Capabilities

None. The project has no existing specs.

## Impact

- **New files:**
  - a site build script in the repository
  - shared site templates, styles and scripts
  - a service worker and web app manifest
  - a GitHub Actions workflow for Pages deployment
- **Existing data reused as-is:** `2027-ireland/places.geojson`, `2027-ireland/excursions.csv`, and the `day-*.md` files.
- **Existing files that change:** `2027-ireland/map.html` and `map-data.js` are superseded by the site's map page. The `.md` files stay the source for repository browsing and research notes.
- **New dependency:** Leaflet is served from the site itself instead of a CDN, so it can be cached for offline use. Map tiles still come from OpenStreetMap.
- **Repository settings (manual steps):**
  - GitHub Pages needs either a public repository or a paid plan. The repository is private today.
  - Making it public exposes every committed file. The only personal detail found is a first name in `jens-ireland-cruise-itinerary.docx`.
  - Pages must be set to deploy from GitHub Actions.
