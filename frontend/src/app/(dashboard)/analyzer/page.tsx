"use client";

import {
  AlertTriangle,
  Check,
  Loader2,
  Palette,
  ScanLine,
  Sparkles,
  X,
} from "lucide-react";
import { useEffect, useState } from "react";

import { Card, CardHeader } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ScoreRing } from "@/components/ui/score-ring";
import { ApiError, apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";

type Lead = {
  id: string;
  business_name: string;
  website_url: string | null;
};

type AnalysisReport = {
  id: string;
  has_ssl: boolean | null;
  is_https: boolean | null;
  performance_score: number | null;
  seo_score: number | null;
  accessibility_score: number | null;
  overall_score: number;
  broken_links_count: number | null;
  is_responsive: boolean | null;
  has_favicon: boolean | null;
  has_meta_tags: boolean | null;
  has_open_graph: boolean | null;
  has_schema_markup: boolean | null;
  has_contact_form: boolean | null;
  has_whatsapp_button: boolean | null;
  has_google_maps_embed: boolean | null;
  has_social_links: boolean | null;
  has_dark_mode: boolean | null;
  loading_speed_ms: number | null;
  image_optimization_score: number | null;
  raw_report: Record<string, unknown> | null;
  created_at: string;
};

type AIReport = {
  id: string;
  business_summary: string;
  weaknesses: string[];
  improvements: string[];
  estimated_lost_customers_per_month: number;
  estimated_revenue_increase_monthly: number;
  suggested_features: string[];
  suggested_colors: string[];
  suggested_fonts: string[];
  suggested_design_style: string;
  model_used: string;
  created_at: string;
};

const CHECKLIST_ITEMS: { key: keyof AnalysisReport; label: string }[] = [
  { key: "has_ssl", label: "Valid SSL Certificate" },
  { key: "is_https", label: "HTTPS" },
  { key: "is_responsive", label: "Responsive Design" },
  { key: "has_favicon", label: "Favicon" },
  { key: "has_meta_tags", label: "Meta Tags" },
  { key: "has_open_graph", label: "Open Graph Tags" },
  { key: "has_schema_markup", label: "Schema Markup" },
  { key: "has_contact_form", label: "Contact Form" },
  { key: "has_whatsapp_button", label: "WhatsApp Button" },
  { key: "has_google_maps_embed", label: "Google Maps Embed" },
  { key: "has_social_links", label: "Social Links" },
  { key: "has_dark_mode", label: "Dark Mode" },
];

function CheckRow({ label, value }: { label: string; value: boolean | null }) {
  return (
    <div className="flex items-center justify-between rounded-md border border-base-border bg-base-raised px-3 py-2">
      <span className="text-sm text-ink-muted">{label}</span>
      {value ? (
        <Check size={16} className="text-success" />
      ) : (
        <X size={16} className="text-danger" />
      )}
    </div>
  );
}

function MiniScore({ label, value }: { label: string; value: number | null }) {
  const color =
    value === null ? "text-ink-subtle" : value >= 80 ? "text-success" : value >= 50 ? "text-warning" : "text-danger";
  return (
    <div className="rounded-md border border-base-border bg-base-raised px-3 py-3 text-center">
      <p className={cn("font-mono text-2xl font-semibold", color)}>{value === null ? "—" : value}</p>
      <p className="mt-1 text-xs text-ink-muted">{label}</p>
    </div>
  );
}

function TagList({ items, variant = "default" }: { items: string[]; variant?: "default" | "color" }) {
  return (
    <div className="flex flex-wrap gap-1.5">
      {items.map((item) => (
        <span
          key={item}
          className="inline-flex items-center gap-1.5 rounded-full border border-base-border-strong bg-base-raised px-2.5 py-1 text-xs text-ink-muted"
        >
          {variant === "color" && (
            <span
              className="h-2.5 w-2.5 rounded-full border border-base-border-strong"
              style={{ backgroundColor: item }}
            />
          )}
          {item}
        </span>
      ))}
    </div>
  );
}

export default function AnalyzerPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [leadsError, setLeadsError] = useState<string | null>(null);
  const [selectedLeadId, setSelectedLeadId] = useState<string>("");

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [report, setReport] = useState<AnalysisReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [isGeneratingAI, setIsGeneratingAI] = useState(false);
  const [aiReport, setAiReport] = useState<AIReport | null>(null);
  const [aiError, setAiError] = useState<string | null>(null);

  useEffect(() => {
    apiFetch<{ leads: Lead[] }>("/leads")
      .then((data) => setLeads(data.leads.filter((l) => l.website_url)))
      .catch((err) => setLeadsError(err instanceof ApiError ? err.message : "Could not load leads."));
  }, []);

  function handleSelectLead(id: string) {
    setSelectedLeadId(id);
    setReport(null);
    setAiReport(null);
    setError(null);
    setAiError(null);
  }

  async function handleAnalyze() {
    if (!selectedLeadId) return;
    setIsAnalyzing(true);
    setError(null);
    setReport(null);
    setAiReport(null);

    try {
      const data = await apiFetch<AnalysisReport>(`/analyzer/${selectedLeadId}`, { method: "POST" });
      setReport(data);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Analysis failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  }

  async function handleGenerateAIReport() {
    if (!selectedLeadId) return;
    setIsGeneratingAI(true);
    setAiError(null);

    try {
      const data = await apiFetch<AIReport>(`/ai-reports/${selectedLeadId}`, { method: "POST" });
      setAiReport(data);
    } catch (err) {
      setAiError(
        err instanceof ApiError
          ? err.message
          : "AI report generation failed. Make sure Ollama is running and the model is pulled."
      );
    } finally {
      setIsGeneratingAI(false);
    }
  }

  const selectedLead = leads.find((l) => l.id === selectedLeadId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Website Analyzer</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Run a full technical and design audit against a lead&apos;s website, then generate an AI report.
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
              <option value="">
                {leads.length === 0 ? "No leads with a website yet" : "Select a lead…"}
              </option>
              {leads.map((lead) => (
                <option key={lead.id} value={lead.id}>
                  {lead.business_name} — {lead.website_url}
                </option>
              ))}
            </select>
          </div>

          <button
            type="button"
            onClick={handleAnalyze}
            disabled={!selectedLeadId || isAnalyzing}
            className="inline-flex items-center gap-1.5 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isAnalyzing ? <Loader2 size={14} className="animate-spin" /> : <ScanLine size={14} />}
            {isAnalyzing ? "Analyzing…" : "Analyze"}
          </button>

          <button
            type="button"
            onClick={handleGenerateAIReport}
            disabled={!selectedLeadId || isGeneratingAI}
            className="inline-flex items-center gap-1.5 rounded-md border border-base-border-strong px-4 py-2 text-sm font-medium text-ink hover:bg-base-raised disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isGeneratingAI ? <Loader2 size={14} className="animate-spin" /> : <Sparkles size={14} />}
            {isGeneratingAI ? "Generating…" : "Generate AI Report"}
          </button>
        </div>
        {isAnalyzing && (
          <p className="mt-3 text-xs text-ink-subtle">
            This runs a real Lighthouse audit against the live site — usually takes 5–20 seconds.
          </p>
        )}
        {isGeneratingAI && (
          <p className="mt-3 text-xs text-ink-subtle">
            Asking your local Ollama model for a business summary and redesign suggestions — this can take anywhere
            from a few seconds to a couple minutes depending on your machine.
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

      {aiError && (
        <div className="flex items-start gap-2 rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
          <AlertTriangle size={15} className="mt-0.5 flex-shrink-0" />
          <span>{aiError}</span>
        </div>
      )}

      {!report && !aiReport && !error && leads.length === 0 && !leadsError && (
        <EmptyState
          icon={ScanLine}
          title="No leads with a website yet"
          description="Save a lead that already has a website from Lead Finder to run an analysis against it."
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

      {report && selectedLead && (
        <div className="space-y-4">
          <Card className="flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <ScoreRing score={report.overall_score} size={56} showLabel />
              <div>
                <p className="text-sm font-semibold text-ink">{selectedLead.business_name}</p>
                <p className="text-xs text-ink-muted">{selectedLead.website_url}</p>
              </div>
            </div>
            <p className="text-xs text-ink-subtle">
              Analyzed {new Date(report.created_at).toLocaleString()}
            </p>
          </Card>

          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <MiniScore label="Performance" value={report.performance_score} />
            <MiniScore label="SEO" value={report.seo_score} />
            <MiniScore label="Accessibility" value={report.accessibility_score} />
            <MiniScore label="Image Optimization" value={report.image_optimization_score} />
          </div>

          <Card>
            <CardHeader title="Site checklist" description="Structural and feature checks found on the page." />
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {CHECKLIST_ITEMS.map((item) => (
                <CheckRow key={item.key} label={item.label} value={report[item.key] as boolean | null} />
              ))}
            </div>
          </Card>

          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
            <Card>
              <p className="text-xs text-ink-muted">Broken Links</p>
              <p className="mt-1 font-mono text-xl font-semibold text-ink">
                {report.broken_links_count ?? "—"}
              </p>
            </Card>
            <Card>
              <p className="text-xs text-ink-muted">Loading Speed</p>
              <p className="mt-1 font-mono text-xl font-semibold text-ink">
                {report.loading_speed_ms ? `${(report.loading_speed_ms / 1000).toFixed(1)}s` : "—"}
              </p>
            </Card>
          </div>

          {report.raw_report?.fetch_error ? (
            <p className="text-xs text-ink-subtle">
              Note: the site could not be fetched directly ({String(report.raw_report.fetch_error)}), so some checks
              above default to &quot;not found&quot; rather than confirmed absent.
            </p>
          ) : null}
          {report.raw_report?.pagespeed_error ? (
            <p className="text-xs text-ink-subtle">
              Note: PageSpeed Insights was unavailable for this run, so performance score is a lightweight estimate
              rather than a full Lighthouse audit.
            </p>
          ) : null}
        </div>
      )}

      {aiReport && selectedLead && (
        <div className="space-y-4">
          <Card>
            <div className="mb-3 flex items-center justify-between">
              <CardHeader title="AI Business Summary" />
              <span className="text-xs text-ink-subtle">Model: {aiReport.model_used}</span>
            </div>
            <p className="text-sm text-ink-muted">{aiReport.business_summary}</p>
          </Card>

          <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader title="Weaknesses" />
              <ul className="space-y-1.5">
                {aiReport.weaknesses.map((w) => (
                  <li key={w} className="flex gap-2 text-sm text-ink-muted">
                    <span className="text-danger">•</span>
                    {w}
                  </li>
                ))}
              </ul>
            </Card>
            <Card>
              <CardHeader title="Suggested improvements" />
              <ul className="space-y-1.5">
                {aiReport.improvements.map((i) => (
                  <li key={i} className="flex gap-2 text-sm text-ink-muted">
                    <span className="text-success">•</span>
                    {i}
                  </li>
                ))}
              </ul>
            </Card>
          </div>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Card>
              <p className="text-xs text-ink-muted">Estimated Lost Customers / Month</p>
              <p className="mt-1 font-mono text-2xl font-semibold text-danger">
                {aiReport.estimated_lost_customers_per_month}
              </p>
            </Card>
            <Card>
              <p className="text-xs text-ink-muted">Estimated Revenue Increase / Month</p>
              <p className="mt-1 font-mono text-2xl font-semibold text-success">
                ${aiReport.estimated_revenue_increase_monthly.toLocaleString()}
              </p>
            </Card>
          </div>

          <Card>
            <CardHeader title="Suggested redesign direction" />
            <div className="space-y-4">
              <div>
                <p className="mb-1.5 text-xs font-medium text-ink-muted">Style</p>
                <p className="text-sm text-ink">{aiReport.suggested_design_style}</p>
              </div>
              <div>
                <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-ink-muted">
                  <Sparkles size={12} /> Features
                </p>
                <TagList items={aiReport.suggested_features} />
              </div>
              <div>
                <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-ink-muted">
                  <Palette size={12} /> Colors
                </p>
                <TagList items={aiReport.suggested_colors} variant="color" />
              </div>
              <div>
                <p className="mb-1.5 text-xs font-medium text-ink-muted">Fonts</p>
                <TagList items={aiReport.suggested_fonts} />
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
