
import pandas as pd
import pymannkendall as mk

from .config import (
    PROCESSED_DIR,
    REPORTS_DIR,
    LOCATIONS
)


VARIABLES = [
    "PRECTOTCORR",
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


def detect_trends(location_name):

    print(f"\nDetecting trends for {location_name}...")

    # Load annual analysis
    file_path = (
        PROCESSED_DIR /
        f"{location_name.lower()}_annual_analysis.csv"
    )

    df = pd.read_csv(file_path)

    results = []

    for variable in VARIABLES:

        if variable not in df.columns:
            continue

        values = df[variable].dropna()

        if len(values) < 10:
            print(f"Insufficient data for {variable}")
            continue

        # Mann-Kendall test
        test = mk.original_test(values)

        results.append({

            "Location": location_name,
            "Variable": variable,
            "Start_Year": int(df.loc[values.index, "Year"].min()),
            "End_Year": int(df.loc[values.index, "Year"].max()),
            "Observations": len(values),

            "Trend": test.trend,
            "Significant": test.h,
            "P_Value": test.p,
            "Kendall_Tau": test.Tau,

            "Sen_Slope_Per_Year": test.slope,
            "Intercept": test.intercept

        })

    results_df = pd.DataFrame(results)

    # Save location-specific results
    output_file = (
        REPORTS_DIR /
        f"{location_name.lower()}_trend_results.csv"
    )

    results_df.to_csv(output_file, index=False)

    print("\nTrend results:")
    print(results_df.to_string(index=False))

    print("\nSaved:", output_file)

    return results_df


def main():

    all_results = []

    for location_name in LOCATIONS:

        try:

            result = detect_trends(location_name)

            all_results.append(result)

        except FileNotFoundError as error:

            print("Required file not found:", error)

        except Exception as error:

            print(
                f"Trend detection error for {location_name}: {error}"
            )

    # Combine both locations
    if all_results:

        combined = pd.concat(
            all_results,
            ignore_index=True
        )

        output_file = (
            REPORTS_DIR /
            "combined_trend_results.csv"
        )

        combined.to_csv(output_file, index=False)

        print("\n========== COMBINED TREND RESULTS ==========")

        print(combined.to_string(index=False))

        print("\nCombined results saved:", output_file)


if __name__ == "__main__":
    main()
