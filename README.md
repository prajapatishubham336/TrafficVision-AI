# TrafficVision-AI
Real-Time AI-powered Vehicle Detection, Tracking &amp; Traffic Monitoring System using YOLO11n, ByteTrack, OpenCV, FastAPI, React and SQLite.


# 🚦 TrafficVision AI
### Real-Time Vehicle Detection, Tracking & Traffic Monitoring System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/YOLO-11n-purple" />
  <img src="https://img.shields.io/badge/Computer%20Vision-Deep%20Learning-green" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" />
  <img src="https://img.shields.io/badge/React-Frontend-61DAFB?logo=react" />
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite" />
</p>

<p align="center">
  <b>An AI-powered traffic monitoring application that detects, tracks, and counts vehicles in real time using Computer Vision and Deep Learning.</b>
</p>

---

## 📌 Overview

**TrafficVision AI** is a real-time vehicle detection and traffic monitoring system developed using Computer Vision and Deep Learning.

The application uses the **YOLO11n object detection model** to identify vehicles from live webcam video streams and **ByteTrack** to track individual vehicles across consecutive frames.

It automatically detects vehicle movement across a virtual counting line and calculates incoming (IN) and outgoing (OUT) traffic. The processed video, vehicle tracking IDs, and traffic statistics are displayed through an interactive React dashboard.

Traffic crossing events are stored in an SQLite database for record keeping.

The main objective of this project is to demonstrate how AI-based Computer Vision can be applied to real-world traffic monitoring and intelligent transportation systems.

## ✨ Key Features

- 🎥 **Real-Time Webcam Detection** – Captures live video directly from the browser webcam.
- 🚗 **Vehicle Detection** – Detects cars, motorcycles, buses, and trucks.
- 🎯 **Object Tracking** – Tracks individual vehicles using ByteTrack.
- 🏷️ **Unique Tracking IDs** – Assigns tracking IDs to detected vehicles.
- 📦 **Bounding Boxes** – Displays bounding boxes and vehicle labels.
- ↕️ **IN/OUT Traffic Counting** – Counts vehicles based on their direction of movement.
- 📊 **Live Dashboard** – Displays traffic statistics and vehicle classification.
- 💾 **Database Integration** – Saves vehicle crossing records in SQLite.
- ⚡ **REST API** – Connects the React frontend with the FastAPI backend.

## 🧠 AI & Computer Vision Technologies

| Technology | Application |
|---|---|
| YOLO11n | Real-time vehicle detection |
| ByteTrack | Multi-object tracking |
| OpenCV | Image and video processing |
| Deep Learning | Vehicle classification and detection |
| Computer Vision | Visual traffic analysis |

### Supported Vehicle Classes

| Vehicle | COCO Class ID |
|---|---:|
| Car | 2 |
| Motorcycle | 3 |
| Bus | 5 |
| Truck | 7 |

## ⚙️ Technology Stack

### Backend
- Python 3.10
- FastAPI
- Ultralytics YOLO
- OpenCV
- SQLAlchemy
- SQLite

### Frontend
- React.js
- Vite
- JavaScript
- CSS

### AI / ML
- YOLO11n
- ByteTrack
- Object Detection
- Multi-Object Tracking

### Development & Deployment
- Git
- GitHub
- Render (planned deployment)

## 🏗️ System Architecture

```text
          USER
           |
           v
    React Web Dashboard
           |
           v
     Browser Webcam
           |
           v
      Video Frames
           |
           v
     FastAPI Backend
           |
           v
      OpenCV Processing
           |
           v
       YOLO11n Model
           |
           v
      Vehicle Detection
           |
           v
       ByteTrack
           |
           v
    Vehicle Tracking IDs
           |
           v
    IN / OUT Line Counting
           |
           v
      SQLite Database
           |
           v
   Traffic Statistics
           |
           v
    React Dashboard
```

## 🔄 How It Works

1. The user opens the TrafficVision AI web application.
2. The browser requests permission to access the webcam.
3. The webcam captures live video frames.
4. Frames are transmitted to the FastAPI backend.
5. OpenCV processes the incoming frames.
6. YOLO11n detects vehicles in each frame.
7. ByteTrack assigns and maintains tracking IDs.
8. A virtual horizontal line is used to identify vehicle movement.
9. Vehicles crossing the line are classified as IN or OUT.
10. Traffic statistics are updated and crossing records are saved in SQLite.
11. Annotated video frames are returned to the React dashboard.

## 📐 Vehicle Counting Logic

The application uses a virtual horizontal counting line positioned at approximately 60% of the frame height.

**IN Direction:**
- A vehicle moves from above the counting line to below it.
- The incoming vehicle counter is incremented.

**OUT Direction:**
- A vehicle moves from below the counting line to above it.
- The outgoing vehicle counter is incremented.

Each tracked vehicle ID is counted only once during its tracking lifecycle to prevent duplicate crossing counts.

## 📊 Dashboard Metrics

The dashboard provides the following traffic information:

- Total vehicle crossings
- Incoming vehicle count
- Outgoing vehicle count
- Processing speed (FPS)
- Vehicle-wise classification
- Live annotated camera feed

## 🗄️ Database

TrafficVision AI uses SQLite to store vehicle crossing events.

Each saved record contains:

| Field | Description |
|---|---|
| ID | Unique database record ID |
| Vehicle Type | Car, Motorcycle, Bus, or Truck |
| Direction | IN or OUT |
| Tracking ID | Vehicle tracking identifier |
| Timestamp | Date and time of crossing |

## 📁 Project Structure

```text
TrafficVision-AI/
│
├── backend/
│   ├── main.py
│   ├── api/
│   ├── database/
│   └── services/
│       ├── database.py
│       ├── traffic_runtime.py
│       └── webcam_detector.py
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── assets/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── LiveCamera.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── package.json
│   ├── package-lock.json
│   ├── index.html
│   └── vite.config.js
│
├── models/
│   └── vehicle/
│       └── yolo11n.pt
│
├── requirements.txt
├── .gitignore
└── README.md
```

## 🚀 Installation & Setup

Follow these steps to run TrafficVision AI locally.

### 1. Clone the Repository

```bash
git clone https://github.com/prajapatishubham336/TrafficVision-AI.git
```

```bash
cd TrafficVision-AI
```

### 2. Create a Python Environment

```bash
conda create -n llmapp python=3.10 -y
```

```bash
conda activate llmapp
```

### 3. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the FastAPI Backend

From the project root directory:

```bash
python -m uvicorn backend.main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

API Documentation:

```text
http://127.0.0.1:8000/docs
```

### 5. Install Frontend Dependencies

Open another terminal:

```bash
cd frontend
```

```bash
npm install
```

### 6. Run the React Frontend

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

### 7. Start Vehicle Detection

1. Open the frontend URL in your browser.
2. Click on Open Camera.
3. Allow webcam permissions.
4. Show a traffic video or vehicles in front of the camera.
5. Observe real-time detection, tracking IDs, and IN/OUT counting.

**Note:** The YOLO model file must be available at `models/vehicle/yolo11n.pt`. Browser webcam access requires HTTPS in production or localhost during local development.

## 🔮 Future Enhancements

The following features are planned for future development:

- 📈 Historical traffic analytics and reports
- 🚦 Traffic congestion detection
- 🔢 Automatic Number Plate Recognition (ANPR)
- 📷 Multiple camera integration
- 🗺️ Smart traffic monitoring across multiple locations
- 📊 Advanced traffic visualization
- ☁️ Cloud deployment and scalable infrastructure
- 🤖 AI-powered traffic pattern analysis

## ☁️ Deployment

The application is planned for deployment on **Render**.

Proposed deployment architecture:

- Frontend: React + Vite Static Site
- Backend: FastAPI Web Service
- AI Model: YOLO11n
- Database: SQLite with persistent storage

Deployment and production testing are still in progress.

## 🎯 Project Objectives

- Apply Computer Vision to a real-world traffic monitoring problem.
- Understand and implement object detection using YOLO.
- Implement multi-object tracking using ByteTrack.
- Develop vehicle counting logic using tracking coordinates.
- Integrate an AI model with a FastAPI backend.
- Build an interactive frontend using React.
- Store traffic events using a relational database.

## 👨‍💻 Author

<p align="center">
  <b>Shubham Prajapati</b><br/>
  AI/ML Engineer | Generative AI Developer
  <br/><br/>
  <a href="https://github.com/prajapatishubham336">
    <img src="https://img.shields.io/badge/GitHub-prajapatishubham336-181717?logo=github" />
  </a>
</p>

**GitHub:** [@prajapatishubham336](https://github.com/prajapatishubham336)

**Areas of Interest:**
- Artificial Intelligence
- Machine Learning
- Deep Learning
- Computer Vision
- Generative AI
- Large Language Models (LLMs)

---

<p align="center">
  <b>TrafficVision AI – Making Traffic Monitoring Smarter with AI 🚦</b>
  <br/>
  Built with ❤️ by Shubham Prajapati
</p>
