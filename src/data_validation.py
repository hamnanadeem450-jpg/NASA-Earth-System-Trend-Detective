
import pandas as pd
import numpy as np

from .config import (
    PROCESSED_DIR,
    REPORTS_DIR,
    LOCATIONS,
    START_YEAR,
    END_YEAR
)


# Expected climate variables
EXPECTED_COLUMNS = [
    "DATE",
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "PRECTOTCORR",
    "RH2M",
    "QV2M",
    "PW",
    "ALLSKY_SFC_SW_DWN",
    "WS2M",
    "PS"
]


# Broad physical plausibility limits.
# These are screening limits, not scientific quality-control standards.
VARIABLE_LIMITS = {
    "T2M": (-90, 60),
    "T2M_MAX": (-90, 65),
    "T2M_MIN": (-100, 60),
    "PRECTOTCORR": (0, 1000),
    "RH2M": (0, 100),
    "QV2M": (0, 100),
    "PW": (0, 150),
    "ALLSKY_SFC_SW_DWN": (0, 50),
    "WS2M": (0, 100),
    "PS": (0, 1100)
}


def validate_location(location_name):

    print(f"\nValidating {location_name} data...")

    # STEP 1: Load cleaned dataset
    file_path = (
        PROCESSED_DIR /
        f"{location_name.lower()}_climate_2000_2025.csv"
    )

    df = pd.read_csv(file_path, parse_dates=["DATE"])

    issues = []

    # STEP 2: Check required columns
    missing_columns = [
        col for col in EXPECTED_COLUMNS
        if col not in df.columns
    ]

    extra_columns = [
        col for col in df.columns
        if col not in EXPECTED_COLUMNS
    ]

    if missing_columns:
        issues.append(
            f"Missing columns: {missing_columns}"
        )

    if extra_columns:
        issues.append(
            f"Unexpected columns: {extra_columns}"
        )

    # STEP 3: Check date range and daily continuity
    expected_dates = pd.date_range(
        start=f"{START_YEAR}-01-01",
        end=f"{END_YEAR}-12-31",
        freq="D"
    )

    actual_dates = pd.DatetimeIndex(df["DATE"].dropna())

    missing_dates = expected_dates.difference(actual_dates)
    extra_dates = actual_dates.difference(expected_dates)

    duplicate_dates = df["DATE"].duplicated().sum()

    if len(missing_dates) > 0:
        issues.append(
            f"{len(missing_dates)} expected dates are missing"
        )

    if len(extra_dates) > 0:
        issues.append(
            f"{len(extra_dates)} dates are outside expected range"
        )

    if duplicate_dates > 0:
        issues.append(
            f"{duplicate_dates} duplicate dates found"
        )

    # STEP 4: Check missing values
    missing_values = df.isnull().sum()

    # STEP 5: Check numeric variables and physical limits
    range_results = []

    for variable, (minimum, maximum) in VARIABLE_LIMITS.items():

        if variable not in df.columns:
            continue

        values = pd.to_numeric(
            df[variable],
            errors="coerce"
        )

        invalid_numeric = (
            values.isna() & df[variable].notna()
        ).sum()

        below_limit = (values < minimum).sum()
        above_limit = (values > maximum).sum()

        range_results.append({
            "Variable": variable,
            "Minimum_Value": values.min(),
            "Maximum_Value": values.max(),
            "Below_Limit": int(below_limit),
            "Above_Limit": int(above_limit),
            "Invalid_Numeric": int(invalid_numeric),
            "Screening_Limits": f"{minimum} to {maximum}"
        })

    range_report = pd.DataFrame(range_results)

    # STEP 6: Check temperature consistency
    temperature_issues = 0

    if all(
        col in df.columns
        for col in ["T2M_MIN", "T2M", "T2M_MAX"]
    ):

        temperature_issues = (
            (df["T2M_MIN"] > df["T2M"]) |
            (df["T2M"] > df["T2M_MAX"]) |
            (df["T2M_MIN"] > df["T2M_MAX"])
        ).sum()

        if temperature_issues > 0:
            issues.append(
                f"{temperature_issues} temperature consistency issues"
            )

    # STEP 7: Generate statistical summary
    numeric_columns = [
        col for col in EXPECTED_COLUMNS
        if col in df.columns and col != "DATE"
    ]

    statistics = df[numeric_columns].describe().T

    statistics.index.name = "Variable"

    # STEP 8: Check PW-specific dataset
    pw_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_pw_2001_2025.csv"
    )

    pw_df = pd.read_csv(pw_file, parse_dates=["DATE"])

    expected_pw_dates = pd.date_range(
        start="2001-01-01",
        end=f"{END_YEAR}-12-31",
        freq="D"
    )

    actual_pw_dates = pd.DatetimeIndex(
        pw_df["DATE"].dropna()
    )

    missing_pw_dates = expected_pw_dates.difference(
        actual_pw_dates
    )

    pw_missing_values = pw_df["PW"].isna().sum()

    pw_duplicate_dates = pw_df["DATE"].duplicated().sum()

    # STEP 9: Save validation reports
    range_file = (
        REPORTS_DIR /
        f"{location_name.lower()}_range_validation.csv"
    )

    statistics_file = (
        REPORTS_DIR /
        f"{location_name.lower()}_statistical_summary.csv"
    )

    range_report.to_csv(range_file, index=False)
    statistics.to_csv(statistics_file)

    # STEP 10: Display results
    print("\n========== VALIDATION RESULTS ==========")

    print("Location:", location_name)
    print("Total records:", len(df))
    print("Expected records:", len(expected_dates))
    print("Missing dates:", len(missing_dates))
    print("Extra dates:", len(extra_dates))
    print("Duplicate dates:", duplicate_dates)

    print("\nMissing values by variable:")
    print(missing_values.to_string())

    print("\nPhysical range screening:")
    print(range_report.to_string(index=False))

    print("\nTemperature consistency issues:")
    print(temperature_issues)

    print("\nPW dataset validation:")
    print("PW records:", len(pw_df))
    print("Expected PW records:", len(expected_pw_dates))
    print("Missing PW dates:", len(missing_pw_dates))
    print("Missing PW values:", pw_missing_values)
    print("Duplicate PW dates:", pw_duplicate_dates)

    if len(missing_pw_dates) > 0:
        issues.append(
            f"{len(missing_pw_dates)} PW dates missing from 2001-2025 dataset"
        )

    if pw_missing_values > 0:
        issues.append(
            f"{pw_missing_values} missing values in PW dataset"
        )

    if pw_duplicate_dates > 0:
        issues.append(
            f"{pw_duplicate_dates} duplicate dates in PW dataset"
        )

    print("\nValidation issues:")

    if issues:
        for issue in issues:
            print("WARNING:", issue)
    else:
        print("No date, column or temperature consistency issues found.")

    print("\nSaved reports:")
    print(range_file)
    print(statistics_file)

    print("\n========================================")

    return {
        "Location": location_name,
        "Records": len(df),
        "Missing_Dates": len(missing_dates),
        "Duplicate_Dates": duplicate_dates,
        "Missing_PW_Dates": len(missing_pw_dates),
        "Temperature_Issues": int(temperature_issues),
        "Validation_Issues": len(issues)
    }


def main():

    validation_results = []

    for location_name in LOCATIONS:

        try:
            result = validate_location(location_name)
            validation_results.append(result)

        except FileNotFoundError as error:
            print("\nRequired dataset not found:", error)

        except Exception as error:
            print(
                f"\nValidation error for {location_name}: {error}"
            )

    # STEP 11: Save combined validation summary
    if validation_results:

        summary = pd.DataFrame(validation_results)

        summary_file = (
            REPORTS_DIR /
            "combined_validation_summary.csv"
        )

        summary.to_csv(summary_file, index=False)

        print("\n========== FINAL VALIDATION SUMMARY ==========")
        print(summary.to_string(index=False))
        print("\nCombined report saved:", summary_file)


if __name__ == "__main__":
    main()
