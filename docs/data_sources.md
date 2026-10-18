# Data Sources and Versions

This document describes the external datasets used in the ERCOT Energy Demand Forecasting & Capacity Planning project.

## 1. ERCOT Historical Hourly Load

- Source: Electric Reliability Council of Texas (ERCOT)
- Website: https://www.ercot.com/
- Period: 2019–2025
- Coverage: ERCOT system and eight weather zones
- Observations: 61,368 hourly records
- Acquisition: Manually downloaded historical load files

The load data were cleaned and aligned using a continuous UTC timeline, with explicit handling of Hour Ending conventions and Daylight Saving Time transitions.

## 2. ERA5 Historical Weather

- Source: Open-Meteo Historical Weather API
- Weather dataset: ERA5
- Period: 2019–2025
- Coverage: Eight ERCOT weather zones
- Observations: 490,944 region-hour records
- Acquisition: API-based historical weather retrieval

Weather variables include temperature, apparent temperature, relative humidity, dew point, precipitation, and wind speed.

Regional weather observations were aligned with hourly electricity load data using UTC timestamps.

## 3. ERCOT Capacity Planning Data

- Source: ERCOT Capacity, Demand and Reserves (CDR)
- Version: December 2024 Revised
- File: CapacityDemandandReservesReport_December2024.xlsx
- Planning period: 2025–2029

The dataset provides seasonal capacity planning information, resource composition, planned generation, and ELCC-related inputs.

The analysis uses this historical planning snapshot and should not be interpreted as a current ERCOT capacity assessment.

## 4. Data Quality

Data validation included:

- Missing and duplicate records
- Hour Ending and DST handling
- UTC timestamp continuity
- Regional and system load consistency
- Weather-to-load alignment

A total of 48 hours with regional aggregation inconsistencies in 2021 were retained and explicitly flagged.

## 5. Additional Source Details

Exact source-file references, weather API parameters, regional coordinates, and input checksums will be documented after verification against the original notebooks and downloaded data.
