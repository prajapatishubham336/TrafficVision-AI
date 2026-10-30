
from pathlib import Path
from collections import defaultdict
import time

import cv2
from ultralytics import YOLO


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = PROJECT_ROOT / "models" / "vehicle" / "yolo11n.pt"

# COCO class IDs
VEHICLE_CLASSES = [2, 3, 5, 7]
VEHICLE_NAMES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


def main():
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

    model = YOLO(str(MODEL_PATH))
    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        camera.release()
        raise RuntimeError("Webcam open nahi hui.")

    line_y = None
    previous_positions = {}
    counted_ids = set()

    # Direction-wise total counts
    direction_counts = {"IN": 0, "OUT": 0}

    # Direction-wise vehicle category counts
    type_counts = {
        direction: defaultdict(int)
        for direction in ("IN", "OUT")
    }

    # FPS calculation
    previous_frame_time = time.perf_counter()
    fps = 0.0

    print("TrafficVision AI counter started. Exit: Q")

    try:
        while True:
            success, frame = camera.read()

            if not success:
                print("Camera frame read nahi hua.")
                break

            height, width = frame.shape[:2]

            if line_y is None:
                line_y = int(height * 0.60)

            results = model.track(
                source=frame,
                persist=True,
                tracker="bytetrack.yaml",
                classes=VEHICLE_CLASSES,
                conf=0.25,
                verbose=False,
            )

            result = results[0]

            # FPS
            current_time = time.perf_counter()
            elapsed = current_time - previous_frame_time
            previous_frame_time = current_time

            if elapsed > 0:
                instant_fps = 1.0 / elapsed
                fps = instant_fps if fps == 0 else 0.8 * fps + 0.2 * instant_fps

            # Virtual counting line
            cv2.line(
                frame,
                (0, line_y),
                (width, line_y),
                (0, 255, 255),
                2,
            )

            if result.boxes is not None and result.boxes.id is not None:
                boxes = result.boxes.xyxy.cpu().tolist()
                ids = result.boxes.id.int().cpu().tolist()
                classes = result.boxes.cls.int().cpu().tolist()

                for box, track_id, class_id in zip(boxes, ids, classes):
                    x1, y1, x2, y2 = map(int, box)
                    center_x = (x1 + x2) // 2
                    center_y = y2

                    previous_y = previous_positions.get(track_id)
                    direction = None

                    if track_id not in counted_ids and previous_y is not None:
                        if previous_y < line_y <= center_y:
                            direction = "IN"
                        elif previous_y > line_y >= center_y:
                            direction = "OUT"

                    if direction is not None:
                        counted_ids.add(track_id)
                        direction_counts[direction] += 1

                        vehicle_name = VEHICLE_NAMES.get(
                            class_id, model.names[class_id]
                        )
                        type_counts[direction][vehicle_name] += 1

                        print(
                            f"\n{direction}: {vehicle_name} "
                            f"(ID {track_id}) | "
                            f"IN={direction_counts['IN']} "
                            f"OUT={direction_counts['OUT']}"
                        )

                    previous_positions[track_id] = center_y

                    vehicle_name = VEHICLE_NAMES.get(
                        class_id, model.names[class_id]
                    )
                    label = f"ID {track_id} {vehicle_name}"

                    cv2.rectangle(
                        frame, (x1, y1), (x2, y2), (0, 255, 0), 2
                    )
                    cv2.putText(
                        frame,
                        label,
                        (x1, max(y1 - 8, 20)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2,
                    )

            # Dashboard overlay
            panel_lines = [
                f"IN: {direction_counts['IN']}",
                f"OUT: {direction_counts['OUT']}",
                f"Total: {direction_counts['IN'] + direction_counts['OUT']}",
                f"FPS: {fps:.1f}",
                "IN = top to bottom | OUT = bottom to top",
            ]

            y_text = 30
            for text in panel_lines:
                cv2.putText(
                    frame,
                    text,
                    (15, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 255, 255),
                    2,
                )
                y_text += 28

            # Per-type counts
            y_text += 5
            for vehicle_name in ("car", "motorcycle", "bus", "truck"):
                in_count = type_counts["IN"][vehicle_name]
                out_count = type_counts["OUT"][vehicle_name]

                cv2.putText(
                    frame,
                    f"{vehicle_name}: IN {in_count} | OUT {out_count}",
                    (15, y_text),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.55,
                    (255, 255, 255),
                    2,
                )
                y_text += 25

            cv2.imshow("TrafficVision AI - Traffic Counter", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

        print("\n========== FINAL COUNTS ==========")
        print("IN:", direction_counts["IN"])
        print("OUT:", direction_counts["OUT"])
        print("Total crossings:", direction_counts["IN"] + direction_counts["OUT"])

        for direction in ("IN", "OUT"):
            print(f"\n{direction} by vehicle type:")
            for vehicle_name in ("car", "motorcycle", "bus", "truck"):
                print(
                    f"  {vehicle_name}: "
                    f"{type_counts[direction][vehicle_name]}"
                )

        print("\nWebcam stopped.")


if __name__ == "__main__":
    main()
