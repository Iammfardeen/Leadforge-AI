"use client";

import { useState } from "react";

import { Card, CardHeader } from "@/components/ui/card";
import { cn } from "@/lib/utils";

function Field({
  label,
  hint,
  children,
}: {
  label: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <div>
      <label className="mb-1.5 block text-xs font-medium text-ink-muted">{label}</label>
      {children}
      {hint && <p className="mt-1 text-xs text-ink-subtle">{hint}</p>}
    </div>
  );
}

function TextInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className="w-full rounded-md border border-base-border bg-base-raised px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus-visible:border-accent"
    />
  );
}

export default function SettingsPage() {
  const [theme, setTheme] = useState<"dark" | "light">("dark");

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Settings</h1>
        <p className="mt-1 text-sm text-ink-muted">Manage your account, AI model, and integration keys.</p>
      </div>

      <Card>
        <CardHeader title="Appearance" description="Choose how LeadForge AI looks on your device." />
        <div className="inline-flex rounded-md border border-base-border bg-base-raised p-0.5">
          {(["dark", "light"] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTheme(t)}
              className={cn(
                "rounded-[5px] px-4 py-1.5 text-xs font-medium capitalize transition-colors",
                theme === t ? "bg-accent text-white" : "text-ink-muted hover:text-ink"
              )}
            >
              {t}
            </button>
          ))}
        </div>
        {theme === "light" && (
          <p className="mt-2 text-xs text-ink-subtle">
            Light theme is on the roadmap — the app currently renders dark mode only.
          </p>
        )}
      </Card>

      <Card>
        <CardHeader title="Branding" description="Shown on proposals and exported reports." />
        <div className="space-y-4">
          <Field label="Business name">
            <TextInput placeholder="Your studio or freelance name" />
          </Field>
          <Field label="Brand logo URL" hint="Paste a hosted image URL, or upload support arrives later.">
            <TextInput placeholder="https://…" />
          </Field>
        </div>
      </Card>

      <Card>
        <CardHeader title="AI model" description="Choose which Groq-hosted model generates your AI content." />
        <select className="w-full rounded-md border border-base-border bg-base-raised px-3 py-2 text-sm text-ink focus-visible:border-accent">
          <option value="llama-3.3-70b-versatile">Llama 3.3 70B (default, best quality)</option>
          <option value="llama-3.1-8b-instant">Llama 3.1 8B (faster, higher free-tier limits)</option>
        </select>
      </Card>

      <Card>
        <CardHeader
          title="API keys"
          description="Your own keys, stored encrypted. Required for Lead Finder to return real results."
        />
        <div className="space-y-4">
          <Field
            label="Google Places API key"
            hint="Free tier available. Get one at developers.google.com/maps/documentation/places/web-service/get-api-key"
          >
            <TextInput type="password" placeholder="AIza…" />
          </Field>
          <Field
            label="Google PageSpeed Insights API key"
            hint="Optional — the Website Analyzer works without one for light use. Adding a key raises the free rate limit."
          >
            <TextInput type="password" placeholder="AIza… (optional)" />
          </Field>
        </div>
      </Card>

      <Card>
        <CardHeader title="SMTP" description="Optional — used if you enable emailed proposals later." />
        <div className="grid grid-cols-2 gap-4">
          <Field label="Host">
            <TextInput placeholder="smtp.example.com" />
          </Field>
          <Field label="Port">
            <TextInput type="number" placeholder="587" />
          </Field>
          <Field label="Username">
            <TextInput placeholder="you@example.com" />
          </Field>
          <Field label="Password">
            <TextInput type="password" placeholder="••••••••" />
          </Field>
        </div>
      </Card>

      <div className="flex justify-end">
        <button className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover">
          Save changes
        </button>
      </div>
    </div>
  );
}
