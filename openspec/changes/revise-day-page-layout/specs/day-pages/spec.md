# Spec Delta

## ADDED Requirements

### Requirement: Places before excursions
Within each stop on a day page, the places section SHALL appear above the shore excursions section. Both SHALL follow the day summary and the stop's port description. On a day with several stops, each stop's places SHALL appear above that stop's own excursions.

#### Scenario: Port day with places and excursions
- **WHEN** a family member opens the day 4 page
- **THEN** the Places section appears after the Belfast description and before the Shore excursions section

#### Scenario: Multi-stop day
- **WHEN** a family member opens the day 9 page
- **THEN** Galway's places appear above Galway's excursions, and the Cliffs of Moher section shows its places with no excursions section

#### Scenario: Stop without places
- **WHEN** a stop has shore excursions but no places
- **THEN** the Shore excursions section follows the port description directly

## MODIFIED Requirements

### Requirement: Excursion list with expandable details
Each port day page SHALL list that day's shore excursions in a compact form showing title, duration and activity level, without the price. Each excursion SHALL expand in place to show its full description, all listed facts including its starting price, and its source link.

#### Scenario: Compact list
- **WHEN** a family member opens the day 4 page
- **THEN** all 18 day 4 excursions are listed with title, duration and activity level, no price is visible in any collapsed row, and their full descriptions are collapsed

#### Scenario: Expand an excursion
- **WHEN** the user expands "The Giant's Causeway"
- **THEN** its starting price, full description, minimum age, meals, wheelchair access and Holland America link are shown without leaving the page
