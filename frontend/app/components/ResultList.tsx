import type { SearchResponse } from "../types";
import { ResultCard } from "./ResultCard";

type ResultListProps = {
  response: SearchResponse;
  submittedQuery: string;
  loading: boolean;
  error: string;
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  onOpen: (articleId: string, position: number) => void;
};

export function ResultList({
  response,
  submittedQuery,
  loading,
  error,
  page,
  totalPages,
  onPageChange,
  onOpen,
}: ResultListProps) {
  return (
    <section className="results-workspace" aria-busy={loading}>
      <div className="section-head">
        <div>
          <span className="micro-label">Kết quả</span>
          <h2>{submittedQuery ? submittedQuery : "Nhập truy vấn để bắt đầu"}</h2>
        </div>
        <span className="status-pill">
          Trang {response.page}/{totalPages}
        </span>
      </div>

      <div className="result-summary-bar">
        <strong>{response.total.toLocaleString("vi-VN")}</strong>
        <span>kết quả phù hợp</span>
      </div>

      {loading ? (
        <StatusCard title="Đang tìm kiếm" description="Hệ thống đang lọc và sắp xếp các bài viết phù hợp." />
      ) : null}
      {!loading && error ? <StatusCard title="Không kết nối được dịch vụ" description={error} /> : null}
      {!loading && !error && response.results.length === 0 ? (
        <StatusCard title="Không có kết quả phù hợp" description="Thử đổi truy vấn, bỏ bớt bộ lọc hoặc dùng từ khóa không dấu." />
      ) : null}

      <div className="result-list">
        {response.results.map((result, index) => (
          <ResultCard
            key={result.id}
            result={result}
            rank={(page - 1) * response.page_size + index + 1}
            onOpen={onOpen}
          />
        ))}
      </div>

      <div className="pager">
        <button type="button" onClick={() => onPageChange(Math.max(1, page - 1))} disabled={page <= 1}>
          Trang trước
        </button>
        <button type="button" onClick={() => onPageChange(Math.min(totalPages, page + 1))} disabled={page >= totalPages}>
          Trang sau
        </button>
      </div>
    </section>
  );
}

function StatusCard({ title, description }: { title: string; description: string }) {
  return (
    <div className="status-card">
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}
