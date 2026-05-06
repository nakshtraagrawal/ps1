const fileInput = document.getElementById("audioFile");
const identifyBtn = document.getElementById("identifyBtn");
const recordBtn = document.getElementById("recordBtn");
const statusDiv = document.getElementById("status");
const resultDiv = document.getElementById("result");
const waveformCanvas = document.getElementById("waveform");
const threshold = document.getElementById("threshold");
const thresholdText = document.getElementById("thresholdText");
const spectrogram = document.getElementById("spectrogram");

let recordedBlob = null;

threshold.addEventListener("input", () => {
  thresholdText.textContent = Number(threshold.value).toFixed(2);
});

fileInput.addEventListener("change", async () => {
  const file = fileInput.files[0];
  if (file) {
    await drawWaveform(file);
    await renderSpectrogram(file);
  }
});

recordBtn.addEventListener("click", async () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    alert("Microphone recording is not supported in this browser.");
    return;
  }
  statusDiv.textContent = "Recording 10 seconds...";
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const recorder = new MediaRecorder(stream);
  const chunks = [];
  recorder.ondataavailable = (e) => chunks.push(e.data);
  recorder.start();
  setTimeout(() => recorder.stop(), 10000);
  recorder.onstop = async () => {
    recordedBlob = new Blob(chunks, { type: "audio/webm" });
    statusDiv.textContent = "Recording complete. Ready to identify.";
    await drawWaveform(recordedBlob);
  };
});

identifyBtn.addEventListener("click", async () => {
  const file = fileInput.files[0] || recordedBlob;
  if (!file) {
    alert("Upload or record an audio clip first.");
    return;
  }
  statusDiv.textContent = "Processing...";
  resultDiv.textContent = "";
  try {
    // Quick health check so we fail fast if server is down.
    const healthRes = await fetch("/health");
    if (!healthRes.ok) throw new Error("Server not reachable");

    const form = new FormData();
    const fileName = fileInput.files[0]?.name || "recorded.webm";
    form.append("file", file, fileName);
    form.append("confidence_threshold", threshold.value);

    const res = await fetch("/identify", { method: "POST", body: form });
    const data = await res.json();

    if (!res.ok || data.error) {
      resultDiv.textContent = data.detail || data.error || "Failed to identify";
      return;
    }
    if (!data.song) {
      resultDiv.textContent = data.reason || "No Match Found";
      return;
    }
    if (!data.matched) {
      resultDiv.innerHTML = `
        <strong>Closest Match (low confidence):</strong> ${data.song}<br/>
        <span>Artist:</span> ${data.artist}<br/>
        <strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%<br/>
        <strong>Latency:</strong> ${data.latency || "-"}<br/>
      `;
      return;
    }
    resultDiv.innerHTML = `
      <strong>Best Match:</strong> ${data.song}<br/>
      <span>Artist:</span> ${data.artist}<br/>
      <strong>Confidence:</strong> ${(data.confidence * 100).toFixed(1)}%<br/>
      <strong>Latency:</strong> ${data.latency}<br/>
      <a href="https://www.youtube.com/results?search_query=${encodeURIComponent(`${data.song} ${data.artist}`)}" target="_blank">Listen on YouTube</a>
    `;
  } catch (error) {
    resultDiv.textContent =
      "Network/server error while identifying. Make sure `python run.py` is running, then retry.";
  } finally {
    statusDiv.textContent = "";
  }
});

async function drawWaveform(file) {
  const arrayBuffer = await file.arrayBuffer();
  const ctx = new AudioContext();
  const audioBuffer = await ctx.decodeAudioData(arrayBuffer.slice(0));
  const channelData = audioBuffer.getChannelData(0);
  const canvasCtx = waveformCanvas.getContext("2d");
  canvasCtx.clearRect(0, 0, waveformCanvas.width, waveformCanvas.height);
  canvasCtx.fillStyle = "#0b1220";
  canvasCtx.fillRect(0, 0, waveformCanvas.width, waveformCanvas.height);
  canvasCtx.strokeStyle = "#38bdf8";
  canvasCtx.beginPath();
  const step = Math.ceil(channelData.length / waveformCanvas.width);
  const amp = waveformCanvas.height / 2;
  for (let i = 0; i < waveformCanvas.width; i++) {
    let min = 1.0;
    let max = -1.0;
    for (let j = 0; j < step; j++) {
      const datum = channelData[i * step + j] || 0;
      if (datum < min) min = datum;
      if (datum > max) max = datum;
    }
    canvasCtx.moveTo(i, (1 + min) * amp);
    canvasCtx.lineTo(i, (1 + max) * amp);
  }
  canvasCtx.stroke();
}

async function renderSpectrogram(file) {
  const form = new FormData();
  form.append("file", file, file.name || "query.wav");
  try {
    const res = await fetch("/spectrogram", { method: "POST", body: form });
    if (!res.ok) return;
    const data = await res.json();
    spectrogram.src = `data:image/png;base64,${data.image_base64}`;
  } catch (_) {
    // Keep UI usable even when preview generation fails.
  }
}

