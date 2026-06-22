import { type LucideIcon } from "lucide-react";

export function EmptyState({
  icon: Icon,
  title,
  description,
  action,
}: {
  icon: LucideIcon;
  title: string;
  description: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-card border border-dashed border-base-border px-6 py-16 text-center">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-full bg-base-raised text-ink-subtle">
        <Icon size={18} />
      </div>
      <h3 className="text-sm font-medium text-ink">{title}</h3>
      <p className="mt-1 max-w-sm text-sm text-ink-muted">{description}</p>
      {action && <div className="mt-5">{action}</div>}
    </div>
  );
}
