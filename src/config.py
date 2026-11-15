
from pathlib import Path

# ==========================================
# 1. PROJECT DIRECTORY
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# 2. DATA DIRECTORIES
# ==========================================

DATA_DIR = BASE_DIR / "data"

RAW_DIR = DATA_DIR / "raw"

PROCESSED_DIR = DATA_DIR / "processed"


# ==========================================
# 3. OUTPUT DIRECTORIES
# ==========================================

OUTPUT_DIR = BASE_DIR / "outputs"

GRAPHS_DIR = OUTPUT_DIR / "graphs"

REPORTS_DIR = OUTPUT_DIR / "reports"


# ==========================================
# 4. CREATE FOLDERS AUTOMATICALLY
# ==========================================

for folder in [
    RAW_DIR,
    PROCESSED_DIR,
    GRAPHS_DIR,
    REPORTS_DIR
]:
    folder.mkdir(parents=True, exist_ok=True)


# ==========================================
# 5. PROJECT INFORMATION
# ==========================================

PROJECT_NAME = "Be an Earth System Trend Detective"

START_YEAR = 2000
END_YEAR = 2025

START_DATE = "20000101"
END_DATE = "20251231"


# ==========================================
# 6. STUDY LOCATIONS
# ==========================================

LOCATIONS = {

    "Rasuwa": {
        "latitude": 28.108,
        "longitude": 85.295
    },

    "Dhankuta": {
        "latitude": 26.983,
        "longitude": 87.333
    }

}


# ==========================================
# 7. NASA POWER API SETTINGS
# ==========================================

NASA_POWER_API = (
    "https://power.larc.nasa.gov/api/temporal/daily/point"
)

COMMUNITY = "AG"

TIME_STANDARD = "UTC"

DATA_FORMAT = "JSON"


# ==========================================
# 8. CLIMATE VARIABLES
# ==========================================

PARAMETERS = [

    "T2M",                  # Average temperature

    "T2M_MAX",              # Maximum temperature

    "T2M_MIN",              # Minimum temperature

    "PRECTOTCORR",          # Corrected precipitation

    "RH2M",                 # Relative humidity

    "QV2M",                 # Specific humidity

    "PW",                   # Precipitable water

    "ALLSKY_SFC_SW_DWN",    # Solar radiation

    "WS2M",                 # Wind speed

    "PS"                    # Surface pressure

]


# ==========================================
# 9. API REQUEST SETTINGS
# ==========================================

REQUEST_TIMEOUT = 180

TEST_START_DATE = "20250101"

TEST_END_DATE = "20251231"


print("Project configuration loaded successfully!")

