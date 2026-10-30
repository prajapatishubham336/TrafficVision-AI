
import cv2
import time
import threading
from pathlib import Path
from ultralytics import YOLO
from backend.services.database import save_traffic_record

# Project root/models/vehicle/yolo11n.pt
PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "vehicle" / "yolo11n.pt"

# COCO class IDs:
# 2 = Car, 3 = Motorcycle, 5 = Bus, 7 = Truck
VEHICLE_CLASSES = [2, 3, 5, 7]

VEHICLE_NAMES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


class TrafficRuntime:

    def __init__(self):
        self.lock = threading.RLock()

        self.thread = None
        self.stop_event = threading.Event()

        self.running = False
        self.error = None

        self.model = None
        self.latest_frame = None

        self.previous_positions = {}
        self.counted_ids = set()

        self.line_y = None
        self.last_frame_time = time.time()
        self.fps = 0.0

        self.stats = self._empty_stats()

        self._load_model()

    def _empty_stats(self):
        return {
            "in_count": 0,
            "out_count": 0,
            "total_count": 0,
            "fps": 0,
            "vehicle_types": {
                "car": 0,
                "motorcycle": 0,
                "bus": 0,
                "truck": 0,
            },
        }

    def _load_model(self):
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"YOLO model not found: {MODEL_PATH}"
            )

        print(f"Loading YOLO model: {MODEL_PATH}")

        self.model = YOLO(str(MODEL_PATH))

        print("YOLO model loaded successfully!")

    def get_stats(self):
        with self.lock:
            return {
                "in_count": self.stats["in_count"],
                "out_count": self.stats["out_count"],
                "total_count": self.stats["total_count"],
                "fps": self.stats["fps"],
                "vehicle_types": self.stats["vehicle_types"].copy(),
                "running": self.running,
                "error": self.error,
            }

    def reset_stats(self):
        with self.lock:
            self.stats = self._empty_stats()
            self.previous_positions.clear()
            self.counted_ids.clear()

    def process_frame(self, frame):
        """
        Browser webcam se received frame ko YOLO se process karta hai.
        Annotated image ke JPEG bytes return karta hai.
        """

        if frame is None:
            raise ValueError("Invalid camera frame")

        if self.model is None:
            raise RuntimeError("YOLO model is not loaded")

        height, width = frame.shape[:2]

        # Counting line: frame ki 60% height par
        line_y = int(height * 0.60)

        # Model tracking and vehicle detection
        with self.lock:
            results = self.model.track(
                frame,
                persist=True,
                tracker="bytetrack.yaml",
                classes=VEHICLE_CLASSES,
                conf=0.25,
                verbose=False,
            )

            result = results[0]
            annotated_frame = result.plot()

            # Counting line draw karo
            cv2.line(
                annotated_frame,
                (0, line_y),
                (width, line_y),
                (0, 255, 255),
                2,
            )

            cv2.putText(
                annotated_frame,
                "IN / OUT COUNTING LINE",
                (10, max(25, line_y - 10)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
            )

            # Tracking boxes se IDs aur classes nikalo
            if result.boxes is not None and result.boxes.id is not None:

                boxes = result.boxes.xyxy.cpu().numpy()
                track_ids = result.boxes.id.int().cpu().tolist()
                class_ids = result.boxes.cls.int().cpu().tolist()

                for box, track_id, class_id in zip(
                    boxes, track_ids, class_ids
                ):

                    if class_id not in VEHICLE_NAMES:
                        continue

                    x1, y1, x2, y2 = map(int, box)

                    center_x = (x1 + x2) // 2
                    center_y = (y1 + y2) // 2

                    # Vehicle ka previous center point
                    previous_y = self.previous_positions.get(track_id)

                    if previous_y is not None and track_id not in self.counted_ids:

                        direction = None

                        # Top se bottom cross = IN
                        if previous_y < line_y <= center_y:
                            direction = "IN"

                        # Bottom se top cross = OUT
                        elif previous_y > line_y >= center_y:
                            direction = "OUT"

                        
                        if direction:
                            # Is tracking ID ko dobara count hone se roko
                            self.counted_ids.add(track_id)

                            vehicle_name = VEHICLE_NAMES[class_id]

                            # Update live IN/OUT statistics
                            if direction == "IN":
                                self.stats["in_count"] += 1
                            else:
                                self.stats["out_count"] += 1

                            self.stats["total_count"] += 1
                            self.stats["vehicle_types"][vehicle_name] += 1

                            # Save crossing event in SQLite database
                            try:
                                save_traffic_record(
                                    vehicle_type=vehicle_name,
                                    direction=direction,
                                    tracking_id=int(track_id)
                                )

                                print(
                                    f"DATABASE SAVED: {vehicle_name} "
                                    f"ID:{track_id} Direction:{direction}"
                                )

                            except Exception as exc:
                                self.error = f"Database save error: {exc}"
                                print("DATABASE SAVE ERROR:", repr(exc))


                    self.previous_positions[track_id] = center_y

                    # Tracking ID and vehicle label
                    label = VEHICLE_NAMES[class_id] + f" ID:{track_id}"

                    cv2.putText(
                        annotated_frame,
                        label,
                        (x1, max(20, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

            # FPS calculate karo
            current_time = time.time()
            elapsed = current_time - self.last_frame_time

            if elapsed > 0:
                current_fps = 1.0 / elapsed
                self.fps = (
                    current_fps
                    if self.fps == 0
                    else (0.8 * self.fps + 0.2 * current_fps)
                )

            self.last_frame_time = current_time
            self.stats["fps"] = round(self.fps, 2)

            self.latest_frame = annotated_frame.copy()

        # JPEG image bytes
        success, buffer = cv2.imencode(
            ".jpg",
            annotated_frame,
            [cv2.IMWRITE_JPEG_QUALITY, 80],
        )

        if not success:
            raise RuntimeError("Could not encode processed frame")

        return buffer.tobytes()

    def start(self, camera_index=0):
        with self.lock:
            if self.running:
                return {
                    "message": "Traffic detection is already running"
                }

            if self.thread and self.thread.is_alive():
                return {
                    "message": "Previous detection thread is still running"
                }

            self.stop_event.clear()
            self.error = None
            self.running = True

            self.thread = threading.Thread(
                target=self._run,
                args=(camera_index, self.stop_event),
                daemon=True,
            )

            self.thread.start()

        return {"message": "Traffic detection started"}

    def stop(self):
        self.stop_event.set()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)

        with self.lock:
            self.running = False

        return {"message": "Traffic detection stopped"}

    def _run(self, camera_index, stop_event):
        """
        Optional backend webcam worker.
        Browser LiveCamera use karte waqt is worker ko start mat karna.
        """

        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        if not cap.isOpened():
            with self.lock:
                self.error = "Could not open backend camera"
                self.running = False
            return

        try:
            while not stop_event.is_set():

                success, frame = cap.read()

                if not success:
                    time.sleep(0.05)
                    continue

                try:
                    self.process_frame(frame)
                except Exception as exc:
                    with self.lock:
                        self.error = str(exc)
                    break

        except Exception as exc:
            with self.lock:
                self.error = str(exc)

        finally:
            cap.release()

            with self.lock:
                self.running = False

    def video_stream(self):
        """
        Existing /api/traffic/video route ke liye JPEG stream.
        """

        while True:
            with self.lock:
                frame = (
                    self.latest_frame.copy()
                    if self.latest_frame is not None
                    else None
                )

            if frame is None:
                time.sleep(0.05)
                continue

            success, buffer = cv2.imencode(".jpg", frame)

            if not success:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n"
                + buffer.tobytes()
                + b"\r\n"
            )


# Global runtime instance
traffic_runtime = TrafficRuntime()
