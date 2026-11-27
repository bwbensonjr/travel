# site-publishing Specification

## Purpose

Turns the trip data kept in this repository into a static website on GitHub Pages, so family members can open it from a link without repository access.

## Requirements

### Requirement: Site is generated from repository data
The site SHALL be generated only from data files committed in the repository: the trip's GeoJSON places file, excursion CSV, and per-day Markdown files. Content SHALL NOT be copied into the site by hand.

#### Scenario: Data change appears on the site
- **WHEN** a place is edited in `places.geojson` and the site is rebuilt
- **THEN** the map and the matching day page show the edited place

#### Scenario: Build fails on broken data
- **WHEN** a place references an excursion ID that is not in the excursion CSV
- **THEN** the build stops with an error naming the place and the missing ID, and nothing is deployed

### Requirement: Automatic deployment from main
A push to the `main` branch SHALL rebuild the site and deploy it to GitHub Pages without manual steps.

#### Scenario: Push deploys
- **WHEN** a commit that changes trip data is pushed to `main`
- **THEN** the published site reflects the change after the deployment workflow finishes

#### Scenario: Failed build leaves site unchanged
- **WHEN** the build fails for a pushed commit
- **THEN** the previously deployed site stays available and the workflow run is marked failed

### Requirement: Local preview
A person maintaining the site SHALL be able to build and view it locally with one documented command, without deploying.

#### Scenario: Local build
- **WHEN** the documented build command is run in a clone of the repository
- **THEN** a complete site is written to a local output directory that can be served and browsed

### Requirement: Stable URL structure
The site SHALL use a root landing page that lists trips, one path per trip (such as `/2027-ireland/`), and one path per day under the trip (such as `/2027-ireland/day/3/`). Paths are relative to the site root, which may itself sit under a project path such as `/travel/`. Paths SHALL stay the same when content is rebuilt.

#### Scenario: Trip and day URLs
- **WHEN** a family member opens the site root
- **THEN** they see a list of trips that includes the 2027 Ireland cruise, linking to its trip path

#### Scenario: Shared day link
- **WHEN** someone shares the URL of a day page and the site is later rebuilt
- **THEN** the same URL still opens that day's page

### Requirement: Excluded from search engines
Every page SHALL tell search engines not to index it, and the site SHALL publish a robots file at the site root that disallows crawling.

#### Scenario: Pages are marked no-index
- **WHEN** any generated page is fetched
- **THEN** its HTML carries a robots meta tag with `noindex, nofollow`

#### Scenario: Robots file
- **WHEN** `robots.txt` at the site root is fetched
- **THEN** it disallows all crawling for all user agents

### Requirement: No personal data published
The site SHALL publish only cruise and destination information from Holland America and public sources, plus the derived map data. It SHALL NOT publish source documents such as `.docx` files, or anything naming family members.

#### Scenario: Source documents excluded
- **WHEN** the site is built
- **THEN** the output contains no `.docx` files and no files outside the generated pages, styles, scripts, data and images

### Requirement: Attribution and source links
The site SHALL credit OpenStreetMap for map tiles and data, and SHALL link each excursion to its Holland America source page.

#### Scenario: Map attribution visible
- **WHEN** the map is shown
- **THEN** an OpenStreetMap attribution link is visible on the map

#### Scenario: Excursion source link
- **WHEN** a family member opens an excursion's details
- **THEN** a link to the excursion's Holland America page is present
