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
          dangerouslySetInnerHTML={renderHighlightedText(result.highlight?.title?.[0] || result.title)}
        />
        <p
          className={result.highlight?.summary?.[0] ? "result-highlight" : "result-summary"}
          dangerouslySetInnerHTML={renderHighlightedText(result.highlight?.summary?.[0] || result.summary)}
        />
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

function renderHighlightedText(value: string) {
  return { __html: sanitizeHighlight(value) };
}
