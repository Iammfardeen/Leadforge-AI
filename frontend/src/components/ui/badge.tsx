import { cn } from "@/lib/utils";

const STATUS_STYLES: Record<string, string> = {
  new: "bg-base-raised text-ink-muted border-base-border-strong",
  contacted: "bg-accent/10 text-accent border-accent/30",
  replied: "bg-accent/10 text-accent border-accent/30",
  interested: "bg-warning/10 text-warning border-warning/30",
  meeting: "bg-warning/10 text-warning border-warning/30",
  proposal_sent: "bg-warning/10 text-warning border-warning/30",
  won: "bg-success/10 text-success border-success/30",
  lost: "bg-danger/10 text-danger border-danger/30",
  archived: "bg-base-raised text-ink-subtle border-base-border",
};

export function StatusBadge({ status }: { status: string }) {
  const style = STATUS_STYLES[status] ?? STATUS_STYLES.new;
  const label = status.replace(/_/g, " ");

  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-medium capitalize",
        style
      )}
    >
      {label}
    </span>
  );
}

export function Badge({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border border-base-border-strong bg-base-raised px-2.5 py-0.5 text-xs font-medium text-ink-muted",
        className
      )}
    >
      {children}
    </span>
  );
}
