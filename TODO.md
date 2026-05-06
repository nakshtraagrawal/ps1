To build a functional hackathon application for the **Audio Identification System**, you need to bridge the gap between your Python signal processing logic and a user-facing interface. This checklist ensures your backend is optimized for speed while your UI remains responsive.



---

### Phase 1: The Core Identification Model (Backend)
*Focus: Accuracy and Low Latency*

*   [x] **Signal Standardizer:** Implement a pre-processing function to force all inputs (dataset and user clips) to **22050 Hz Mono**.
*   [ ] **Feature Extractor (The "Black Box"):** 
    *   [x] Generate a Log-Spectrogram to visualize audio energy.
    *   [x] Implement 2D Peak Finding (Constellation Map) to identify the strongest frequencies.
    *   [x] Create combinatorial hashes from peak pairs: `(f1, f2, Δt)`.
*   [ ] **The Fast Index:** 
    *   [x] Construct an **Inverted Index** (Python dictionary) where hashes point to song IDs and timestamps.
    *   [x] Use `pickle` to save the trained index to disk so the app starts instantly.
*   [ ] **The Robust Matcher:**
    *   [x] Implement **Time-Alignment Logic**: Calculate $Offset = Time_{Song} - Time_{Query}$ for all hash hits.
    *   [x] Identify the highest "peak" in a histogram of these offsets to find the correct song.
    *   [x] Calculate a **Confidence Score**: (Aligned Matches / Total Hashes in Query).

---

### Phase 2: The User Interface (Frontend)
*Focus: Clean User Experience*

*   [x] **Audio Input Component:**
    *   [x] Add a **File Uploader** for `.mp3` or `.wav` files.
    *   [x] (Optional/Bonus) Add a **Microphone Recorder** button that captures exactly 10 seconds of audio.
*   [x] **Visual Feedback:**
    *   [x] Include a "Processing..." spinner or progress bar to manage user expectations during the identification lag.
    *   [x] Display a **Waveform or Spectrogram** visualization of the uploaded clip for aesthetic appeal.
*   [x] **Result Display:**
    *   [x] Show the **Best Match** (Song Title & Artist) clearly.
    *   [x] Display the **Confidence Score** as a percentage or a "Match Strength" bar.
    *   [x] (Optional) Add a "Listen on YouTube/Spotify" link for the identified song.

---

### Phase 3: The Connection (API & Integration)
*Focus: Seamless Communication*

*   [x] **Web Framework:** Build a lightweight **FastAPI** or **Flask** server to host your model.
*   [x] **Identification Endpoint:** Create a `POST /identify` route that:
    1.  Receives the audio file from the UI.
    2.  Runs it through the identification model.
    3.  Returns a JSON response: `{ "song": "Name", "artist": "Artist", "confidence": 0.85, "latency": "0.4s" }`.
*   [x] **Latency Tracking:** Use `time.perf_counter()` on the server to measure exactly how long the identification took and send that back to the UI.
*   [x] **Async Processing:** Use `FastAPI`'s async capabilities or a simple thread to ensure that one user's query doesn't block another's.

---

### Phase 4: Final Evaluation (Accuracy & Readiness)
*   [x] **Noise Stress Test:** Verify the model can identify a song even when you play background talking or white noise over the 10-second clip.
*   [x] **Threshold Tuning:** Ensure the app returns "No Match Found" if the confidence score is below a certain limit (e.g., < 10%) to prevent false positives.
*   [x] **Single-Command Launch:** Create a `run.py` that starts both the backend and the UI simultaneously for a smooth judge demo.

