from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[2]

DATASET_DIR = APP_DIR / "data" / "raw" / "dataset"
METADATA_CSV_PATH = APP_DIR / "data" / "raw" / "songs.csv"
METADATA_JSON_PATH = APP_DIR / "data" / "raw" / "songs.json"
INDEX_PATH = APP_DIR / "data" / "processed" / "fingerprint_index.pkl"
SAMPLE_RATE = 11025
N_FFT = 4096
HOP_LENGTH = N_FFT // 2
WINDOW = "hann"
PEAK_NEIGHBORHOOD = 20
PEAK_MIN_DB = -35.0
FAN_OUT = 10
TARGET_TIME_BINS = 60
TARGET_FREQ_BINS = 128
MIN_QUERY_SECONDS = 1.0
MAX_QUERY_SECONDS = 10.0
SILENCE_RMS_THRESHOLD = 1e-3
MIN_ALIGNED_HASHES = 5
DEFAULT_CONFIDENCE_THRESHOLD = 0.40

