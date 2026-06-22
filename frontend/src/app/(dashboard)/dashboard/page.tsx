import { Search, ScanLine, MessageCircle, Users, TrendingUp, Gauge } from "lucide-react";

import { Card } from "@/components/ui/card";

const STAT_DEFS = [
  { key: "total_leads", label: "Total Leads", icon: Search },
  { key: "analyzed", label: "Analyzed", icon: ScanLine },
  { key: "messages_generated", label: "Messages Generated", icon: MessageCircle },
  { key: "meetings", label: "Meetings", icon: Users },
  { key: "conversion_rate_percent", label: "Conversion Rate", icon: TrendingUp, suffix: "%" },
  { key: "average_lead_score", label: "Avg. Lead Score", icon: Gauge },
];

export default async function DashboardPage() {
  // NOTE (foundation phase): summary stats will be wired to GET /reports/summary
  // once the backend is reachable from server components (requires forwarding
  // the user's Supabase session as a Bearer token server-side). For now the
  // shell renders with zeroed placeholders so the layout is real and final.
  const stats: Record<string, number | null> = {
    total_leads: 0,
    analyzed: 0,
    messages_generated: 0,
    meetings: 0,
    conversion_rate_percent: 0,
    average_lead_score: null,
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Dashboard</h1>
        <p className="mt-1 text-sm text-ink-muted">An overview of your pipeline, at a glance.</p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-3 xl:grid-cols-6">
        {STAT_DEFS.map((item) => {
          const { key, label, icon: Icon } = item;
          // Safely extract suffix by checking if it exists on the item object dynamically
          const suffix = "suffix" in item ? (item as any).suffix : "";
          const value = stats[key];

          return (
            <Card key={key} className="p-4">
              <div className="mb-2 flex items-center justify-between">
                <span className="text-xs font-medium text-ink-muted">{label}</span>
                <Icon size={14} className="text-ink-subtle" />
              </div>
              <p className="font-mono text-2xl font-semibold text-ink">
                {value === null ? "—" : value}
                {value !== null && suffix}
              </p>
            </Card>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card className="p-4">
          <h3 className="mb-1 text-sm font-semibold text-ink">Get started</h3>
          <p className="mb-4 text-sm text-ink-muted">
            Run your first search in Lead Finder to start building your pipeline.
          </p>
          <a
            href="/leads"
            className="inline-flex items-center gap-1.5 rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent-hover"
          >
            <Search size={14} />
            Find leads
          </a>
        </Card>

        <Card className="p-4">
          <h3 className="mb-1 text-sm font-semibold text-ink">Recent activity</h3>
          <p className="text-sm text-ink-muted">Nothing yet. Activity will appear here as you work leads.</p>
        </Card>
      </div>
    </div>
  );
}
