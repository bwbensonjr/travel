# Spec Delta

## Purpose

Keeps the trip information readable on a phone during the cruise when ship internet is slow, costly or unavailable, and lets the site be installed like an app.

## ADDED Requirements

### Requirement: Full trip cached after one online visit
After a trip page has been opened once online, the browser SHALL have stored every page, style, script and data file that trip's day pages need. No further visits to individual pages SHALL be required.

#### Scenario: Read unvisited day offline
- **WHEN** a family member opens only the trip map while online, then turns on airplane mode and opens the day 10 page
- **THEN** the day 10 page loads in full, with its port description and every excursion's details

### Requirement: Offline readiness indicator
The trip pages SHALL show whether the trip is fully saved for offline use, so a family member can confirm it before boarding.

#### Scenario: Saved state shown
- **WHEN** caching of the trip has finished
- **THEN** the page shows a short "Available offline" status

#### Scenario: Not yet saved
- **WHEN** the browser does not support offline caching or caching has not finished
- **THEN** the page does not claim to be available offline

### Requirement: Updates reach cached copies
When the site is redeployed, a device that has the trip cached SHALL pick up the new content on its next online visit, without the user clearing data. It SHALL keep serving the old cached copy while offline.

#### Scenario: Updated excursion price
- **WHEN** an excursion price changes, the site is redeployed, and a family member who cached the old version opens the site online
- **THEN** after the update completes, the day page shows the new price

#### Scenario: Offline before update
- **WHEN** the same family member opens the site offline before visiting online again
- **THEN** the previously cached version is shown without errors

### Requirement: Installable on a home screen
The site SHALL provide what a phone needs to install it on the home screen: name, icons and start page. Once installed, it SHALL open to the trip in a standalone window.

#### Scenario: Add to home screen
- **WHEN** a family member adds the site to their phone's home screen and opens it from the icon
- **THEN** it opens to the 2027 Ireland trip map without browser address bar controls

### Requirement: Graceful offline behavior
While offline, cached pages SHALL work normally. Content that needs the network, namely map tiles and external links, SHALL fail visibly without breaking the page. A page that is not cached SHALL show an offline message with links to the cached trip pages.

#### Scenario: External link offline
- **WHEN** the user follows a Holland America link while offline
- **THEN** the browser's own offline error appears, and going back returns to the working cached day page

#### Scenario: Uncached page offline
- **WHEN** the user opens a site URL that was never cached while offline
- **THEN** an offline page appears with links to the cached trip map and day pages
