# Data Documentation

## Overview

This project integrates historical electricity demand, weather observations, and capacity planning data for ERCOT analysis.

## Data Sources

| Dataset | Source | Period |
|---|---|---|
| Historical hourly electricity load | ERCOT | 2019–2025 |
| Historical hourly weather | Open-Meteo Historical Weather API (ERA5) | 2019–2025 |
| Capacity, Demand and Reserves (CDR) | ERCOT December 2024 Revised CDR | Planning years 2025–2029 |

## Data Organization

The local analysis uses the following directories:

- `raw/`: Original source files
- `interim/`: Intermediate processing outputs
- `processed/`: Cleaned and validated datasets
- `weather/`: Weather observations and regional mappings
- `modeling/`: Model-ready datasets

## Data Quality

The analysis includes 61,368 hourly load records and 490,944 regional load-weather observations.

Timestamp handling includes ERCOT Hour Ending conventions, Daylight Saving Time transitions, and UTC alignment.

A total of 48 hours with regional aggregation inconsistencies in 2021 were retained and flagged for quality control.

## Data Availability

The complete raw and intermediate datasets are not included in this repository.

Data acquisition instructions, source versions, and processing requirements will be documented separately.
