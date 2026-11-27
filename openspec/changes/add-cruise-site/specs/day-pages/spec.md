# Spec Delta

## Purpose

One page per cruise day with everything needed for that day: port facts, what the port offers, places to see, and the shore excursions with full details.

## ADDED Requirements

### Requirement: One page per cruise day
The site SHALL have one page for each day of the cruise, including sea days. A day with more than one stop SHALL show every stop on the same page, such as day 9's Galway call and Cliffs of Moher scenic cruising.

#### Scenario: All days present
- **WHEN** the site is built for the 2027 Ireland trip
- **THEN** pages exist for days 1 through 12

#### Scenario: Multi-stop day
- **WHEN** a family member opens the day 9 page
- **THEN** it shows a section for Galway and a section for the Cliffs of Moher scenic cruising

### Requirement: Day summary first
Each day page SHALL open with the day number, date, port name, arrival and departure times, and port notes such as "Tender required". These SHALL be shown before any descriptive text.

#### Scenario: Port day summary
- **WHEN** a family member opens the day 5 page
- **THEN** the top of the page shows Day 5, Jun 26, 2027, Dun Laoghaire (Dublin), arrive 7:00 AM, depart 7:00 PM, and the tender and wheelchair-access notes

#### Scenario: Sea day summary
- **WHEN** a family member opens the day 2 page
- **THEN** it shows the day number and date and identifies the day as a day at sea, with no arrival or departure times

### Requirement: Port description and places
Each port day page SHALL include the port description from the source data, and a list of the day's places grouped by type. Each place SHALL be linked to its position on the trip map.

#### Scenario: Places listed
- **WHEN** a family member opens the day 3 page
- **THEN** it lists the day 3 places, including the Callanish standing stones, grouped by type

#### Scenario: Place to map
- **WHEN** the user follows a place's map link on a day page
- **THEN** the trip map opens zoomed to that place with its pop-up open

### Requirement: Excursion list with expandable details
Each port day page SHALL list that day's shore excursions in a compact form showing title, price, duration and activity level. Each excursion SHALL expand in place to show its full description, all listed facts and its source link.

#### Scenario: Compact list
- **WHEN** a family member opens the day 4 page
- **THEN** all 18 day 4 excursions are listed with title, price, duration and activity level, and their full descriptions are collapsed

#### Scenario: Expand an excursion
- **WHEN** the user expands "The Giant's Causeway"
- **THEN** its full description, minimum age, meals, wheelchair access and Holland America link are shown without leaving the page

### Requirement: Linkable excursions
Each excursion SHALL have a stable link that opens its day page with that excursion expanded and scrolled into view. Excursions with the same title on the same day SHALL each get a distinct link.

#### Scenario: Direct excursion link
- **WHEN** someone opens a day page link that targets a specific excursion
- **THEN** the page scrolls to that excursion and shows it expanded

#### Scenario: Duplicate titles
- **WHEN** day 9 has two excursions titled "A Day in Scenic Connemara"
- **THEN** each has its own link, and following either opens the right one

### Requirement: Day-to-day navigation
Each day page SHALL link to the previous and next day and back to the trip map.

#### Scenario: Next day
- **WHEN** the user follows the next-day link on the day 6 page
- **THEN** the day 7 page opens

#### Scenario: First and last days
- **WHEN** the user views the day 1 page
- **THEN** there is no previous-day link, and the day 12 page has no next-day link
