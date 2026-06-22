"use client";

import { AlertTriangle, Check, Copy, Loader2, MessageCircle, RotateCw } from "lucide-react";
import { useEffect, useState } from "react";

import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ApiError, apiFetch } from "@/lib/api";
import { cn } from "@/lib/utils";

type Tone = "professional" | "friendly" | "luxury";
type Length = "short" | "long";
type Language = "en" | "hi";

type Lead = {
  id: string;
  business_name: string;
  website_url: string | null;
};

type WhatsAppMessage = {
  id: string;
  tone: Tone;
  length: Length;
  language: Language;
  content: string;
  created_at: string;
};

function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
}: {
  options: { value: T; label: string }[];
  value: T;
  onChange: (v: T) => void;
}) {
  return (
    <div className="inline-flex rounded-md border border-base-border bg-base-raised p-0.5">
      {options.map((opt) => (
        <button
          key={opt.value}
          type="button"
          onClick={() => onChange(opt.value)}
          className={cn(
            "rounded-[5px] px-3 py-1 text-xs font-medium transition-colors",
            value === opt.value ? "bg-accent text-white" : "text-ink-muted hover:text-ink"
          )}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}

export default function WhatsAppGeneratorPage() {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [leadsError, setLeadsError] = useState<string | null>(null);
  const [selectedLeadId, setSelectedLeadId] = useState<string>("");

  const [tone, setTone] = useState<Tone>("professional");
  const [length, setLength] = useState<Length>("short");
  const [language, setLanguage] = useState<Language>("en");

  const [isGenerating, setIsGenerating] = useState(false);
  const [message, setMessage] = useState<WhatsAppMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const [history, setHistory] = useState<WhatsAppMessage[]>([]);

  useEffect(() => {
    apiFetch<{ leads: Lead[] }>("/leads")
      .then((data) => setLeads(data.leads))
      .catch((err) => setLeadsError(err instanceof ApiError ? err.message : "Could not load leads."));
  }, []);

  useEffect(() => {
    if (!selectedLeadId) {
      setHistory([]);
      setMessage(null);
      return;
    }
    apiFetch<{ messages: WhatsAppMessage[] }>(`/whatsapp/${selectedLeadId}/history`)
      .then((data) => setHistory(data.messages))
      .catch(() => setHistory([]));
  }, [selectedLeadId]);

  async function handleGenerate() {
    if (!selectedLeadId) return;
    setIsGenerating(true);
    setError(null);
    setCopied(false);

    try {
      const data = await apiFetch<WhatsAppMessage>(`/whatsapp/${selectedLeadId}/generate`, {
        method: "POST",
        body: JSON.stringify({ tone, length, language }),
      });
      setMessage(data);
      setHistory((prev) => [data, ...prev]);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Message generation failed. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  }

  async function handleCopy() {
    if (!message) return;
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Could not copy to clipboard. Try selecting and copying the text manually.");
    }
  }

  const selectedLead = leads.find((l) => l.id === selectedLeadId);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">WhatsApp Generator</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Generate a personalized outreach message — copy it manually. This app never sends messages for you.
        </p>
      </div>

      <Card>
        <div className="mb-4">
          <label htmlFor="lead-select" className="mb-1.5 block text-xs font-medium text-ink-muted">
            Lead
          </label>
          <select
            id="lead-select"
            value={selectedLeadId}
            onChange={(e) => {
              setSelectedLeadId(e.target.value);
              setMessage(null);
              setError(null);
            }}
            disabled={leads.length === 0}
            className="w-full max-w-md rounded-md border border-base-border bg-base-raised px-3 py-2 text-sm text-ink focus-visible:border-accent disabled:opacity-50"
          >
            <option value="">{leads.length === 0 ? "No leads saved yet" : "Select a lead…"}</option>
            {leads.map((lead) => (
              <option key={lead.id} value={lead.id}>
                {lead.business_name}
              </option>
            ))}
          </select>
        </div>

        <div className="flex flex-wrap items-center gap-6">
          <div>
            <p className="mb-1.5 text-xs font-medium text-ink-muted">Tone</p>
            <SegmentedControl
              value={tone}
              onChange={setTone}
              options={[
                { value: "professional", label: "Professional" },
                { value: "friendly", label: "Friendly" },
                { value: "luxury", label: "Luxury" },
              ]}
            />
          </div>
          <div>
            <p className="mb-1.5 text-xs font-medium text-ink-muted">Length</p>
            <SegmentedControl
              value={length}
              onChange={setLength}
              options={[
                { value: "short", label: "Short" },
                { value: "long", label: "Long" },
              ]}
            />
          </div>
          <div>
            <p className="mb-1.5 text-xs font-medium text-ink-muted">Language</p>
            <SegmentedControl
              value={language}
              onChange={setLanguage}
              options={[
                { value: "en", label: "English" },
                { value: "hi", label: "Hindi" },
              ]}
            />
          </div>

          <button
            type="button"
            onClick={handleGenerate}
            disabled={!selectedLeadId || isGenerating}
            className="ml-auto inline-flex items-center gap-1.5 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isGenerating ? <Loader2 size={14} className="animate-spin" /> : <MessageCircle size={14} />}
            {isGenerating ? "Generating…" : message ? "Regenerate" : "Generate"}
          </button>
        </div>
        {leadsError && <p className="mt-3 text-xs text-danger">{leadsError}</p>}
      </Card>

      {error && (
        <div className="flex items-start gap-2 rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
          <AlertTriangle size={15} className="mt-0.5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {!selectedLeadId && leads.length === 0 && !leadsError && (
        <EmptyState
          icon={MessageCircle}
          title="No leads saved yet"
          description="Save a lead from Lead Finder, then come back here to generate a personalized outreach message."
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

      {!message && selectedLeadId && !error && (
        <EmptyState
          icon={MessageCircle}
          title="No message generated yet"
          description={`Click Generate to create a ${tone} message for ${selectedLead?.business_name ?? "this lead"}.`}
        />
      )}

      {message && selectedLead && (
        <Card>
          <div className="mb-3 flex items-center justify-between">
            <h3 className="text-sm font-semibold text-ink">Preview — {selectedLead.business_name}</h3>
            <div className="flex gap-2">
              <button
                onClick={handleGenerate}
                disabled={isGenerating}
                className="inline-flex items-center gap-1.5 rounded-md border border-base-border-strong px-2.5 py-1 text-xs text-ink-muted hover:bg-base-raised hover:text-ink disabled:opacity-60"
              >
                <RotateCw size={12} className={isGenerating ? "animate-spin" : ""} /> Regenerate
              </button>
              <button
                onClick={handleCopy}
                className="inline-flex items-center gap-1.5 rounded-md border border-base-border-strong px-2.5 py-1 text-xs text-ink-muted hover:bg-base-raised hover:text-ink"
              >
                {copied ? <Check size={12} className="text-success" /> : <Copy size={12} />}
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
          </div>
          <p className="whitespace-pre-wrap text-sm text-ink">{message.content}</p>
          <div className="mt-3 flex gap-2 text-xs text-ink-subtle">
            <span className="capitalize">{message.tone}</span>
            <span>·</span>
            <span className="capitalize">{message.length}</span>
            <span>·</span>
            <span>{message.language === "hi" ? "Hindi" : "English"}</span>
          </div>
        </Card>
      )}

      {history.length > 1 && (
        <Card>
          <h3 className="mb-3 text-sm font-semibold text-ink">History</h3>
          <div className="space-y-2">
            {history.slice(1).map((h) => (
              <button
                key={h.id}
                onClick={() => setMessage(h)}
                className="block w-full rounded-md border border-base-border bg-base-raised px-3 py-2 text-left text-xs text-ink-muted hover:border-base-border-strong hover:text-ink"
              >
                <p className="truncate">{h.content}</p>
                <p className="mt-1 text-ink-subtle">
                  {h.tone} · {h.length} · {h.language === "hi" ? "Hindi" : "English"} ·{" "}
                  {new Date(h.created_at).toLocaleString()}
                </p>
              </button>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
