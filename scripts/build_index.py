import sys
from pathlib import Path

# Ensure `ps1/` is on PYTHONPATH so imports like `src.audioid.*` work.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.audioid.indexer import build_index, save_index


def main() -> None:
    # Optional development flag to avoid indexing the whole dataset while iterating.
    max_files = None
    for i, arg in enumerate(sys.argv):
        if arg in {"--limit", "-l"} and i + 1 < len(sys.argv):
            try:
                max_files = int(sys.argv[i + 1])
            except ValueError:
                raise SystemExit("Invalid --limit value (must be an integer).")

    payload = build_index(max_files=max_files)
    save_index(payload)
    print(f"Indexed {len(payload['songs'])} songs")
    skipped_meta = payload.get("skipped_metadata", [])
    skipped_decode = payload.get("skipped_decode", [])
    if skipped_meta:
        print(f"Skipped {len(skipped_meta)} invalid metadata rows (showing up to 5):")
        for item in skipped_meta[:5]:
            print(f"- {item.get('record')} :: {item.get('error')}")
    if skipped_decode:
        print(f"Skipped {len(skipped_decode)} unreadable files (showing up to 5):")
        for item in skipped_decode[:5]:
            print(f"- {item.get('song_id')} :: {item.get('path')} :: {item.get('error')}")


if __name__ == "__main__":
    main()

