import { FileText } from "lucide-react";

import { EmptyState } from "@/components/ui/empty-state";

export default function ProposalsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Proposal Generator</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Build a PDF proposal with pricing, timeline, deliverables, and a digital signature area.
        </p>
      </div>

      <EmptyState
        icon={FileText}
        title="No proposals yet"
        description="Open a lead to create a proposal. Once generated, it's saved here and tracked through to signed."
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
