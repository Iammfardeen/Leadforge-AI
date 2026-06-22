"use client";

import { AlertTriangle, Code2, Eye, Image as ImageIcon, Loader2, Sparkles } from "lucide-react";
import { useEffect, useState } from "react";

import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ApiError, apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";

type Lead = {
  id: string;
  business_name: string;
  website_url: string | null;
};

type Mockup = {
  id: string;
  sections: string[];
  image_prompt: string;
  html_preview: string;
  created_at: string;
};

type ViewMode = "preview" | "code";

export default function RedesignPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [leadsError, setLeadsError] = useState<string | null>(null);
  const [selectedLeadId, setSelectedLeadId] = useState<string>("");

  const [isGenerating, setIsGenerating] = useState(false);
  const [mockup, setMockup] = useState<Mockup | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>("preview");

  useEffect(() => {
    apiFetch<{ leads: Lead[] }>("/leads")
      .then((data) => setLeads(data.leads))
      .catch((err) => setLeadsError(err instanceof ApiError ? err.message : "Could not load leads."));
  }, []);

  function handleSelectLead(id: string) {
    setSelectedLeadId(id);
    setMockup(null);
    setError(null);
  }

  async function handleGenerate() {
    if (!selectedLeadId) return;
    setIsGenerating(true);
    setError(null);
    setMockup(null);

    try {
      const data = await apiFetch<Mockup>(`/mockups/${selectedLeadId}`, { method: "POST" });
      setMockup(data);
      setViewMode("preview");
    } catch (err) {
      setError(
        err instanceof ApiError
          ? err.message
          : "Mockup generation failed. Make sure Ollama is running and the model is pulled."
      );
    } finally {
      setIsGenerating(false);
    }
  }

  const selectedLead = leads.find((l) => l.id === selectedLeadId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">AI Website Redesign</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Generate a homepage wireframe concept — an image prompt plus an HTML preview — for a lead.
        </p>
      </div>

      <Card>
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-[260px] flex-1">
            <label htmlFor="lead-select" className="mb-1.5 block text-xs font-medium text-ink-muted">
              Lead
            </label>
            <select
              id="lead-select"
              value={selectedLeadId}
              onChange={(e) => handleSelectLead(e.target.value)}
              disabled={leads.length === 0}
              className="w-full rounded-md border border-base-border bg-base-raised px-3 py-2 text-sm text-ink focus-visible:border-accent disabled:opacity-50"
            >
              <option value="">{leads.length === 0 ? "No leads saved yet" : "Select a lead…"}</option>
              {leads.map((lead) => (
                <option key={lead.id} value={lead.id}>
                  {lead.business_name}
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            onClick={handleGenerate}
            disabled={!selectedLeadId || isGenerating}
            className="inline-flex items-center gap-1.5 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
            {isGenerating ? "Generating…" : "Generate Mockup"}
          </button>
        </div>
        {isGenerating && (
          <p className="mt-3 text-xs text-ink-subtle">
            Building an image prompt and a full HTML wireframe via your local Ollama model — this can take anywhere
            from 30 seconds to a couple minutes.
          </p>
        )}
        {leadsError && <p className="mt-3 text-xs text-danger">{leadsError}</p>}
      </Card>

      {error && (
        <div className="flex items-start gap-2 rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
          <AlertTriangle size={15} className="mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {!mockup && !error && leads.length === 0 && !leadsError && (
        <EmptyState
          icon={Sparkles}
          title="No leads saved yet"
          description="Save a lead from Lead Finder, then come back here to generate a redesign concept for them."
          action={
            <a
              href="/leads"
              className="inline-flex items-center rounded-md bg-accent px-3 py-1.5 text-sm font-medium text-white hover:bg-accent-hover"
            >
              Go to Lead Finder
            </a>
          }
        />
      )}

      {!mockup && selectedLeadId && !error && !isGenerating && (
        <EmptyState
          icon={Sparkles}
          title="No mockup generated yet"
          description={`Click Generate Mockup to build a homepage concept for ${selectedLead?.business_name ?? "this lead"}.`}
        />
      )}

      {mockup && selectedLead && (
        <div className="space-y-4">
          <Card>
            <div className="mb-3 flex items-center gap-2">
              <ImageIcon size={15} className="text-ink-subtle" />
              <h3 className="text-sm font-semibold text-ink">Hero image prompt</h3>
            </div>
            <p className="rounded-md border border-base-border bg-base-raised px-3 py-2.5 text-sm text-ink-muted">
              {mockup.image_prompt}
            </p>
            <p className="mt-2 text-xs text-ink-subtle">
              Paste this into Midjourney, DALL-E, or Stable Diffusion to generate the hero visual.
            </p>
          </Card>

          <Card className="overflow-hidden p-0">
            <div className="flex items-center justify-between border-b border-base-border px-5 py-3">
              <CardHeader title={`Homepage preview — ${selectedLead.business_name}`} />
              <div className="inline-flex rounded-md border border-base-border bg-base-raised p-0.5">
                <button
                  onClick={() => setViewMode("preview")}
                  className={cn(
                    "inline-flex items-center gap-1.5 rounded-[5px] px-3 py-1 text-xs font-medium transition-colors",
                    viewMode === "preview" ? "bg-accent text-white" : "text-ink-muted hover:text-ink"
                  )}
                >
                  <Eye size={12} /> Preview
                </button>
                <button
                  onClick={() => setViewMode("code")}
                  className={cn(
                    "inline-flex items-center gap-1.5 rounded-[5px] px-3 py-1 text-xs font-medium transition-colors",
                    viewMode === "code" ? "bg-accent text-white" : "text-ink-muted hover:text-ink"
                  )}
                >
                  <Code2 size={12} /> Code
                </button>
              </div>
            </div>

            {viewMode === "preview" ? (
              // sandbox="allow-scripts" only (no allow-same-origin) is intentional:
              // the Tailwind CDN script needs to execute to render any styling at
              // all, but without allow-same-origin the iframe's origin stays opaque,
              // so the AI-generated HTML can't read cookies, localStorage, or reach
              // the parent page even though its own script tag runs.
              <iframe
                srcDoc={mockup.html_preview}
                sandbox="allow-scripts"
                title={`${selectedLead.business_name} homepage preview`}
                className="h-[600px] w-full bg-white"
              />
            ) : (
              <pre className="max-h-[600px] overflow-auto bg-base-raised p-4 text-xs text-ink-muted scrollbar-thin">
                <code>{mockup.html_preview}</code>
              </pre>
            )}
          </Card>

          <Card>
            <h3 className="mb-3 text-sm font-semibold text-ink">Sections included</h3>
            <div className="flex flex-wrap gap-2">
              {mockup.sections.map((s) => (
                <span
                  key={s}
                  className="rounded-full border border-base-border-strong bg-base-raised px-3 py-1 text-xs capitalize text-ink-muted"
                >
                  {s}
                </span>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
