"use client";

import { useEffect, useState } from "react";
import AppShell from "@/components/AppShell";
import { api } from "@/lib/api";

export default function HistoryPage() {
  const [period, setPeriod] = useState("month");
  const [rows, setRows] = useState<any[]>([]);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    api.history(period, page).then((result) => {
      setRows(result.items);
      setTotal(result.total);
    }).catch(() => {
      setRows([]);
      setTotal(0);
    });
  }, [period, page]);

  return (
    <AppShell>
      <main className="mx-auto max-w-[1180px] px-6 pb-32 pt-8">
        <div className="mb-5 flex items-center justify-between">
          <h1 className="text-3xl font-bold text-[#1261ad]">Usage History</h1>
          <select className="h-11 rounded-md border px-4" value={period} onChange={(event) => { setPeriod(event.target.value); setPage(1); }}>
            <option value="week">Week</option>
            <option value="month">Month</option>
            <option value="year">Year</option>
          </select>
        </div>
        <div className="metric-card overflow-hidden">
          <table className="w-full border-collapse text-left">
            <thead className="bg-[#e5f1ff] text-sm uppercase tracking-wide text-slate-600">
              <tr><th className="p-4">Date</th><th className="p-4">Usage</th><th className="p-4">Season</th><th className="p-4">Time</th><th className="p-4">Weather</th></tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className={`border-t ${row.is_anomaly ? "bg-red-50 text-red-700" : "bg-white"}`}>
                  <td className="p-4 font-semibold">{row.date}</td>
                  <td className="p-4">{row.usage_liters}L</td>
                  <td className="p-4">{row.season}</td>
                  <td className="p-4">{row.time_of_day}</td>
                  <td className="p-4">{row.temperature}°C · {row.rainfall}mm</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-4 flex items-center justify-between">
          <p className="text-sm font-semibold text-slate-500">{total} records</p>
          <div className="flex gap-2">
            <button className="rounded-md bg-white px-4 py-2 shadow-panel" disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button>
            <button className="rounded-md bg-white px-4 py-2 shadow-panel" onClick={() => setPage(page + 1)}>Next</button>
          </div>
        </div>
      </main>
    </AppShell>
  );
}
