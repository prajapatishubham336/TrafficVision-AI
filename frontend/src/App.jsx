
import LiveCamera from "./LiveCamera";

import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  CarFront,
  Bus,
  Bike,
  Truck,
  ArrowDownToLine,
  ArrowUpFromLine,
  Gauge,
  RefreshCw,
  Wifi,
  WifiOff,
} from "lucide-react";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

import "./App.css";

const API = "http://127.0.0.1:8000";

const emptyStats = {
  in_count: 0,
  out_count: 0,
  total_count: 0,
  fps: 0,
  vehicle_types: {
    car: 0,
    motorcycle: 0,
    bus: 0,
    truck: 0,
  },
  running: false,
  error: null,
};

function Metric({ title, value, icon: Icon, color, note }) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span>{title}</span>
        <span className={`metric-icon ${color}`}>
          <Icon size={20} />
        </span>
      </div>

      <div className="metric-value">{value}</div>
      <div className="metric-note">{note}</div>
    </div>
  );
}

export default function App() {
  const [stats, setStats] = useState(emptyStats);
  const [connected, setConnected] = useState(false);
  const [message, setMessage] = useState("Connecting to backend...");
  const [history, setHistory] = useState([]);
  const [refreshing, setRefreshing] = useState(false);

  const refreshStats = useCallback(async () => {
    try {
      const response = await fetch(`${API}/api/traffic/stats`);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();

      setStats((previous) => ({
        ...previous,
        ...data,
        vehicle_types: {
          ...previous.vehicle_types,
          ...(data.vehicle_types || {}),
        },
      }));

      setConnected(true);
      setMessage(
        data.error
          ? `Detector error: ${data.error}`
          : "Backend connected"
      );

      setHistory((old) => [
        ...old.slice(-29),
        {
          time: new Date().toLocaleTimeString(),
          vehicles: data.total_count ?? 0,
          fps: data.fps ?? 0,
        },
      ]);
    } catch (error) {
      setConnected(false);
      setMessage(
        "Backend unavailable: " + error.message
      );
    }
  }, []);

  useEffect(() => {
    refreshStats();

    const timer = setInterval(refreshStats, 2000);

    return () => clearInterval(timer);
  }, [refreshStats]);

  async function handleRefresh() {
    setRefreshing(true);
    await refreshStats();
    setRefreshing(false);
  }

  const types = stats.vehicle_types || emptyStats.vehicle_types;

  const vehicleRows = [
    { name: "Cars", icon: CarFront, key: "car" },
    { name: "Motorcycles", icon: Bike, key: "motorcycle" },
    { name: "Buses", icon: Bus, key: "bus" },
    { name: "Trucks", icon: Truck, key: "truck" },
  ];

  return (
    <main className="dashboard">
      <header className="topbar">
        <div className="brand">
          <div className="brand-logo">
            <Activity size={25} />
          </div>

          <div>
            <h1>
              TrafficVision <span>AI</span>
            </h1>
            <p>Intelligent traffic monitoring system</p>
          </div>
        </div>

        <div className={`connection ${connected ? "online" : "offline"}`}>
          {connected ? <Wifi size={16} /> : <WifiOff size={16} />}
          {connected ? "API Connected" : "API Disconnected"}
        </div>
      </header>

      <section className="welcome">
        <div>
          <p className="eyebrow">TRAFFIC CONTROL CENTER</p>
          <h2>Real-time Traffic Dashboard</h2>
          <p className="subtitle">
            Live vehicle detection, directional counts and system performance.
          </p>
        </div>

        <div className="controls">
          <button
            className="btn btn-refresh"
            disabled={refreshing}
            onClick={handleRefresh}
            title="Refresh statistics"
          >
            <RefreshCw size={17} />
          </button>
        </div>
      </section>

      <div className="status-line">
        <span className={`status-dot ${connected ? "active" : ""}`} />
        {connected ? "Backend connected" : "Backend disconnected"}
        <span className="status-message">{message}</span>
      </div>

      <section className="metrics-grid">
        <Metric
          title="Total Crossings"
          value={stats.total_count ?? 0}
          icon={Activity}
          color="purple"
          note="IN + OUT line crossings"
        />

        <Metric
          title="Incoming Vehicles"
          value={stats.in_count ?? 0}
          icon={ArrowDownToLine}
          color="blue"
          note="Crossings in IN direction"
        />

        <Metric
          title="Outgoing Vehicles"
          value={stats.out_count ?? 0}
          icon={ArrowUpFromLine}
          color="orange"
          note="Crossings in OUT direction"
        />

        <Metric
          title="Processing Speed"
          value={`${stats.fps ?? 0} FPS`}
          icon={Gauge}
          color="green"
          note="Detector processing rate"
        />
      </section>

      <section className="content-grid">
        <LiveCamera />

        <div className="panel chart-panel">
          <div className="panel-heading">
            <div>
              <h3>Detection Activity</h3>
              <p>Recent API snapshots</p>
            </div>

            <span className="live-tag">
              <span />
              AUTO REFRESH · 2 SEC
            </span>
          </div>

          <div className="chart">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={history}>
                <defs>
                  <linearGradient
                    id="vehicleFill"
                    x1="0"
                    y1="0"
                    x2="0"
                    y2="1"
                  >
                    <stop
                      offset="0%"
                      stopColor="#5c72f2"
                      stopOpacity={0.3}
                    />
                    <stop
                      offset="95%"
                      stopColor="#5c72f2"
                      stopOpacity={0}
                    />
                  </linearGradient>
                </defs>

                <CartesianGrid
                  strokeDasharray="3 3"
                  stroke="#e9edf5"
                />

                <XAxis
                  dataKey="time"
                  tick={{ fontSize: 10 }}
                  minTickGap={35}
                />

                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 11 }}
                />

                <Tooltip />

                <Area
                  type="monotone"
                  dataKey="vehicles"
                  name="Total crossings"
                  stroke="#5c72f2"
                  strokeWidth={2.5}
                  fill="url(#vehicleFill)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div>
              <h3>Vehicle Classification</h3>
              <p>Detected vehicle counts by type</p>
            </div>
          </div>

          <div className="vehicle-table">
            <div className="table-head">
              <span>Vehicle</span>
              <span>Count</span>
            </div>

            {vehicleRows.map(({ name, icon: Icon, key }) => (
              <div className="vehicle-row" key={key}>
                <span className="vehicle-name">
                  <Icon size={19} />
                  {name}
                </span>

                <span>
                  {typeof types[key] === "number"
                    ? types[key]
                    : (types.IN?.[key] ?? 0) +
                      (types.OUT?.[key] ?? 0)}
                </span>
              </div>
            ))}
          </div>

          <div className="classification-total">
            <span>Total counted crossings</span>
            <strong>{stats.total_count ?? 0}</strong>
          </div>
        </div>
      </section>

      <footer>
        <span>
          TrafficVision AI <b>v0.2.0</b>
        </span>
        <span>YOLO11n · ByteTrack · FastAPI</span>
      </footer>
    </main>
  );
}
