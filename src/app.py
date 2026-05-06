from __future__ import annotations

import base64
import io
from pathlib import Path

import matplotlib

# Use a headless backend to avoid Tkinter/thread-related crashes
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from src.audioid.config import APP_DIR, DEFAULT_CONFIDENCE_THRESHOLD, SAMPLE_RATE
from src.audioid.fingerprint import log_spectrogram
from src.audioid.service import AudioIdentifierService
from src.health import build_health_status

app = FastAPI(title="Audio Identification System")
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
service = AudioIdentifierService()


@app.on_event("startup")
async def startup() -> None:
    await run_in_threadpool(service.load_or_build)


@app.get("/", response_class=HTMLResponse)
async def home() -> FileResponse:
    return FileResponse(str(Path(APP_DIR) / "templates" / "index.html"))


@app.get("/health")
async def health() -> dict[str, object]:
    return build_health_status(payload=service.payload, ready=service.ready)


@app.post("/identify")
async def identify(
    file: UploadFile = File(...),
    confidence_threshold: float = Form(DEFAULT_CONFIDENCE_THRESHOLD),
) -> dict[str, object]:
    if not file.filename.lower().endswith((".wav", ".mp3", ".webm")):
        raise HTTPException(status_code=400, detail="Only .wav, .mp3, or .webm supported")
    payload = await file.read()
    try:
        result = await run_in_threadpool(service.identify_bytes, payload, confidence_threshold)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal error during identification") from e
    return result


@app.post("/spectrogram")
async def spectrogram(file: UploadFile = File(...)) -> dict[str, str]:
    payload = await file.read()

    def _make_png() -> bytes:
        import soundfile as sf

        signal, sr = sf.read(io.BytesIO(payload))
        if signal.ndim > 1:
            signal = np.mean(signal, axis=1)
        if sr != SAMPLE_RATE:
            import librosa

            signal = librosa.resample(
                signal.astype(np.float32), orig_sr=sr, target_sr=SAMPLE_RATE
            ).astype(np.float32)

        spec = log_spectrogram(signal.astype(np.float32))
        fig, ax = plt.subplots(figsize=(7, 3))
        ax.imshow(spec, aspect="auto", origin="lower", cmap="magma")
        ax.set_title("Query Log-Spectrogram")
        ax.set_xlabel("Time Bins")
        ax.set_ylabel("Freq Bins")
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        return buf.getvalue()

    try:
        png_bytes: bytes = await run_in_threadpool(_make_png)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Could not decode uploaded audio for spectrogram.") from e

    b64 = base64.b64encode(png_bytes).decode("ascii")
    return {"image_base64": b64}

