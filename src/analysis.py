
import pandas as pd

from .config import (
    PROCESSED_DIR,
    REPORTS_DIR,
    LOCATIONS,
    START_YEAR,
    END_YEAR
)


# Variables whose daily values will be added
# to calculate monthly, seasonal and annual totals.
SUM_VARIABLES = [
    "PRECTOTCORR"
]


# All other climate variables will use their mean.
MEAN_VARIABLES = [
    "T2M",
    "T2M_MAX",
    "T2M_MIN",
    "RH2M",
    "QV2M",
    "PW",
    "ALLSKY_SFC_SW_DWN",
    "WS2M",
    "PS"
]


# Seasons used for Nepal climate analysis
SEASONS = {
    "Winter": [12, 1, 2],
    "Pre-Monsoon": [3, 4, 5],
    "Monsoon": [6, 7, 8, 9],
    "Post-Monsoon": [10, 11]
}


def load_climate_data(location_name):

    file_path = (
        PROCESSED_DIR /
        f"{location_name.lower()}_climate_2000_2025.csv"
    )

    df = pd.read_csv(file_path, parse_dates=["DATE"])

    return df


def load_pw_data(location_name):

    file_path = (
        PROCESSED_DIR /
        f"{location_name.lower()}_pw_2001_2025.csv"
    )

    df = pd.read_csv(file_path, parse_dates=["DATE"])

    return df


def get_aggregation_rules(df):

    rules = {}

    for variable in SUM_VARIABLES:

        if variable in df.columns:
            rules[variable] = "sum"

    for variable in MEAN_VARIABLES:

        if variable in df.columns:
            rules[variable] = "mean"

    return rules


def analyze_location(location_name):

    print(f"\nAnalyzing climate data for {location_name}...")

    # STEP 1: Load complete climate dataset
    df = load_climate_data(location_name)

    # Add date-related columns
    df["Year"] = df["DATE"].dt.year
    df["Month"] = df["DATE"].dt.month

    aggregation_rules = get_aggregation_rules(df)

    # STEP 2: Annual climate analysis
    annual_data = (
        df.groupby("Year")
        .agg(aggregation_rules)
        .reset_index()
    )

    annual_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_annual_analysis.csv"
    )

    annual_data.to_csv(annual_file, index=False)

    # STEP 3: Monthly climate analysis
    monthly_data = (
        df.groupby(["Year", "Month"])
        .agg(aggregation_rules)
        .reset_index()
    )

    monthly_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_monthly_analysis.csv"
    )

    monthly_data.to_csv(monthly_file, index=False)

    # STEP 4: Seasonal climate analysis
    df["Season"] = df["Month"].map(
        lambda month: next(
            season
            for season, months in SEASONS.items()
            if month in months
        )
    )

    seasonal_data = (
        df.groupby(["Year", "Season"])
        .agg(aggregation_rules)
        .reset_index()
    )

    seasonal_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_seasonal_analysis.csv"
    )

    seasonal_data.to_csv(seasonal_file, index=False)

    # STEP 5: Separate PW analysis (2001-2025)
    pw_df = load_pw_data(location_name)

    pw_df["Year"] = pw_df["DATE"].dt.year
    pw_df["Month"] = pw_df["DATE"].dt.month

    pw_annual = (
        pw_df.groupby("Year")["PW"]
        .mean()
        .reset_index(name="PW_Mean")
    )

    pw_annual_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_pw_annual_analysis.csv"
    )

    pw_annual.to_csv(pw_annual_file, index=False)

    pw_monthly = (
        pw_df.groupby(["Year", "Month"])["PW"]
        .mean()
        .reset_index(name="PW_Mean")
    )

    pw_monthly_file = (
        PROCESSED_DIR /
        f"{location_name.lower()}_pw_monthly_analysis.csv"
    )

    pw_monthly.to_csv(pw_monthly_file, index=False)

    # STEP 6: Display analysis summary
    print("\n========== ANALYSIS SUMMARY ==========")

    print("Location:", location_name)

    print("\nAnnual records:", len(annual_data))
    print("Monthly records:", len(monthly_data))
    print("Seasonal records:", len(seasonal_data))

    print("PW annual records:", len(pw_annual))
    print("PW monthly records:", len(pw_monthly))

    print("\nAnnual climate analysis:")
    print(annual_data.head().to_string(index=False))

    print("\nSeasonal climate analysis:")
    print(seasonal_data.head(8).to_string(index=False))

    print("\nPW annual analysis:")
    print(pw_annual.head().to_string(index=False))

    print("\nSaved files:")
    print(annual_file)
    print(monthly_file)
    print(seasonal_file)
    print(pw_annual_file)
    print(pw_monthly_file)

    print("\n=====================================")

    return annual_data, monthly_data, seasonal_data


def main():

    all_annual_data = []

    for location_name in LOCATIONS:

        try:

            annual, monthly, seasonal = analyze_location(
                location_name
            )

            annual["Location"] = location_name

            all_annual_data.append(annual)

        except FileNotFoundError as error:

            print("\nDataset not found:", error)

        except Exception as error:

            print(
                f"\nAnalysis error for {location_name}: {error}"
            )

    # STEP 7: Create Rasuwa vs Dhankuta annual comparison
    if len(all_annual_data) == len(LOCATIONS):

        combined_annual = pd.concat(
            all_annual_data,
            ignore_index=True
        )

        comparison_file = (
            REPORTS_DIR /
            "rasuwa_dhankuta_annual_comparison.csv"
        )

        combined_annual.to_csv(
            comparison_file,
            index=False
        )

        print("\n========== FINAL COMPARISON ==========")

        print(
            combined_annual.head(10).to_string(index=False)
        )

        print("\nComparison report saved:")
        print(comparison_file)


if __name__ == "__main__":
    main()
