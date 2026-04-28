import type { DashboardData } from "@/types/aquasense";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export function getToken() {
  if (typeof window === "undefined") return "";
  return localStorage.getItem("aquasense_token") || "";
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {})
    }
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export const api = {
  login: (email: string, password: string) => request<{ access_token: string; role: string; name: string }>("/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  register: (payload: { name: string; email: string; password: string; city: string }) => request("/register", { method: "POST", body: JSON.stringify(payload) }),
  dashboard: () => request<DashboardData>("/dashboard"),
  history: (period = "month", page = 1) => request<{ items: any[]; total: number; page: number; size: number }>(`/usage-history?period=${period}&page=${page}&size=10`),
  logUsage: (payload: { date: string; usage_liters: number; time_of_day: string }) => request("/log-usage", { method: "POST", body: JSON.stringify(payload) }),
  metrics: () => request<{ model: string; r2_score: number; rmse: number }[]>("/model-metrics"),
  train: () => request<{ model: string; r2_score: number; rmse: number }[]>("/train-models", { method: "POST" }),
  adminStats: () => request<any>("/admin/stats"),
  cost: (cost_per_liter: number) => request<any>("/cost-estimator", { method: "POST", body: JSON.stringify({ cost_per_liter }) }),
  chat: (message: string) => request<{ answer: string }>("/chatbot", { method: "POST", body: JSON.stringify({ message }) })
};
