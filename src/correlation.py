
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from .config import (
    PROCESSED_DIR,
    REPORTS_DIR,
    GRAPHS_DIR,
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


def analyze_correlations(location_name):

    print(f"\nAnalyzing correlations for {location_name}...")

    # Load annual climate data
    file_path = (
        PROCESSED_DIR /
        f"{location_name.lower()}_annual_analysis.csv"
    )

    df = pd.read_csv(file_path)

    # Keep available climate variables
    available_variables = [
        variable for variable in VARIABLES
        if variable in df.columns
    ]

    climate_data = df[available_variables]

    # Pearson correlation
    pearson_corr = climate_data.corr(
        method="pearson"
    )

    # Spearman correlation
    spearman_corr = climate_data.corr(
        method="spearman"
    )

    # Pairwise observation counts
    sample_counts = climate_data.notna().astype(int).T @ (
        climate_data.notna().astype(int)
    )

    # Save correlation reports
    pearson_file = (
        REPORTS_DIR /
        f"{location_name.lower()}_pearson_correlation.csv"
    )

    spearman_file = (
        REPORTS_DIR /
        f"{location_name.lower()}_spearman_correlation.csv"
    )

    sample_file = (
        REPORTS_DIR /
        f"{location_name.lower()}_correlation_sample_counts.csv"
    )

    pearson_corr.to_csv(pearson_file)
    spearman_corr.to_csv(spearman_file)
    sample_counts.to_csv(sample_file)

    # Create Pearson heatmap
    plt.figure(figsize=(12, 9))

    sns.heatmap(
        pearson_corr,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        center=0,
        square=True
    )

    plt.title(
        f"Pearson Correlation - {location_name}"
    )

    plt.tight_layout()

    pearson_graph = (
        GRAPHS_DIR /
        f"{location_name.lower()}_pearson_heatmap.png"
    )

    plt.savefig(
        pearson_graph,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    # Create Spearman heatmap
    plt.figure(figsize=(12, 9))

    sns.heatmap(
        spearman_corr,
        annot=True,
        cmap="coolwarm",
        fmt=".2f",
        center=0,
        square=True
    )

    plt.title(
        f"Spearman Correlation - {location_name}"
    )

    plt.tight_layout()

    spearman_graph = (
        GRAPHS_DIR /
        f"{location_name.lower()}_spearman_heatmap.png"
    )

    plt.savefig(
        spearman_graph,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

    print("\nPearson Correlation:")
    print(pearson_corr.round(2).to_string())

    print("\nSpearman Correlation:")
    print(spearman_corr.round(2).to_string())

    print("\nSaved reports:")
    print(pearson_file)
    print(spearman_file)
    print(sample_file)

    print("\nSaved graphs:")
    print(pearson_graph)
    print(spearman_graph)


def main():

    for location_name in LOCATIONS:

        try:
            analyze_correlations(location_name)

        except FileNotFoundError as error:
            print("\nDataset not found:", error)

        except Exception as error:
            print(
                f"\nCorrelation analysis error: {error}"
            )

    print("\nAll correlation analyses completed!")


if __name__ == "__main__":
    main()
