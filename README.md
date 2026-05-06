# Audio Identification & Source Detection System

## Team Information
- **Team Name**: Julius Seizure
- **Year**: 2nd Year
- **All-Female Team**: No

## Architecture Overview

#### Describe your approach here. Keep it short and clear.

    - We ingest song metadata (song_id, title, artist, duration, genre) from CSV/JSON with validation; bad rows are logged and skipped. Audio is standardized to mono 11025 Hz, transformed with Hann-window STFT (4096 FFT, 50% overlap), then converted into constellation peaks and packed 32-bit hashes (f_anchor, f_target, dt) for compact storage.
    - Matching uses inverted-index retrieval plus time-offset histogram voting: for each candidate, we compute dt = song_offset - query_offset for all hash hits and select the strongest histogram spike. Confidence is spike_height / total_matched_hashes with thresholds (aligned_hashes > 5 and confidence > 0.4) to reduce false positives.
    - Scalability is achieved through hash-table indexing (hash -> [(song_id, time_offset)]) with O(1) lookup per hash, persisted index snapshots for instant startup, and stateless read-only query execution that supports concurrent requests.
    - Robustness and latency are handled by strict query validation (format, duration, RMS silence), deterministic feature extraction shared by offline and online paths, per-stage latency timing (extract/match/total), and graceful handling of corrupt files instead of pipeline crashes.

**Note:** Please do not change the format or spelling of anything in this README. The fields are extracted using a script, so any changes to the structure or formatting may break the extraction process.
