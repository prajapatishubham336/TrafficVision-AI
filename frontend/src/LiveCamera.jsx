
import { useEffect, useRef, useState } from "react";

const API = "http://127.0.0.1:8000";

export default function LiveCamera() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const timerRef = useRef(null);
  const frameUrlRef = useRef(null);
  const busyRef = useRef(false);
  const activeRef = useRef(false);

  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");
  const [frameUrl, setFrameUrl] = useState("");

  async function openCamera() {
    try {
      setError("");

      if (!navigator.mediaDevices?.getUserMedia) {
        throw new Error(
          "Camera API unavailable. Open the website using localhost or HTTPS."
        );
      }

      // Browser camera permission
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: "environment",
        },
        audio: false,
      });

      streamRef.current = stream;

      const video = videoRef.current;
      video.srcObject = stream;

      await video.play();

      activeRef.current = true;
      setRunning(true);

    } catch (err) {
      setError("Camera access failed: " + err.message);
      stopCamera();
    }
  }

  async function sendFrame() {
    if (!activeRef.current || busyRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;

    if (!video || !canvas || video.readyState < 2) return;

    busyRef.current = true;

    try {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      const context = canvas.getContext("2d");

      context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
      );

      const blob = await new Promise((resolve) => {
        canvas.toBlob(resolve, "image/jpeg", 0.70);
      });

      if (!blob) {
        throw new Error("Could not capture camera frame");
      }

      const controller = new AbortController();

      const timeout = setTimeout(() => {
        controller.abort();
      }, 15000);

      let response;

      try {
        response = await fetch(`${API}/api/traffic/process-frame`, {
          method: "POST",
          headers: {
            "Content-Type": "image/jpeg",
          },
          body: blob,
          signal: controller.signal,
        });
      } finally {
        clearTimeout(timeout);
      }

      if (!response.ok) {
        const detail = await response.text();
        throw new Error(`Backend HTTP ${response.status}: ${detail}`);
      }

      const processedBlob = await response.blob();

      if (!processedBlob.type.includes("image")) {
        throw new Error("Backend did not return a processed image");
      }

      const newUrl = URL.createObjectURL(processedBlob);

      if (frameUrlRef.current) {
        URL.revokeObjectURL(frameUrlRef.current);
      }

      frameUrlRef.current = newUrl;
      setFrameUrl(newUrl);
      setError("");

    } catch (err) {
      if (err.name === "AbortError") {
        setError("Backend processing timeout. Check YOLO performance.");
      } else {
        setError("Frame processing failed: " + err.message);
      }

    } finally {
      busyRef.current = false;
    }
  }

  function stopCamera() {
    activeRef.current = false;

    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }

    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }

    if (videoRef.current) {
      videoRef.current.pause();
      videoRef.current.srcObject = null;
    }

    if (frameUrlRef.current) {
      URL.revokeObjectURL(frameUrlRef.current);
      frameUrlRef.current = null;
    }

    busyRef.current = false;

    setRunning(false);
    setFrameUrl("");
  }

  useEffect(() => {
    if (running) {
      // Approximately 3 frames per second; actual rate depends on YOLO speed.
      timerRef.current = setInterval(sendFrame, 350);
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
    };
  }, [running]);

  useEffect(() => {
    return () => {
      activeRef.current = false;

      if (timerRef.current) {
        clearInterval(timerRef.current);
      }

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }

      if (frameUrlRef.current) {
        URL.revokeObjectURL(frameUrlRef.current);
      }
    };
  }, []);

  return (
    <div className="panel camera-panel">
      <div className="panel-heading">
        <div>
          <h3>Live Vehicle Detection</h3>
          <p>YOLO11n · Car · Motorcycle · Bus · Truck</p>
        </div>

        <span className="live-tag">
          {running ? "CAMERA ACTIVE" : "CAMERA STOPPED"}
        </span>
      </div>

      <div className="camera-frame">
        {frameUrl ? (
          <img
            src={frameUrl}
            alt="Real-time YOLO vehicle detection"
            style={{
              display: "block",
              width: "100%",
              height: "100%",
              objectFit: "contain",
            }}
          />
        ) : (
          <div className="camera-placeholder">
            <strong>
              {running
                ? "Waiting for YOLO processed frame..."
                : "Camera is stopped"}
            </strong>

            <span>
              Click Open Camera to start live vehicle detection.
            </span>
          </div>
        )}
      </div>

      <video
        ref={videoRef}
        autoPlay
        muted
        playsInline
        style={{ display: "none" }}
      />

      <canvas
        ref={canvasRef}
        style={{ display: "none" }}
      />

      {error && (
        <p
          style={{
            color: "#dc2626",
            fontSize: "13px",
            marginTop: "10px",
            overflowWrap: "anywhere",
          }}
        >
          {error}
        </p>
      )}

      <div style={{ display: "flex", gap: 10, marginTop: 15 }}>
        {!running ? (
          <button onClick={openCamera}>
            Open Camera
          </button>
        ) : (
          <button onClick={stopCamera}>
            Stop Camera
          </button>
        )}
      </div>
    </div>
  );
}
