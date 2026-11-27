# Proposal

## Why

On port day pages, the places to see currently sit below the long list of shore excursions, so most readers never reach them. The collapsed excursion list also puts a price on every row, which makes the list read like a price list rather than a menu of things to do. The family wants to browse what each port offers first and look at cost only when an excursion interests them.

## What Changes

- On day pages that have both, the **Places** section moves above the **Shore excursions** section. It still comes after the day summary and port description.
- The collapsed row of each shore excursion shows only its title, duration and activity level. The price no longer appears there.
- The price stays in the expanded details ("Starting at"), which open with the excursion's "+" control. Nothing else in the expanded view changes.

Out of scope:
- The trip map's place pop-ups keep showing excursion prices, as `trip-map` requires. This request concerns the day pages only.
- The map's price filter is unchanged.
- The Places section keeps its current collapsed-by-default behavior.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `day-pages`: Adds a requirement fixing the section order on port day pages (summary, description, places, excursions). Modifies "Excursion list with expandable details" so the compact form omits price and only the expanded details show it.

## Impact

- `site/sitegen/trip.py`: the excursion summary line no longer includes the price.
- `site/templates/day.html`: the places block moves above the excursions block within each stop.
- `site/tests/test_day_pages.py`: new assertions for section order and for price placement.
- No data, URL, offline-cache or deployment changes. The next push to `main` redeploys the site, and phones pick up the change through the existing "Updated, reload" flow.
