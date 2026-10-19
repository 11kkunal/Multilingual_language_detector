let mediaRecorder;
let audioChunks = [];

const startBtn = document.getElementById("startBtn");
const stopBtn = document.getElementById("stopBtn");
const statusText = document.getElementById("status");

startBtn.onclick = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    mediaRecorder = new MediaRecorder(stream);
    mediaRecorder.start();

    audioChunks = [];

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    startBtn.classList.add("recording");
    statusText.innerText = "🎙️ Recording...It may take a moment !";
    startBtn.disabled = true;
    stopBtn.disabled = false;
};

stopBtn.onclick = () => {
    mediaRecorder.stop();

    mediaRecorder.onstop = async () => {
        const blob = new Blob(audioChunks, { type: "audio/wav" });

        const formData = new FormData();
        formData.append("audio", blob, "audio.wav");

        statusText.innerText = "⏳ Processing...";

        startBtn.classList.remove("recording");  // ❗ stop start pulse
        stopBtn.classList.add("recording");      // ❗ start stop pulse

        const response = await fetch("/detect", {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        document.getElementById("textOutput").innerText = data.text;
        document.getElementById("langOutput").innerText = data.language;
        document.getElementById("confOutput").innerText = data.confidence + "%";

        startBtn.classList.remove("recording");
        statusText.innerText = "✅ Done";

        startBtn.disabled = false;
        stopBtn.disabled = true;

        stopBtn.classList.remove("recording");   // ❗ stop stop pulse
    };
};