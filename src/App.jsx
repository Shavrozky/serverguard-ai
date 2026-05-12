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

  useEffect(() => {
    fetchMetrics();

    const interval = setInterval(() => {
      fetchMetrics();
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

        <div className="status-card">
          <span>Status</span>
          <strong>Healthy</strong>
        </div>
      </section>

      <section className="cards">
        <div className="card">
          <span>CPU Usage</span>
          <strong>{latest ? `${latest.cpu_percent}%` : "-"}</strong>
        </div>

        <div className="card">
          <span>RAM Usage</span>
          <strong>{latest ? `${latest.ram_percent}%` : "-"}</strong>
        </div>

        <div className="card">
          <span>Disk Usage</span>
          <strong>{latest ? `${latest.disk_percent}%` : "-"}</strong>
        </div>
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

export default App;