# Spec Delta

## Purpose

The trip's home page: an interactive map of the cruise route, ports and excursion places, used to explore the trip and jump into each day's details.

## ADDED Requirements

### Requirement: Map is the trip home page
The trip path SHALL open to a page whose main element is an interactive map of the whole voyage. It SHALL show the sea route, a numbered marker for each port call, and a marker for each place, next to a list of the cruise days.

#### Scenario: Opening the trip
- **WHEN** a family member opens `/2027-ireland/`
- **THEN** the map shows the full route with port markers labeled by day number and all places, and the day list shows days 1 to 12 with date and port

### Requirement: Day selection
Selecting a day in the day list SHALL zoom the map to that day's port and places, and SHALL hide places from other days until the whole voyage is selected again.

#### Scenario: Select a port day
- **WHEN** the user selects day 4 in the day list
- **THEN** the map zooms to Belfast and shows only day 4's places, and the day list marks day 4 as selected

#### Scenario: Select a sea day
- **WHEN** the user selects day 2 (at sea)
- **THEN** the map zooms to the route leg sailed that day

#### Scenario: Return to whole voyage
- **WHEN** the user selects the whole-voyage entry
- **THEN** all places are shown and the map fits the full route

### Requirement: Links into day pages
Every port pop-up, place pop-up and day list entry SHALL provide a link to the matching day page on the site. Links SHALL go to site pages, never to repository Markdown files.

#### Scenario: Place pop-up link
- **WHEN** the user opens the pop-up for a place visited on day 9
- **THEN** the pop-up links to the day 9 page, and each listed excursion links to that excursion's details on the day 9 page

#### Scenario: Day list link
- **WHEN** the user follows the details link for day 7 in the day list
- **THEN** the day 7 page opens

### Requirement: Place pop-up content
A place's pop-up SHALL show its name, type, day and port, and a short note. It SHALL list each excursion that visits the place with price, duration and activity level, and SHALL say when a place's location is approximate.

#### Scenario: Place with excursions
- **WHEN** the user opens the pop-up for Giant's Causeway
- **THEN** it lists the day 4 excursions that visit it, each with its price, duration and activity level

#### Scenario: Approximate location
- **WHEN** the user opens the pop-up for a place marked approximate in the data
- **THEN** the pop-up states that the location is approximate

### Requirement: Map filters
The map SHALL let users filter places by name search, place type, maximum excursion price and activity level, and SHALL show how many places match. Filters that would match no data SHALL NOT be shown.

#### Scenario: Price filter
- **WHEN** the user sets the maximum price to $150
- **THEN** only places with at least one excursion priced $150 or less, or with no excursion, remain, and the count updates

#### Scenario: Search
- **WHEN** the user types "castle" in the search box
- **THEN** only places whose name, note or excursion titles contain "castle" are shown

#### Scenario: Empty filter hidden
- **WHEN** no excursion in the data is wheelchair accessible
- **THEN** no wheelchair-accessibility filter is shown

### Requirement: Usable on phones
The map page SHALL be usable on a phone screen 360 pixels wide or wider without horizontal scrolling. The day list and filters SHALL be collapsible so the map stays visible.

#### Scenario: Phone layout
- **WHEN** the page is opened on a 375-pixel-wide screen
- **THEN** the map and the day list are both reachable without horizontal scrolling, and the user can collapse the list to enlarge the map

### Requirement: Offline map notice
When the map cannot load because there is no connection, the page SHALL say that the map needs a connection, and SHALL keep the day list and day page links usable.

#### Scenario: Opened offline
- **WHEN** the trip page is opened from the offline cache with no network
- **THEN** a notice says the map needs a connection, and the day list still links to every day page
