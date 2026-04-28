"use client";

import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip
} from "chart.js";
import { Bar, Line } from "react-chartjs-2";
import type { PredictionPoint, UsagePoint } from "@/types/aquasense";

ChartJS.register(CategoryScale, LinearScale, BarElement, LineElement, PointElement, Tooltip, Legend, Filler);

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    x: { grid: { display: false } },
    y: { beginAtZero: true, grid: { color: "#e7eef8" } }
  }
};

export function WeeklyChart({ data }: { data: UsagePoint[] }) {
  return (
    <Bar
      options={options}
      data={{
        labels: data.map((point) => point.date),
        datasets: [{ data: data.map((point) => point.usage), backgroundColor: data.map((point) => (point.is_anomaly ? "#ef4444" : "#3b8edb")), borderRadius: 6 }]
      }}
    />
  );
}

export function PredictionChart({ data }: { data: PredictionPoint[] }) {
  return (
    <Line
      options={options}
      data={{
        labels: data.map((point) => point.date),
        datasets: [{ data: data.map((point) => point.predicted_usage), borderColor: "#14b8a6", backgroundColor: "rgba(20,184,166,.14)", fill: true, tension: 0.35, pointRadius: 4 }]
      }}
    />
  );
}

export function TrendChart({ data }: { data: UsagePoint[] }) {
  return (
    <Line
      options={options}
      data={{
        labels: data.map((point) => point.date),
        datasets: [{ data: data.map((point) => point.usage), borderColor: "#2563eb", backgroundColor: "rgba(37,99,235,.1)", fill: true, tension: 0.32, pointRadius: 2 }]
      }}
    />
  );
}
