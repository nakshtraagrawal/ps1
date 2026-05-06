from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import soundfile as sf

from .config import DATASET_DIR, METADATA_CSV_PATH, METADATA_JSON_PATH


@dataclass
class SongRecord:
    song_id: str
    title: str
    artist: str
    duration: float
    genre: str
    path: str


def _safe_duration(path: Path) -> float:
    try:
        info = sf.info(str(path))
        if info.samplerate <= 0:
            return 0.0
        return float(info.frames / info.samplerate)
    except Exception:
        return 0.0


def _validate_row(row: dict[str, object]) -> tuple[bool, str]:
    required = ("song_id", "title", "artist", "genre", "path")
    for key in required:
        if key not in row or row[key] in (None, ""):
            return False, f"missing field '{key}'"
    return True, ""


def _load_csv(csv_path: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with csv_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows


def _load_json(json_path: Path) -> list[dict[str, object]]:
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON metadata must be a list of song records")
    return [dict(item) for item in data if isinstance(item, dict)]


def _fallback_records(dataset_dir: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for genre_dir in sorted(dataset_dir.iterdir()):
        if not genre_dir.is_dir():
            continue
        for wav_file in sorted(genre_dir.glob("*.wav")):
            rows.append(
                {
                    "song_id": f"{genre_dir.name}:{wav_file.stem}",
                    "title": wav_file.stem,
                    "artist": genre_dir.name.title(),
                    "genre": genre_dir.name,
                    "duration": _safe_duration(wav_file),
                    "path": str(wav_file),
                }
            )
    return rows


def load_song_records(
    dataset_dir: Path = DATASET_DIR,
    metadata_csv_path: Path = METADATA_CSV_PATH,
    metadata_json_path: Path = METADATA_JSON_PATH,
) -> tuple[list[SongRecord], list[dict[str, str]]]:
    rows: list[dict[str, object]]
    if metadata_csv_path.exists():
        rows = _load_csv(metadata_csv_path)
    elif metadata_json_path.exists():
        rows = _load_json(metadata_json_path)
    else:
        rows = _fallback_records(dataset_dir)

    records: list[SongRecord] = []
    skipped: list[dict[str, str]] = []
    for raw in rows:
        ok, reason = _validate_row(raw)
        if not ok:
            skipped.append({"record": str(raw), "error": reason})
            continue
        path = Path(str(raw["path"]))
        if not path.exists():
            skipped.append({"record": str(raw), "error": "audio path does not exist"})
            continue
        duration = float(raw.get("duration", 0.0) or _safe_duration(path))
        records.append(
            SongRecord(
                song_id=str(raw["song_id"]),
                title=str(raw["title"]),
                artist=str(raw["artist"]),
                duration=duration,
                genre=str(raw["genre"]),
                path=str(path),
            )
        )
    return records, skipped

