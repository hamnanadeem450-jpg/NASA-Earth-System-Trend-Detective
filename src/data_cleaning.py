


import pandas as pd
import numpy as np

from .config import (
    RAW_DIR,
    PROCESSED_DIR,
    LOCATIONS,
    START_YEAR,
    END_YEAR
)


def clean_location_data(location_name):

    print(f"\nCleaning data for {location_name}...")

    # STEP 1: Read original NASA CSV
    input_file = RAW_DIR / f"{location_name.lower()}_nasa_raw.csv"

    df = pd.read_csv(input_file)

    original_records = len(df)

    # STEP 2: Replace NASA missing-data fill values
    df = df.replace([-999, -999.0], np.nan)

    # STEP 3: Convert DATE into datetime format
    df["DATE"] = pd.to_datetime(
        df["DATE"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # STEP 4: Remove rows with invalid dates
    invalid_dates = df["DATE"].isna().sum()
    df = df.dropna(subset=["DATE"])

    # STEP 5: Sort records by date
    df = df.sort_values("DATE").copy()

    # STEP 6: Remove duplicate dates
    before_duplicates = len(df)

    df = df.drop_duplicates(
        subset=["DATE"],
        keep="first"
    )

    duplicate_count = before_duplicates - len(df)

    # STEP 7: Check expected date range
    expected_start = pd.Timestamp(f"{START_YEAR}-01-01")
    expected_end = pd.Timestamp(f"{END_YEAR}-12-31")

    df = df.loc[
        (df["DATE"] >= expected_start) &
        (df["DATE"] <= expected_end)
    ].copy()

    # STEP 8: Generate missing values report
    missing_report = pd.DataFrame({
        "Variable": df.columns,
        "Missing_Count": df.isnull().sum().values,
        "Missing_Percentage": (
            df.isnull().mean().values * 100
        ).round(2)
    })

    # STEP 9: Save complete cleaned dataset
    cleaned_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_climate_cleaned.csv"
    )

    df.to_csv(cleaned_file, index=False)

    # STEP 10: Save missing values report
    report_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_missing_report.csv"
    )

    missing_report.to_csv(report_file, index=False)

    # STEP 11: Create full climate analysis dataset
    # All variables: 2000-2025
    full_dataset = df.copy()

    full_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_climate_2000_2025.csv"
    )

    full_dataset.to_csv(full_file, index=False)

    # STEP 12: Create separate PW analysis dataset
    # PW data: 2001-2025, without missing values
    pw_dataset = df.loc[
        (df["DATE"].dt.year >= 2001) &
        (df["DATE"].dt.year <= 2025) &
        (df["PW"].notna())
    ].copy()

    pw_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_pw_2001_2025.csv"
    )

    pw_dataset.to_csv(pw_file, index=False)

    # STEP 13: Check PW missing values year-wise
    print("\nPW MISSING VALUES BY YEAR")

    if "PW" in df.columns:

        pw_missing = df.loc[df["PW"].isna(), "DATE"]

        if pw_missing.empty:
            print("No missing PW values found.")

        else:
            print(
                pw_missing.dt.year
                .value_counts()
                .sort_index()
                .to_string()
            )

            print(
                "\nFirst missing PW date:",
                pw_missing.min()
            )

            print(
                "Last missing PW date:",
                pw_missing.max()
            )

    # STEP 14: Validate date continuity
    expected_dates = pd.date_range(
        start=expected_start,
        end=expected_end,
        freq="D"
    )

    actual_dates = pd.DatetimeIndex(df["DATE"])

    missing_dates = expected_dates.difference(actual_dates)

    extra_dates = actual_dates.difference(expected_dates)

    # STEP 15: Display cleaning summary
    print("\n========== CLEANING SUMMARY ==========")

    print(f"Location: {location_name}")
    print(f"Original records: {original_records}")
    print(f"Cleaned records: {len(df)}")
    print(f"Invalid dates removed: {invalid_dates}")
    print(f"Duplicate dates removed: {duplicate_count}")

    print(f"Expected daily records: {len(expected_dates)}")
    print(f"Missing dates: {len(missing_dates)}")
    print(f"Extra dates: {len(extra_dates)}")

    print("\nMissing values report:")
    print(missing_report.to_string(index=False))

    print("\n========== ANALYSIS DATASETS ==========")

    print(
        f"Full climate dataset ({START_YEAR}-{END_YEAR}): "
        f"{len(full_dataset)} records"
    )

    print(
        f"PW analysis dataset (2001-2025): "
        f"{len(pw_dataset)} records"
    )

    print("\nSaved files:")
    print("Cleaned dataset:", cleaned_file)
    print("Missing report:", report_file)
    print("Full climate dataset:", full_file)
    print("PW analysis dataset:", pw_file)

    print("\n=======================================")


def main():

    for location_name in LOCATIONS:

        try:
            clean_location_data(location_name)

        except FileNotFoundError:
            print(
                f"Raw CSV file not found for {location_name}"
            )

        except Exception as error:
            print(
                f"Error cleaning {location_name}: {error}"
            )


if __name__ == "__main__":
    main()
