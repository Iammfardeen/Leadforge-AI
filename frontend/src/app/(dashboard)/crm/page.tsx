import { Plus } from "lucide-react";

const COLUMNS = [
  { status: "new", label: "New" },
  { status: "contacted", label: "Contacted" },
  { status: "replied", label: "Replied" },
  { status: "interested", label: "Interested" },
  { status: "meeting", label: "Meeting" },
  { status: "proposal_sent", label: "Proposal Sent" },
  { status: "won", label: "Won" },
  { status: "lost", label: "Lost" },
] as const;

export default function CrmPage() {
  return (
    <div className="flex h-full flex-col space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold text-ink">CRM</h1>
          <p className="mt-1 text-sm text-ink-muted">Track every lead from first contact to closed deal.</p>
        </div>
        <a
          href="/leads"
          className="inline-flex items-center gap-1.5 rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent-hover"
        >
          <Plus size={14} />
          Add lead
        </a>
      </div>

      <div className="flex-1 overflow-x-auto pb-2 scrollbar-thin">
        <div className="flex h-full gap-3">
          {COLUMNS.map((col) => (
            <div
              key={col.status}
              className="flex w-64 flex-shrink-0 flex-col rounded-card border border-base-border bg-base-surface"
            >
              <div className="flex items-center justify-between border-b border-base-border px-3 py-2.5">
                <span className="text-xs font-medium text-ink-muted">{col.label}</span>
                <span className="rounded-full bg-base-raised px-1.5 py-0.5 font-mono text-[10px] text-ink-subtle">
                  0
                </span>
              </div>
              <div className="flex-1 space-y-2 overflow-y-auto p-2 scrollbar-thin">
                <div className="rounded-md border border-dashed border-base-border p-3 text-center text-xs text-ink-subtle">
                  No leads
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
