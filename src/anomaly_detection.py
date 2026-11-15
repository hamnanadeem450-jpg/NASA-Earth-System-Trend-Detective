
import pandas as pd
import numpy as np

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


def detect_anomalies(location_name):

    print(f"\nDetecting anomalies for {location_name}...")

    # Load annual climate data
    file_path = (
        PROCESSED_DIR /
        f"{location_name.lower()}_annual_analysis.csv"
    )

    df = pd.read_csv(file_path)

    anomaly_results = []

    for variable in VARIABLES:

        if variable not in df.columns:
            continue

        data = df[["Year", variable]].dropna().copy()

        if len(data) < 5:
            continue

        values = data[variable]

        # Z-score method
        mean_value = values.mean()
        std_value = values.std()

        if std_value == 0 or pd.isna(std_value):
            data["Z_Score"] = 0.0
        else:
            data["Z_Score"] = (
                (values - mean_value) / std_value
            )

        data["Z_Anomaly"] = (
            data["Z_Score"].abs() > 2
        )

        # IQR method
        q1 = values.quantile(0.25)
        q3 = values.quantile(0.75)

        iqr = q3 - q1

        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        data["IQR_Anomaly"] = (
            (values < lower_bound) |
            (values > upper_bound)
        )

        # Record results
        for _, row in data.iterrows():

            if row["Z_Anomaly"] or row["IQR_Anomaly"]:

                anomaly_results.append({
                    "Location": location_name,
                    "Variable": variable,
                    "Year": int(row["Year"]),
                    "Observed_Value": row[variable],
                    "Z_Score": row["Z_Score"],
                    "Z_Anomaly": bool(row["Z_Anomaly"]),
                    "IQR_Anomaly": bool(row["IQR_Anomaly"]),
                    "Lower_IQR_Bound": lower_bound,
                    "Upper_IQR_Bound": upper_bound
                })

    # Create report
    results_df = pd.DataFrame(anomaly_results)

    output_file = (
        REPORTS_DIR /
        f"{location_name.lower()}_anomaly_results.csv"
    )

    results_df.to_csv(output_file, index=False)

    print("\nAnomaly detection summary:")
    print("Total anomalies:", len(results_df))

    if not results_df.empty:
        print(results_df.to_string(index=False))
    else:
        print("No anomalies detected.")

    print("\nSaved report:", output_file)

    return results_df


def main():

    all_results = []

    for location_name in LOCATIONS:

        try:
            results = detect_anomalies(location_name)
            all_results.append(results)

        except FileNotFoundError as error:
            print("\nDataset not found:", error)

        except Exception as error:
            print(
                f"\nAnomaly detection error: {error}"
            )

    # Combine both locations
    if all_results:

        combined = pd.concat(
            all_results,
            ignore_index=True
        )

        combined_file = (
            REPORTS_DIR /
            "combined_anomaly_results.csv"
        )

        combined.to_csv(
            combined_file,
            index=False
        )

        print("\nCombined anomaly report saved:")
        print(combined_file)

        print("\nTotal combined anomalies:", len(combined))

    print("\nAnomaly detection completed!")


if __name__ == "__main__":
    main()
