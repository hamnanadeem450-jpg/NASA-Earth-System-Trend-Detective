
import json
import requests
import pandas as pd

from .config import (
    NASA_POWER_API,
    LOCATIONS,
    PARAMETERS,
    COMMUNITY,
    TIME_STANDARD,
    START_DATE,
    END_DATE,
    TEST_START_DATE,
    TEST_END_DATE,
    REQUEST_TIMEOUT,
    RAW_DIR
)

# True = one-year test
# False = complete 2000-2025 data
TEST_MODE = False


def download_location(location_name, coordinates):

    params = {
        "parameters": ",".join(PARAMETERS),
        "community": COMMUNITY,
        "longitude": coordinates["longitude"],
        "latitude": coordinates["latitude"],
        "start": TEST_START_DATE if TEST_MODE else START_DATE,
        "end": TEST_END_DATE if TEST_MODE else END_DATE,
        "format": "JSON",
        "time-standard": TIME_STANDARD
    }

    print(f"\nSending NASA API request for {location_name}...")

    response = requests.get(
        NASA_POWER_API,
        params=params,
        timeout=REQUEST_TIMEOUT
    )

    response.raise_for_status()

    data = response.json()

    # Check NASA response
    if "properties" not in data:
        raise ValueError(f"Unexpected NASA response: {data}")

    climate_data = data["properties"]["parameter"]

    # Convert NASA JSON into a Pandas DataFrame
    df = pd.DataFrame(climate_data)
    df.index.name = "DATE"
    df = df.reset_index()

    # Save original JSON response
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    json_file = RAW_DIR / f"{location_name.lower()}_nasa_raw.json"

    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    # Save tabular CSV
    csv_file = RAW_DIR / f"{location_name.lower()}_nasa_raw.csv"

    df.to_csv(csv_file, index=False)

    print(f"{location_name} data downloaded successfully!")
    print("Total records:", len(df))
    print("CSV file:", csv_file)
    print("\nFirst five records:")
    print(df.head())


def main():

    for location_name, coordinates in LOCATIONS.items():

        try:
            download_location(location_name, coordinates)

        except requests.exceptions.RequestException as error:
            print(f"API/network error for {location_name}: {error}")

        except (ValueError, KeyError) as error:
            print(f"Data error for {location_name}: {error}")


if __name__ == "__main__":
    main()
