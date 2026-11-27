---
cruise: "11-Day Wild British Isles: Ireland & Cliffs of Moher"
line: "Holland America Line"
ship: "Zuiderdam"
itinerary_code: "E7N11A"
voyage_code: "U745"
embark: "2027-06-22"
disembark: "2027-07-03"
source: "https://www.hollandamerica.com/en/us/find-a-cruise/e7n11a/u745"
---

# 11-Day Wild British Isles: Ireland & Cliffs of Moher

Holland America Line, ms Zuiderdam. Round trip from Amsterdam, June 22 to July 3, 2027.

Source: <https://www.hollandamerica.com/en/us/find-a-cruise/e7n11a/u745>

> Journey from Amsterdam to the heart of Ireland and Scotland. Explore Dublin's lively waterfront and take in views of Glasgow's grand Victorian architecture.

## Day-by-day

| Day | Date | Port | Arrive | Depart | Notes | Excursions | Details |
|---|---|---|---|---|---|---|---|
| 1 | Jun 22, 2027 | Amsterdam, The Netherlands |  | 4:00 PM | Times are subject to canal transit; Visa required for some nationalities |  | [Day 1](day-01-amsterdam.md) |
| 2 | Jun 23, 2027 | At Sea |  |  |  |  | [Day 2](day-02-at-sea.md) |
| 3 | Jun 24, 2027 | Stornoway, Isle of Lewis, Scotland, United Kingdom | 8:00 AM | 5:00 PM | Visa required for some nationalities | 10 | [Day 3](day-03-stornoway.md) |
| 4 | Jun 25, 2027 | Belfast, Northern Ireland, United Kingdom | 10:00 AM | 9:00 PM | Visa required for some nationalities | 18 | [Day 4](day-04-belfast.md) |
| 5 | Jun 26, 2027 | Dun Laoghaire (Dublin), Ireland | 7:00 AM | 7:00 PM | Tender required; Wheelchair access limited | 18 | [Day 5](day-05-dublin-dun-laoghaire.md) |
| 6 | Jun 27, 2027 | Greenock (Glasgow), Scotland, United Kingdom | 10:00 AM | 9:00 PM | Visa required for some nationalities | 18 | [Day 6](day-06-glasgow-greenock.md) |
| 7 | Jun 28, 2027 | Greencastle (Londonderry), Ireland | 8:00 AM | 6:00 PM | Tender required; Wheelchair access limited | 14 | [Day 7](day-07-londonderry-greencastle.md) |
| 8 | Jun 29, 2027 | Killybegs, Donegal, Ireland | 8:00 AM | 5:00 PM | Tender required; Wheelchair access limited | 13 | [Day 8](day-08-killybegs.md) |
| 9 | Jun 30, 2027 | Galway, Ireland | 7:00 AM | 3:00 PM | Tender required; Wheelchair access limited; Times subject to weather conditions | 13 | [Day 9](day-09-galway-cliffs-of-moher.md) |
| 9 | Jun 30, 2027 | Scenic cruising Cliffs of Moher |  |  | Cruising only |  | [Day 9](day-09-galway-cliffs-of-moher.md) |
| 10 | Jul 01, 2027 | Cobh (Cork), Ireland | 7:00 AM | 3:00 PM | Times are subject to canal transit | 14 | [Day 10](day-10-cork-cobh.md) |
| 11 | Jul 02, 2027 | At Sea |  |  |  |  | [Day 11](day-11-at-sea.md) |
| 12 | Jul 03, 2027 | Amsterdam, The Netherlands | 7:00 AM |  | Times are subject to canal transit; Visa required for some nationalities | 13 | [Day 12](day-12-amsterdam.md) |

Times are local ship time as published by Holland America and subject to change.

## Port notes legend

| Code | Meaning |
|---|---|
| CO | Cruising only |
| NW | Wheelchair access limited |
| PC | Times are subject to canal transit |
| TR | Tender required |
| VS | Visa required for some nationalities |
| WC | Times subject to weather conditions |

## Data files

- Each `day-NN-*.md` file has YAML front matter (day, date, stops, port codes, arrive/depart, flags) followed by the port description and full shore excursion descriptions.
- [excursions.csv](excursions.csv) lists every shore excursion with price, duration, activity level, accessibility, and source URL for sorting and filtering.
- [places.geojson](places.geojson) holds the map data: the sea route, port calls, and places mentioned in the port and excursion descriptions, each tagged with its day and excursion IDs. Places whose coordinates could not be confirmed in OpenStreetMap have `"location_check": "approximate"`.
- The interactive map and day pages are on the family site, built from these files by [`site/`](../site/README.md). Once GitHub Pages is set up it is published at <https://bwbensonjr.github.io/travel/2027-ireland/>. To preview locally, run `uv run site/build.py` from the repository root and serve `_site/`.
