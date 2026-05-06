# Audio Identification Architecture Schema

## Phase 1 - Offline indexing (runs once)

1) **Metadata ingestion**
- Load metadata from CSV/JSON if present (`song_id`, `title`, `artist`, `duration`, `genre`, `path`).
- Validate required fields and file existence.
- Skip and log invalid rows (never crash ingestion).
- Fallback mode auto-builds metadata from dataset folders.

2) **Fingerprint extraction**
- Decode audio -> mono PCM @ `11025 Hz`.
- STFT with Hann window, `4096` FFT, `50%` overlap.
- Convert to log-magnitude spectrogram.
- Apply 2D max filter (radius `~20` bins) to keep local constellation peaks.
- For each anchor peak, form fan-out pairs (up to `10`) inside target zone (`dt`, `df` constraints).
- Pack each `(f_anchor, f_target, dt)` into a 32-bit integer hash.

3) **Inverted index storage**
- `songs`: `song_id -> {title, artist, duration, genre, path}`
- `index`: `hash_value -> [(song_id, anchor_time_bin), ...]`
- Collisions are expected and resolved by histogram alignment at query time.
- Persist as pickle for instant service startup.


## Phase 2 - Online query (real-time)

1) **Input validation**
- Accept snippets in practical range (1-10 sec).
- Reject silent clips using RMS threshold.
- Reject unsupported/corrupt input with structured error code.

2) **Shared extraction interface**
- Apply the exact same preprocessing + fingerprinting path as indexing.
- Guarantees feature-space consistency between database and query.

3) **Fast retrieval + robust matching**
- Lookup all query hashes in inverted index (O(1) per hash).
- For each candidate song, compute `delta_t = song_offset - query_offset`.
- Build per-song offset histograms.
- True matches produce a sharp spike at one offset; random overlaps stay flat.

4) **Confidence heuristic**
- `confidence = spike_height / total_matched_hashes`
- `matched = (spike_height > 5) AND (confidence > 0.4)`
- Return closest candidate regardless, and strict match flag by threshold.


## Phase 3 - System concerns

- **Concurrency:** queries are read-only on in-memory index; run safely in async/threadpool mode.
- **Latency telemetry:** report extract/match/total timings per query.
- **Accuracy harness:** evaluate known `(snippet, expected_song_id)` pairs for threshold tuning.
- **Memory strategy:** compact integer hashes + append-only postings; optional numpy/Redis optimization path.
- **Health checks:** `/health` reports index readiness and service status.


## Modular code map

- `src/audioid/metadata.py` -> metadata loading + validation
- `src/audioid/preprocessing.py` -> decode/resample/mono normalization
- `src/audioid/fingerprint.py` -> STFT, peak-picking, hash packing
- `src/audioid/indexer.py` -> offline index build + persistence
- `src/audioid/query_validation.py` -> query duration/silence checks
- `src/audioid/matcher.py` -> offset-histogram scoring + confidence
- `src/audioid/service.py` -> orchestration + telemetry
- `src/app.py` -> API surface (`/identify`, `/spectrogram`, `/health`)

