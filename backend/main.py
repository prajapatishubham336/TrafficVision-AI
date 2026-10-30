
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from backend.services.traffic_runtime import traffic_runtime

from fastapi import Request, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from backend.services.database import init_db
import numpy as np
import cv2

app = FastAPI(
    title="TrafficVision AI",
    description="Real-time vehicle detection and traffic analytics API",
    version="0.2.0",
)

@app.on_event("startup")
def startup_event():
    init_db()
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "project": "TrafficVision AI",
        "message": "API is running",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "project": "TrafficVision AI",
    }


@app.get("/api/traffic/status")
def traffic_status():
    return {
        "project": "TrafficVision AI",
        "detector": "YOLO11n",
        "integration_status": "connected",
        "message": "Traffic runtime API is available.",
    }


@app.post("/api/traffic/start")
def start_traffic_detection():
    try:
        started = traffic_runtime.start(camera_index=0)
        if not started:
            return {
                "status": "already_running",
                "message": "Traffic detection pehle se chal raha hai.",
            }

        return {
            "status": "started",
            "message": "Traffic detection start request accepted.",
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/traffic/stop")
def stop_traffic_detection():
    stopped = traffic_runtime.stop()

    if not stopped:
        if traffic_runtime.get_stats()["running"]:
            raise HTTPException(
                status_code=504,
                detail="Detector abhi stop nahi hua. Dobara status check karein.",
            )

        return {
            "status": "not_running",
            "message": "Traffic detection currently run nahi kar raha.",
        }

    return {
        "status": "stopped",
        "message": "Traffic detection stopped.",
    }


@app.get("/api/traffic/stats")
def get_traffic_stats():
    return traffic_runtime.get_stats()


@app.get("/api/traffic/video")
def traffic_video():
    return StreamingResponse(
        traffic_runtime.video_stream(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-cache"},
    )

@app.post("/api/traffic/process-frame")
async def process_camera_frame(request: Request):
    try:
        image_bytes = await request.body()

        if not image_bytes:
            raise HTTPException(
                status_code=400,
                detail="Empty camera frame"
            )

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if frame is None:
            raise HTTPException(
                status_code=400,
                detail="Invalid camera frame"
            )

        processed_frame = traffic_runtime.process_frame(frame)

        return Response(
            content=processed_frame,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-store"
            }
        )

    except HTTPException:
        raise

    except Exception as e:
        print("PROCESS FRAME ERROR:", repr(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )