"use client";

import { useEffect, useMemo, useState } from "react";

import { FilterPanel } from "./components/FilterPanel";
import { ResultList } from "./components/ResultList";
import { SearchBar } from "./components/SearchBar";
import { fetchSearch, fetchSuggestions, INITIAL_SEARCH_RESPONSE, trackClick } from "./lib/api";
import type { SearchFilters, SearchResponse } from "./types";

const QUICK_QUERIES = ["giá vàng", "nga ukraine", "địa phương điểm thi", "việt nam", "công an huế"];

const INITIAL_FILTERS: SearchFilters = {
  mode: "keyword",
  category: "",
  author: "",
  source: "",
  fromDate: "",
  toDate: "",
  sort: "relevance",
};

export default function HomePage() {
  const [query, setQuery] = useState("");
  const [submittedQuery, setSubmittedQuery] = useState("");
  const [filters, setFilters] = useState<SearchFilters>(INITIAL_FILTERS);
  const [page, setPage] = useState(1);
  const [response, setResponse] = useState<SearchResponse>(INITIAL_SEARCH_RESPONSE);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const totalPages = useMemo(
    () => Math.max(1, Math.ceil(response.total / response.page_size)),
    [response.total, response.page_size],
  );

  useEffect(() => {
    const trimmed = query.trim();
    const controller = new AbortController();
    const timeout = setTimeout(async () => {
      if (trimmed.length < 2) {
        setSuggestions([]);
        return;
      }
      setSuggestions(await fetchSuggestions(trimmed, controller.signal));
    }, 260);

    return () => {
      controller.abort();
      clearTimeout(timeout);
    };
  }, [query]);

  useEffect(() => {
    void runSearch(page, submittedQuery, filters);
  }, [page, filters, submittedQuery]);

  async function runSearch(nextPage: number, nextQuery: string, nextFilters: SearchFilters) {
    setLoading(true);
    setError("");
    try {
      const data = await fetchSearch(nextQuery, nextFilters, nextPage);
      setResponse(data);
    } catch (err) {
      setResponse(INITIAL_SEARCH_RESPONSE);
      setError(err instanceof Error ? err.message : "Không thể kết nối dịch vụ tìm kiếm.");
    } finally {
      setLoading(false);
    }
  }

  function submitSearch(nextQuery: string) {
    const trimmed = nextQuery.trim();
    setQuery(trimmed);
    setSubmittedQuery(trimmed);
    setPage(1);
  }

  function updateFilters(nextFilters: SearchFilters) {
    setFilters(nextFilters);
    setPage(1);
  }

  function resetFilters() {
    setFilters(INITIAL_FILTERS);
    setPage(1);
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div className="brand-lockup">
          <div className="brand-mark" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div>
            <span className="micro-label">Vietnamese News Search</span>
            <h1>Tìm kiếm báo tiếng Việt</h1>
            <p>Tra cứu nhanh tin tức theo từ khóa, nguồn báo và chuyên mục.</p>
          </div>
        </div>
      </header>

      <section className="search-layout">
        <FilterPanel filters={filters} response={response} onChange={updateFilters} onReset={resetFilters} />
        <div className="center-column">
          <SearchBar
            query={query}
            mode={filters.mode}
            suggestions={suggestions}
            quickQueries={QUICK_QUERIES}
            loading={loading}
            onQueryChange={setQuery}
            onModeChange={(mode) => updateFilters({ ...filters, mode })}
            onSubmit={submitSearch}
          />
          <ResultList
            response={response}
            submittedQuery={submittedQuery}
            loading={loading}
            error={error}
            page={page}
            totalPages={totalPages}
            onPageChange={setPage}
            onOpen={(articleId, position) => trackClick(articleId, submittedQuery, position)}
          />
        </div>
      </section>
    </main>
  );
}
