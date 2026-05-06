# Audio Identification & Source Detection System

## Team Information
- **Team Name**: Julius Seizure
- **Year**: 2nd Year
- **All-Female Team**: No

## Architecture Overview

#### Describe your approach here. Keep it short and clear.

    - Phase 1 (offline indexing): ingest metadata from CSV/JSON with validation and skip-on-error handling, decode each track to mono PCM at 11025 Hz, compute Hann-window STFT (4096 FFT, 50% overlap), perform 2D peak picking, and generate packed 32-bit fingerprint hashes from (f_anchor, f_target, dt).
    - Phase 2 (online query): run the exact same extraction interface on 3-10 second snippets, retrieve candidate hits through an inverted index (hash -> [(song_id, time_offset)]), and compute per-song offset histograms where true matches form a sharp alignment spike.
    - Matching heuristic: choose the candidate with strongest histogram peak and score confidence as spike_height / total_matched_hashes; classify strict match with thresholds (aligned_hashes > 5 and confidence > 0.4), while still returning closest candidate metadata for low-confidence cases.
    - System design for scale and reliability: O(1) hash lookup with prebuilt serialized index for low latency, stateless read-heavy query path suitable for concurrent requests, per-stage latency telemetry (extract/match/total), strict query validation (silence/length/format), and graceful handling of corrupt dataset files.

**Note:** Please do not change the format or spelling of anything in this README. The fields are extracted using a script, so any changes to the structure or formatting may break the extraction process.
