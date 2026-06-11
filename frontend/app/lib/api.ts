import type { DiagnosticsResponse, SearchFilters, SearchResponse, SuggestResponse } from "../types";

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

export const INITIAL_SEARCH_RESPONSE: SearchResponse = {
  query: "",
  mode: "keyword",
  total: 0,
  page: 1,
  page_size: 10,
  latency_ms: 0,
  results: [],
  facets: {
    category: [],
    author: [],
    source: [],
  },
  explain: null,
};

export async function fetchSearch(
  query: string,
  filters: SearchFilters,
  page: number,
  signal?: AbortSignal,
): Promise<SearchResponse> {
  const url = new URL(`${API_BASE_URL}/search`);
  url.searchParams.set("q", query);
  url.searchParams.set("mode", filters.mode);
  if (filters.rerank) url.searchParams.set("rerank", "true");
  url.searchParams.set("page", String(page));
  url.searchParams.set("page_size", "10");
  url.searchParams.set("sort", filters.sort);
  if (filters.category) url.searchParams.set("category", filters.category);
  if (filters.author) url.searchParams.set("author", filters.author);
  if (filters.source) url.searchParams.set("source", filters.source);
  if (filters.fromDate) url.searchParams.set("from_date", filters.fromDate);
  if (filters.toDate) url.searchParams.set("to_date", filters.toDate);

  try {
    const response = await fetch(url.toString(), { cache: "no-store", signal });
    if (!response.ok) {
      throw new Error(await readErrorMessage(response));
    }
    return response.json();
  } catch (error) {
    if (isAbortError(error)) {
      throw error;
    }
    throw error;
  }
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = await response.json();
    if (typeof payload?.detail === "string") {
      return payload.detail;
    }
  } catch {
    // Fall back to the generic HTTP status message below.
  }
  return `Search request failed with ${response.status}`;
}

export async function fetchSuggestions(query: string, signal?: AbortSignal): Promise<string[]> {
  const url = new URL(`${API_BASE_URL}/suggest`);
  url.searchParams.set("q", query);
  try {
    const response = await fetch(url.toString(), { cache: "no-store", signal });
    if (!response.ok) return [];
    const data = (await response.json()) as SuggestResponse;
    return data.suggestions.map((item) => item.text);
  } catch (error) {
    if (isAbortError(error)) {
      return [];
    }
    throw error;
  }
}

export function isAbortError(error: unknown): boolean {
  return error instanceof DOMException && error.name === "AbortError";
}

export async function fetchDiagnostics(signal?: AbortSignal): Promise<DiagnosticsResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/diagnostics`, { cache: "no-store", signal });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export function trackClick(articleId: string, query: string, position: number) {
  const payload = new Blob(
    [
      JSON.stringify({
        article_id: articleId,
        query,
        position,
      }),
    ],
    { type: "application/json" },
  );
  navigator.sendBeacon(`${API_BASE_URL}/events/click`, payload);
}
