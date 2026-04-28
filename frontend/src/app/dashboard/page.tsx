"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import AppShell from "@/components/AppShell";
import { PredictionChart, TrendChart, WeeklyChart } from "@/components/Charts";
import { api, getToken } from "@/lib/api";
import type { DashboardData } from "@/types/aquasense";

const emptyDashboard: DashboardData = {
  summary: { today_usage: 0, weekly_average: 0, monthly_total: 0, active_alerts: 0 },
  weekly: [],
  history: [],
  predictions: [],
  anomalies: [],
  alerts: [],
  gamification: { streak_count: 0, conservation_score: 0, badges: [] }
};

function Metric({ label, value, tone }: { label: string; value: string; tone?: "good" | "bad" }) {
  return (
    <div className="metric-card p-5">
      <p className="text-sm font-bold uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-3 text-3xl font-bold ${tone === "bad" ? "text-red-500" : tone === "good" ? "text-emerald-600" : "text-[#1261ad]"}`}>{value}</p>
    </div>
  );
}

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<DashboardData>(emptyDashboard);
  const [cost, setCost] = useState<any>(null);

  useEffect(() => {
    if (!getToken()) {
      router.push("/login");
      return;
    }
    api.dashboard().then(setData).catch(() => setData(emptyDashboard));
  }, [router]);

  const submitUsage = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    await api.logUsage({
      date: String(form.get("date")),
      usage_liters: Number(form.get("usage")),
      time_of_day: String(form.get("time"))
    });
    setData(await api.dashboard());
    event.currentTarget.reset();
  };

  const estimate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setCost(await api.cost(Number(form.get("cost"))));
  };

  return (
    <AppShell>
      <main className="mx-auto max-w-[1320px] px-6 pb-32 pt-8">
        <div className="mb-7 flex flex-wrap items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-[#1261ad]">Smart Water Monitoring Dashboard</h1>
            <p className="mt-2 text-slate-600">Live usage, anomaly signals, forecasts, and conservation progress.</p>
          </div>
          <a href="http://localhost:8000/docs" className="rounded-md bg-white px-4 py-3 font-semibold text-[#1261ad] shadow-panel">Swagger API</a>
        </div>

        <section className="grid gap-5 md:grid-cols-4">
          <Metric label="Today's usage" value={`${data.summary.today_usage}L`} tone={data.summary.today_usage > 500 ? "bad" : "good"} />
          <Metric label="Weekly average" value={`${data.summary.weekly_average}L`} />
          <Metric label="Monthly total" value={`${data.summary.monthly_total}L`} />
          <Metric label="Active alerts" value={String(data.summary.active_alerts)} tone={data.summary.active_alerts ? "bad" : "good"} />
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-3">
          <div className="metric-card p-5 lg:col-span-2">
            <h2 className="mb-4 text-xl font-bold text-slate-800">Weekly Usage</h2>
            <div className="h-[300px]">{data.weekly.length ? <WeeklyChart data={data.weekly} /> : <EmptyChart />}</div>
          </div>
          <div className="metric-card p-5">
            <h2 className="text-xl font-bold text-slate-800">Gamification</h2>
            <div className="mt-6 grid grid-cols-2 gap-4">
              <Metric label="Streak" value={`${data.gamification.streak_count} days`} tone="good" />
              <Metric label="Score" value={`${data.gamification.conservation_score}%`} tone="good" />
            </div>
            <div className="mt-5 flex flex-wrap gap-2">
              {data.gamification.badges.map((badge) => <span key={badge} className="rounded-md bg-emerald-50 px-3 py-2 text-sm font-bold text-emerald-700">{badge}</span>)}
              {!data.gamification.badges.length && <p className="text-sm font-semibold text-slate-500">No badges yet. Log usage to begin.</p>}
            </div>
          </div>
        </section>

        <section id="predictions" className="mt-6 grid gap-6 lg:grid-cols-2">
          <div className="metric-card p-5">
            <h2 className="mb-4 text-xl font-bold text-slate-800">7-Day Prediction</h2>
            <div className="h-[285px]">{data.predictions.length ? <PredictionChart data={data.predictions} /> : <EmptyChart />}</div>
          </div>
          <div className="metric-card p-5">
            <h2 className="mb-4 text-xl font-bold text-slate-800">Historical Trend</h2>
            <div className="h-[285px]">{data.history.length ? <TrendChart data={data.history} /> : <EmptyChart />}</div>
          </div>
        </section>

        <section className="mt-6 grid gap-6 lg:grid-cols-3">
          <form id="log" onSubmit={submitUsage} className="metric-card p-5">
            <h2 className="mb-4 text-xl font-bold text-slate-800">Log Usage</h2>
            <input name="date" type="date" className="mb-3 h-11 w-full rounded-md border px-3" required />
            <input name="usage" type="number" placeholder="Usage liters" className="mb-3 h-11 w-full rounded-md border px-3" required />
            <select name="time" className="mb-3 h-11 w-full rounded-md border px-3">
              <option>morning</option><option>afternoon</option><option>evening</option><option>night</option>
            </select>
            <button className="h-11 w-full rounded-md bg-[#3b8edb] font-bold text-white">Save Usage</button>
          </form>
          <div className="metric-card p-5">
            <h2 className="mb-4 text-xl font-bold text-slate-800">Active Anomaly Alerts</h2>
            <div className="space-y-3">
              {data.alerts.map((alert) => <p key={alert.id} className="rounded-md border border-red-100 bg-red-50 p-3 text-sm font-semibold text-red-700">{alert.message}</p>)}
              {!data.alerts.length && <p className="rounded-md bg-emerald-50 p-3 text-sm font-semibold text-emerald-700">No active alerts.</p>}
            </div>
          </div>
          <form id="cost" onSubmit={estimate} className="metric-card p-5">
            <h2 className="mb-4 text-xl font-bold text-slate-800">Water Cost Estimator</h2>
            <input name="cost" type="number" step="0.001" placeholder="Cost per liter" className="mb-3 h-11 w-full rounded-md border px-3" required />
            <button className="h-11 w-full rounded-md bg-[#3b8edb] font-bold text-white">Estimate</button>
            {cost && <div className="mt-4 space-y-2 text-sm font-semibold text-slate-700">
              <p>Daily: {cost.daily_cost}</p><p>Monthly: {cost.monthly_projection}</p><p>Annual: {cost.annual_projection}</p><p className="text-emerald-700">Savings: {cost.estimated_savings}</p>
            </div>}
          </form>
        </section>
      </main>
    </AppShell>
  );
}

function EmptyChart() {
  return (
    <div className="flex h-full items-center justify-center rounded-md border border-dashed border-[#c9dff5] bg-aqua-50 text-sm font-semibold text-slate-500">
      No usage data yet. Add a reading to populate this chart.
    </div>
  );
}
