import type { SearchMode } from "../types";

type SearchBarProps = {
  query: string;
  mode: SearchMode;
  suggestions: string[];
  quickQueries: string[];
  loading: boolean;
  onQueryChange: (value: string) => void;
  onModeChange: (mode: SearchMode) => void;
  onSubmit: (value: string) => void;
};

export function SearchBar({
  query,
  mode,
  suggestions,
  quickQueries,
  loading,
  onQueryChange,
  onModeChange,
  onSubmit,
}: SearchBarProps) {
  return (
    <section className="search-command" aria-label="Tìm kiếm tin tức">
      <div className="mode-switch" aria-label="Search mode">
        <ModeButton value="keyword" current={mode} onChange={onModeChange}>
          Keyword
        </ModeButton>
        <ModeButton value="semantic" current={mode} onChange={onModeChange}>
          Semantic
        </ModeButton>
        <ModeButton value="hybrid" current={mode} onChange={onModeChange}>
          Hybrid
        </ModeButton>
      </div>

      <form
        className="command-form"
        onSubmit={(event) => {
          event.preventDefault();
          onSubmit(query);
        }}
      >
        <label className="query-field">
          <span>Truy vấn</span>
          <input
            value={query}
            onChange={(event) => onQueryChange(event.target.value)}
            placeholder="Tìm theo sự kiện, nhân vật, địa điểm..."
            autoComplete="off"
          />
        </label>
        <button className="primary-action" type="submit">
          {loading ? "Đang tìm" : "Tìm kiếm"}
        </button>
      </form>

      <div className="query-assists">
        <AssistGroup label="Tìm nhanh" items={quickQueries} onSubmit={onSubmit} />
        {suggestions.length > 0 ? (
          <AssistGroup label="Gợi ý" items={suggestions.slice(0, 6)} muted onSubmit={onSubmit} />
        ) : null}
      </div>
    </section>
  );
}

function ModeButton({
  value,
  current,
  children,
  onChange,
}: {
  value: SearchMode;
  current: SearchMode;
  children: string;
  onChange: (mode: SearchMode) => void;
}) {
  return (
    <button
      type="button"
      className={current === value ? "mode-option active" : "mode-option"}
      aria-pressed={current === value}
      onClick={() => onChange(value)}
    >
      {children}
    </button>
  );
}

function AssistGroup({
  label,
  items,
  muted = false,
  onSubmit,
}: {
  label: string;
  items: string[];
  muted?: boolean;
  onSubmit: (value: string) => void;
}) {
  return (
    <div className="assist-group">
      <span className="micro-label">{label}</span>
      <div className="chip-row">
        {items.map((item) => (
          <button type="button" className={muted ? "query-chip muted" : "query-chip"} key={item} onClick={() => onSubmit(item)}>
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}
