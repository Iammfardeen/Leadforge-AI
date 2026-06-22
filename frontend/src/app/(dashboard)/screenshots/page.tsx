import { Camera } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";

export default function ScreenshotsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Website Screenshots</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Capture and compare before/after screenshots for each lead&apos;s website.
        </p>
      </div>

      <EmptyState
        icon={Camera}
        title="No screenshots yet"
        description="Open a lead to capture its current website screenshot. History is kept automatically so you can compare before and after your redesign."
        action={
          <a
            href="/leads"
            className="inline-flex items-center rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent-hover"
          >
            Go to Lead Finder
          </a>
        }
      />
    </div>
  );
}
