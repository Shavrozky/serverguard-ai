import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

const API_URL = "http://localhost:8095";

function App() {
  const [metrics, setMetrics] = useState([]);
  const [latest, setLatest] = useState(null);
  const [health, setHealth] = useState({
    status: "unknown",
    message: "Loading health status...",
    issues: [],
  });

  async function fetchMetrics() {
    try {
      const response = await fetch(`${API_URL}/metrics?limit=50`);
      const data = await response.json();

      const formattedData = data.map((item) => ({
        ...item,
        time: new Date(item.created_at).toLocaleTimeString(),
      }));

      setMetrics(formattedData);
      setLatest(formattedData[formattedData.length - 1] || null);
    } catch (error) {
      console.error("Failed to fetch metrics:", error);
    }
  }

  async function fetchHealth() {
    try {
      const response = await fetch(`${API_URL}/health`);
      const data = await response.json();

      setHealth(data);
    } catch (error) {
      console.error("Failed to fetch health:", error);
      setHealth({
        status: "unknown",
        message: "Failed to connect to backend",
        issues: [],
      });
    }
  }

  async function refreshDashboard() {
    await fetchMetrics();
    await fetchHealth();
  }

  useEffect(() => {
    refreshDashboard();

    const interval = setInterval(() => {
      refreshDashboard();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  return (
    <main className="container">
      <section className="header">
        <div>
          <h1>ServerGuard AI</h1>
          <p>Simple server monitoring dashboard</p>
        </div>

        <div className={`status-card status-${health.status}`}>
          <span>Status</span>
          <strong>{formatStatus(health.status)}</strong>
          <p>{health.message}</p>
        </div>
      </section>

      {health.issues.length > 0 && (
        <section className="alert-box">
          <h2>Active Alerts</h2>

          <ul>
            {health.issues.map((issue, index) => (
              <li key={index} className={`alert-${issue.level}`}>
                {issue.message}
              </li>
            ))}
          </ul>
        </section>
      )}

      <section className="cards">
        <MetricCard
          label="CPU Usage"
          value={latest ? latest.cpu_percent : null}
        />

        <MetricCard
          label="RAM Usage"
          value={latest ? latest.ram_percent : null}
        />

        <MetricCard
          label="Disk Usage"
          value={latest ? latest.disk_percent : null}
        />
      </section>

      <section className="chart-card">
        <h2>CPU Usage</h2>
        <MetricChart data={metrics} dataKey="cpu_percent" />
      </section>

      <section className="chart-card">
        <h2>RAM Usage</h2>
        <MetricChart data={metrics} dataKey="ram_percent" />
      </section>

      <section className="chart-card">
        <h2>Disk Usage</h2>
        <MetricChart data={metrics} dataKey="disk_percent" />
      </section>
    </main>
  );
}

function MetricCard({ label, value }) {
  const statusClass = getMetricStatusClass(value);

  return (
    <div className={`card ${statusClass}`}>
      <span>{label}</span>
      <strong>{value !== null ? `${value}%` : "-"}</strong>
    </div>
  );
}

function MetricChart({ data, dataKey }) {
  return (
    <div className="chart-wrapper">
      <ResponsiveContainer width="100%" height={260}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Line
            type="monotone"
            dataKey={dataKey}
            strokeWidth={2}
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function formatStatus(status) {
  const statusMap = {
    healthy: "Healthy",
    warning: "Warning",
    critical: "Critical",
    unknown: "Unknown",
  };

  return statusMap[status] || "Unknown";
}

function getMetricStatusClass(value) {
  if (value === null) {
    return "metric-unknown";
  }

  if (value >= 90) {
    return "metric-critical";
  }

  if (value >= 80) {
    return "metric-warning";
  }

  return "metric-healthy";
}

export default App;