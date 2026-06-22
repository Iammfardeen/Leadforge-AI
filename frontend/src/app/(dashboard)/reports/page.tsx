"use client";

import { useState } from "react";
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";

type Interval = "daily" | "weekly" | "monthly";

const PLACEHOLDER_SERIES = [
  { date: "Mon", count: 0 },
  { date: "Tue", count: 0 },
  { date: "Wed", count: 0 },
  { date: "Thu", count: 0 },
  { date: "Fri", count: 0 },
  { date: "Sat", count: 0 },
  { date: "Sun", count: 0 },
];

export default function ReportsPage() {
  const [interval, setInterval] = useState<Interval>("daily");

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Reports</h1>
        <p className="mt-1 text-sm text-ink-muted">Track lead volume and pipeline performance over time.</p>
      </div>

      <Card>
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-ink">New leads</h3>
          <div className="inline-flex rounded-md border border-base-border bg-base-raised p-0.5">
            {(["daily", "weekly", "monthly"] as Interval[]).map((opt) => (
              <button
                key={opt}
                onClick={() => setInterval(opt)}
                className={cn(
                  "rounded-[5px] px-3 py-1 text-xs font-medium capitalize transition-colors",
                  interval === opt ? "bg-accent text-white" : "text-ink-muted hover:text-ink"
                )}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>

        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={PLACEHOLDER_SERIES}>
              <XAxis dataKey="date" stroke="#71717A" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis stroke="#71717A" fontSize={12} tickLine={false} axisLine={false} width={24} />
              <Tooltip
                contentStyle={{ background: "#1B1B1E", border: "1px solid #262629", borderRadius: 8, fontSize: 12 }}
              />
              <Line type="monotone" dataKey="count" stroke="#6366F1" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <p className="mt-2 text-center text-xs text-ink-subtle">
          No lead activity yet — this chart will populate as you add leads.
        </p>
      </Card>
    </div>
  );
}
