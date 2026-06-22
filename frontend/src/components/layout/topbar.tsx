"use client";

import { Bell, Search } from "lucide-react";
import { useRouter } from "next/navigation";

import { createSupabaseBrowserClient } from "@/lib/supabase/client";

export function Topbar({ userEmail }: { userEmail?: string | null }) {
  const router = useRouter();
  const supabase = createSupabaseBrowserClient();

  async function handleLogout() {
    await supabase.auth.signOut();
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="flex h-14 items-center justify-between border-b border-base-border bg-base px-6">
      <div className="relative w-80">
        <Search size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-subtle" />
        <input
          type="search"
          placeholder="Search leads, businesses, phone…"
          className="w-full rounded-md border border-base-border bg-base-surface py-1.5 pl-9 pr-3 text-sm text-ink placeholder:text-ink-subtle focus-visible:border-accent"
        />
      </div>

      <div className="flex items-center gap-4">
        <button
          type="button"
          aria-label="Notifications"
          className="relative rounded-md p-2 text-ink-muted hover:bg-base-surface hover:text-ink"
        >
          <Bell size={17} />
        </button>

        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-base-raised text-xs font-medium text-ink-muted">
            {userEmail ? userEmail.slice(0, 2).toUpperCase() : "?"}
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="text-sm text-ink-muted hover:text-ink"
          >
            Log out
          </button>
        </div>
      </div>
    </header>
  );
}
