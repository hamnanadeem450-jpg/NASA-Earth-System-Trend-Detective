
import pandas as pd
import matplotlib.pyplot as plt

from .config import (
    PROCESSED_DIR,
    GRAPHS_DIR,
    LOCATIONS
)


def load_annual_data(location_name):

    file_path = (
        PROCESSED_DIR /
        f"{location_name.lower()}_annual_analysis.csv"
    )

    return pd.read_csv(file_path)


def load_monthly_data(location_name):

    file_path = (
        PROCESSED_DIR /
        f"{location_name.lower()}_monthly_analysis.csv"
    )

    return pd.read_csv(file_path)


def save_graph(filename):

    output_file = GRAPHS_DIR / filename

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    print("Graph saved:", output_file)


def plot_annual_comparison(variable, title, ylabel, filename):

    plt.figure(figsize=(12, 6))

    for location_name in LOCATIONS:

        df = load_annual_data(location_name)

        plt.plot(
            df["Year"],
            df[variable],
            marker="o",
            label=location_name
        )

    plt.title(title)
    plt.xlabel("Year")
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_graph(filename)


def plot_temperature_extremes():

    plt.figure(figsize=(12, 6))

    for location_name in LOCATIONS:

        df = load_annual_data(location_name)

        plt.plot(
            df["Year"],
            df["T2M_MAX"],
            marker="o",
            label=f"{location_name} Maximum"
        )

        plt.plot(
            df["Year"],
            df["T2M_MIN"],
            marker="s",
            linestyle="--",
            label=f"{location_name} Minimum"
        )

    plt.title("Annual Maximum and Minimum Temperature")
    plt.xlabel("Year")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_graph("temperature_extremes_comparison.png")


def plot_monthly_climatology():

    plt.figure(figsize=(12, 6))

    for location_name in LOCATIONS:

        df = load_monthly_data(location_name)

        monthly_average = (
            df.groupby("Month")["T2M"]
            .mean()
        )

        plt.plot(
            monthly_average.index,
            monthly_average.values,
            marker="o",
            label=location_name
        )

    month_names = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    plt.xticks(range(1, 13), month_names)
    plt.title("Average Monthly Temperature (2000–2025)")
    plt.xlabel("Month")
    plt.ylabel("Temperature (°C)")
    plt.legend()
    plt.grid(True, alpha=0.3)

    save_graph("monthly_temperature_comparison.png")


def main():

    print("\nGenerating climate visualizations...")

    # Graph 1: Average annual temperature
    plot_annual_comparison(
        variable="T2M",
        title="Annual Average Temperature: Rasuwa vs Dhankuta",
        ylabel="Temperature (°C)",
        filename="annual_temperature_comparison.png"
    )

    # Graph 2: Annual precipitation
    plot_annual_comparison(
        variable="PRECTOTCORR",
        title="Annual Precipitation: Rasuwa vs Dhankuta",
        ylabel="Annual PRECTOTCORR Total (check API units)",
        filename="annual_rainfall_comparison.png"
    )

    # Graph 3: Maximum and minimum temperatures
    plot_temperature_extremes()

    # Graph 4: Relative humidity
    plot_annual_comparison(
        variable="RH2M",
        title="Annual Relative Humidity: Rasuwa vs Dhankuta",
        ylabel="Relative Humidity (%)",
        filename="annual_humidity_comparison.png"
    )

    # Graph 5: Solar radiation
    plot_annual_comparison(
        variable="ALLSKY_SFC_SW_DWN",
        title="Annual Average Solar Radiation: Rasuwa vs Dhankuta",
        ylabel="NASA POWER Solar Radiation Value",
        filename="annual_solar_radiation_comparison.png"
    )

    # Graph 6: Monthly temperature pattern
    plot_monthly_climatology()

    print("\nAll climate graphs generated successfully!")


if __name__ == "__main__":
    main()
