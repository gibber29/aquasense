export type Summary = {
  today_usage: number;
  weekly_average: number;
  monthly_total: number;
  active_alerts: number;
};

export type UsagePoint = {
  date: string;
  usage: number;
  is_anomaly?: boolean;
};

export type PredictionPoint = {
  date: string;
  predicted_usage: number;
};

export type DashboardData = {
  summary: Summary;
  weekly: UsagePoint[];
  history: UsagePoint[];
  predictions: PredictionPoint[];
  anomalies: { date: string; usage: number; type: string; severity: number }[];
  alerts: { id: number; message: string; created_at: string; resolved: boolean }[];
  gamification: { streak_count: number; conservation_score: number; badges: string[] };
};
