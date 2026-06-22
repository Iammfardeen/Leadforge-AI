"use client";

import { Check, Loader2, Search } from "lucide-react";
import { useState } from "react";

import { Card } from "@/components/ui/card";
import { EmptyState } from "@/components/ui/empty-state";
import { ApiError, apiFetch } from "@/lib/api";

const CATEGORIES = [
  "Restaurants", "Salons", "Lawyers", "Doctors", "Dentists", "Gyms", "Hotels",
  "Schools", "Real Estate", "Car Dealers", "Auto Repair", "Electronics",
  "Clothing", "Builders", "Cafes",
];

type SearchResult = {
  business_name: string;
  owner_name: string | null;
  phone: string | null;
  email: string | null;
  website_url: string | null;
  google_rating: number | null;
  review_count: number | null;
  address: string | null;
  city: string | null;
  category: string | null;
  business_age_years: number | null;
  has_website: boolean;
  instagram_url: string | null;
  facebook_url: string | null;
  google_place_id: string | null;
};

type SaveState = "idle" | "saving" | "saved" | "error";

export default function LeadFinderPage() {
  const [city, setCity] = useState("");
  const [category, setCategory] = useState(CATEGORIES[0]);
  const [isSearching, setIsSearching] = useState(false);
  const [results, setResults] = useState<SearchResult[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saveStates, setSaveStates] = useState<Record<string, SaveState>>({});

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setIsSearching(true);
    setError(null);

    try {
      const data = await apiFetch<{ results: SearchResult[] }>("/leads/search", {
        method: "POST",
        body: JSON.stringify({ city, category, max_results: 20 }),
      });
      setResults(data.results);
      setSaveStates({});
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Search failed. Please try again.");
    } finally {
      setIsSearching(false);
    }
  }

  async function handleSave(result: SearchResult) {
    const key = result.google_place_id ?? result.business_name;
    setSaveStates((prev) => ({ ...prev, [key]: "saving" }));

    try {
      await apiFetch("/leads", {
        method: "POST",
        body: JSON.stringify(result),
      });
      setSaveStates((prev) => ({ ...prev, [key]: "saved" }));
    } catch {
      setSaveStates((prev) => ({ ...prev, [key]: "error" }));
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-semibold text-ink">Lead Finder</h1>
        <p className="mt-1 text-sm text-ink-muted">
          Search businesses by city and category using Google Places.
        </p>
      </div>

      <Card>
        <form onSubmit={handleSearch} className="flex flex-wrap items-end gap-3">
          <div className="min-w-[200px] flex-1">
            <label htmlFor="city" className="mb-1.5 block text-xs font-medium text-ink-muted">
              City
            </label>
            <input
              id="city"
              required
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="e.g. Haridwar"
              className="w-full rounded-md border border-base-border bg-base-raised px-3 py-2 text-sm text-ink placeholder:text-ink-subtle focus-visible:border-accent"
            />
          </div>

          <div className="min-w-[180px]">
            <label htmlFor="category" className="mb-1.5 block text-xs font-medium text-ink-muted">
              Category
            </label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full rounded-md border border-base-border bg-base-raised px-3 py-2 text-sm text-ink focus-visible:border-accent"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={isSearching}
            className="inline-flex items-center gap-1.5 rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:bg-accent-hover disabled:opacity-60"
          >
            {isSearching ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
            Search
          </button>
        </form>
      </Card>

      {error && (
        <p role="alert" className="rounded-md border border-danger/30 bg-danger/10 px-3 py-2 text-sm text-danger">
          {error}
        </p>
      )}

      {results === null && !error && (
        <EmptyState
          icon={Search}
          title="No search yet"
          description="Enter a city and category above to find businesses that might need a new website."
        />
      )}

      {results !== null && results.length === 0 && (
        <EmptyState
          icon={Search}
          title="No results"
          description="Try a different city or category."
        />
      )}

      {results !== null && results.length > 0 && (
        <Card className="overflow-x-auto p-0">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-base-border text-left text-xs text-ink-muted">
                <th className="px-4 py-3 font-medium">Business</th>
                <th className="px-4 py-3 font-medium">Phone</th>
                <th className="px-4 py-3 font-medium">Website</th>
                <th className="px-4 py-3 font-medium">Rating</th>
                <th className="px-4 py-3 font-medium">Address</th>
                <th className="px-4 py-3 font-medium"></th>
              </tr>
            </thead>
            <tbody>
              {results.map((r) => {
                const key = r.google_place_id ?? r.business_name;
                const state = saveStates[key] ?? "idle";
                return (
                  <tr key={key} className="border-b border-base-border last:border-0">
                    <td className="px-4 py-3 font-medium text-ink">{r.business_name}</td>
                    <td className="px-4 py-3 text-ink-muted">{r.phone ?? "—"}</td>
                    <td className="px-4 py-3 text-ink-muted">
                      {r.has_website ? (
                        <span className="text-success">Yes</span>
                      ) : (
                        <span className="text-danger">No website</span>
                      )}
                    </td>
                    <td className="px-4 py-3 font-mono text-ink-muted">
                      {r.google_rating ? `${r.google_rating} (${r.review_count})` : "—"}
                    </td>
                    <td className="max-w-xs truncate px-4 py-3 text-ink-muted">{r.address ?? "—"}</td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleSave(r)}
                        disabled={state === "saving" || state === "saved"}
                        className="inline-flex items-center gap-1 rounded-md border border-base-border-strong px-2.5 py-1 text-xs text-ink-muted hover:bg-base-raised hover:text-ink disabled:cursor-not-allowed"
                      >
                        {state === "saving" && <Loader2 size={12} className="animate-spin" />}
                        {state === "saved" && <Check size={12} className="text-success" />}
                        {state === "saving"
                          ? "Saving…"
                          : state === "saved"
                            ? "Saved"
                            : state === "error"
                              ? "Retry"
                              : "Save lead"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </Card>
      )}
    </div>
  );
}
