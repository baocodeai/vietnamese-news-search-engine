import type { SearchResult } from "../types";

type ResultCardProps = {
  result: SearchResult;
  rank: number;
  onOpen: (articleId: string, position: number) => void;
};

export function ResultCard({ result, rank, onOpen }: ResultCardProps) {
  return (
    <article className="result-item">
      <div className="rank-badge" aria-label={`Kết quả số ${rank}`}>
        {String(rank).padStart(2, "0")}
      </div>
      <div className="result-body">
        <div className="result-meta">
          <span>{result.source || "Nguồn chưa rõ"}</span>
          <span>{result.category || "Chưa phân loại"}</span>
          <span>{formatDate(result.published_at)}</span>
        </div>
        <a
          href={result.url}
          target="_blank"
          rel="noreferrer"
          className="result-heading"
          onClick={() => onOpen(result.id, rank)}
        >
          {result.title}
        </a>
        <p className="result-summary">{result.summary}</p>
        <p className="result-highlight" dangerouslySetInnerHTML={renderHighlight(result)} />
        <div className="result-actions">
          <span>Kết quả phù hợp</span>
          <a href={result.url} target="_blank" rel="noreferrer" onClick={() => onOpen(result.id, rank)}>
            Mở bài viết
          </a>
        </div>
      </div>
    </article>
  );
}

function formatDate(value: string) {
  if (!value) {
    return "Không rõ ngày";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "Không rõ ngày";
  }

  return new Intl.DateTimeFormat("vi-VN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

function escapeHtml(value: string) {
  return value.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function sanitizeHighlight(value: string) {
  return escapeHtml(value)
    .replaceAll("&lt;em&gt;", "<em>")
    .replaceAll("&lt;/em&gt;", "</em>");
}

function renderHighlight(result: SearchResult) {
  const highlight =
    result.highlight?.title?.[0] ||
    result.highlight?.summary?.[0] ||
    result.highlight?.content?.[0] ||
    result.summary;

  return { __html: sanitizeHighlight(highlight) };
}
