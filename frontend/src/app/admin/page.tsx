"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

export default function AdminPage() {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    api.adminStats().then(setStats).catch(() => setStats(null));
  }, []);

  return (
    <AppShell>
      <main className="mx-auto max-w-[1180px] px-6 pb-32 pt-8">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-[#1261ad]">Admin Panel</h1>
          <a className="rounded-md bg-[#3b8edb] px-4 py-3 font-bold text-white" href="http://localhost:8000/admin/export-csv">Export CSV</a>
        </div>
        {!stats ? (
          <div className="metric-card p-6 font-semibold text-slate-600">Admin login required. Use admin@aquasense.local / admin123.</div>
        ) : (
          <>
            <section className="grid gap-5 md:grid-cols-3">
              <div className="metric-card p-5"><p className="text-sm font-bold uppercase text-slate-500">Total users</p><p className="mt-3 text-3xl font-bold text-[#1261ad]">{stats.total_users}</p></div>
              <div className="metric-card p-5"><p className="text-sm font-bold uppercase text-slate-500">Total usage</p><p className="mt-3 text-3xl font-bold text-[#1261ad]">{stats.total_water_usage}L</p></div>
              <div className="metric-card p-5"><p className="text-sm font-bold uppercase text-slate-500">Total anomalies</p><p className="mt-3 text-3xl font-bold text-red-500">{stats.total_anomalies}</p></div>
            </section>
            <section className="mt-6 grid gap-6 lg:grid-cols-2">
              <div className="metric-card p-5">
                <h2 className="mb-4 text-xl font-bold">Top 5 Highest Consumers</h2>
                <div className="space-y-3">{stats.top_consumers.map((user: any) => <p key={user.name} className="flex justify-between rounded-md bg-aqua-50 p-3 font-semibold"><span>{user.name}</span><span>{user.total}L</span></p>)}</div>
              </div>
              <div className="metric-card p-5">
                <h2 className="mb-4 text-xl font-bold">All Alerts</h2>
                <div className="max-h-[360px] space-y-3 overflow-auto">{stats.alerts.map((alert: any) => <p key={alert.id} className="rounded-md bg-red-50 p-3 text-sm font-semibold text-red-700">{alert.message}</p>)}</div>
              </div>
            </section>
          </>
        )}
      </main>
    </AppShell>
  );
}
