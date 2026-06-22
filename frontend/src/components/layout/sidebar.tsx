"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NAV_ITEMS } from "@/lib/nav-items";
import { cn } from "@/lib/utils";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex h-screen w-60 flex-col border-r border-base-border bg-base-surface">
      <div className="flex h-14 items-center gap-2 border-b border-base-border px-4">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent font-mono text-xs font-bold text-white">
          L
        </div>
        <span className="text-sm font-semibold text-ink">LeadForge AI</span>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto p-3 scrollbar-thin">
        {NAV_ITEMS.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition-colors",
                isActive
                  ? "bg-accent/10 font-medium text-accent"
                  : "text-ink-muted hover:bg-base-raised hover:text-ink"
              )}
            >
              <Icon size={16} strokeWidth={2} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-base-border p-3">
        <p className="px-3 text-xs text-ink-subtle">v0.1.0 · foundation phase</p>
      </div>
    </aside>
  );
}
