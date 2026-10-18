"""Utilities for cleaning and validating ERCOT hourly-load data."""

from pathlib import Path

import pandas as pd


ZONE_COLUMNS = [
    "COAST",
    "EAST",
    "FWEST",
    "NORTH",
    "NCENT",
    "SOUTH",
    "SCENT",
    "WEST",
]

LOAD_COLUMNS = ZONE_COLUMNS + ["ERCOT"]

REQUIRED_COLUMNS = [
    "HourEnding",
    *LOAD_COLUMNS,
]


def expected_hours(year: int) -> int:
    """Return the expected number of hourly records in a calendar year."""
    return 8784 if pd.Timestamp(year, 12, 31).is_leap_year else 8760


def clean_ercot_hourly_load(
    file_path: Path,
    year: int,
) -> pd.DataFrame:
    """Clean an annual ERCOT hourly-load Excel file."""
    file_path = Path(file_path)

    df = pd.read_excel(file_path)
    # Normalize source column names across annual files.
    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    df = df.rename(
        columns={
            "Hour Ending": "HourEnding",
        }
    )
    missing_columns = (
        set(REQUIRED_COLUMNS)
        - set(df.columns)
    )

    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            f"{sorted(missing_columns)}"
        )

    expected_row_count = expected_hours(year)

    if len(df) != expected_row_count:
        raise ValueError(
            f"{year} row count is {len(df)}, "
            f"but {expected_row_count} was expected."
        )

    # Preserve the original source label.
    df["HourEnding_raw"] = (
        df["HourEnding"]
        .astype(str)
        .str.strip()
    )

    # Preserve the explicit DST indicator.
    df["is_dst_label"] = (
        df["HourEnding_raw"]
        .str.endswith(" DST")
    )

    normalized_text = (
        df["HourEnding_raw"]
        .str.replace(
            r"\s+DST$",
            "",
            regex=True,
        )
    )

    # Identify the Hour Ending 24 convention.
    is_hour_24 = (
        normalized_text
        .str.endswith("24:00")
    )

    normalized_text = (
        normalized_text
        .str.replace(
            r"\s24:00$",
            " 00:00",
            regex=True,
        )
    )

    parsed_local_time = pd.to_datetime(
        normalized_text,
        format="%m/%d/%Y %H:%M",
        errors="coerce",
    )

    # Parse isolated ISO-formatted timestamps.
    iso_timestamp_mask = parsed_local_time.isna()

    parsed_local_time.loc[iso_timestamp_mask] = (
        pd.to_datetime(
            normalized_text.loc[iso_timestamp_mask],
            format="%Y-%m-%d %H:%M:%S",
            errors="coerce",
        )
    )

    # Hour 24 is midnight of the following day.
    parsed_local_time.loc[is_hour_24] = (
        parsed_local_time.loc[is_hour_24]
        + pd.Timedelta(days=1)
    )

    df["HourEnding_local"] = parsed_local_time

    if df["HourEnding_local"].isna().any():
        failed_values = df.loc[
            df["HourEnding_local"].isna(),
            "HourEnding_raw",
        ].tolist()

        raise ValueError(
            "Unparsed timestamps remain: "
            f"{failed_values[:10]}"
        )

    # Create a stable annual sequence.
    df["interval_id"] = range(1, len(df) + 1)
    df["source_year"] = year

    # Construct a continuous UTC Hour Ending timeline.
    first_local_hour_ending = pd.Timestamp(
        year=year,
        month=1,
        day=1,
        hour=1,
    )

    first_utc_hour_ending = (
        first_local_hour_ending
        .tz_localize("America/Chicago")
        .tz_convert("UTC")
    )

    df["HourEnding_utc"] = pd.date_range(
        start=first_utc_hour_ending,
        periods=len(df),
        freq="h",
    )

    # Validate the weather-zone total.
    df["calculated_ercot_mw"] = (
        df[ZONE_COLUMNS]
        .sum(axis=1)
    )

    df["ercot_difference_mw"] = (
        df["ERCOT"]
        - df["calculated_ercot_mw"]
    )
    # Flag material disagreement between the reported ERCOT total
    # and the sum of the eight weather zones.
    maximum_allowed_difference_mw = 0.01

    df["zone_total_mismatch_flag"] = (
        df["ercot_difference_mw"].abs()
        > maximum_allowed_difference_mw
    )

    return df


def validate_ercot_hourly_load(
    df: pd.DataFrame,
    year: int,
) -> dict:
    """Summarize data-quality checks for a cleaned annual ERCOT dataset."""
    utc_differences = (
        df["HourEnding_utc"]
        .diff()
        .dropna()
    )

    return {
        "year": year,
        "row_count": len(df),
        "expected_hours": expected_hours(year),
        "row_count_matches": (
            len(df) == expected_hours(year)
        ),
        "missing_load_values": int(
            df[LOAD_COLUMNS]
            .isna()
            .sum()
            .sum()
        ),
        "unparsed_local_timestamps": int(
            df["HourEnding_local"]
            .isna()
            .sum()
        ),
        "unique_utc_timestamps": bool(
            df["HourEnding_utc"].is_unique
        ),
        "utc_is_sorted": bool(
            df["HourEnding_utc"]
            .is_monotonic_increasing
        ),
        "non_hourly_utc_intervals": int(
            (
                utc_differences
                != pd.Timedelta(hours=1)
            ).sum()
        ),
        "exact_duplicate_source_rows": int(
            df[REQUIRED_COLUMNS]
            .duplicated()
            .sum()
        ),
        "nonpositive_load_values": int(
            (
                df[LOAD_COLUMNS] <= 0
            )
            .sum()
            .sum()
        ),
        "maximum_zone_difference_mw": float(
            df["ercot_difference_mw"]
            .abs()
            .max()
        ),
    }