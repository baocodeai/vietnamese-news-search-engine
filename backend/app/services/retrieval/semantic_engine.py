from pathlib import Path
from typing import Any, Callable

from backend.app.services.preprocessing.text_normalizer import clean_display_text
from backend.app.services.retrieval.base import SearchDocument, SearchResult


class SemanticSearchEngine:
    """
    Semantic search engine dung embedding E5 va FAISS artifacts.

    Engine nay khong build embedding tu SearchDocument luc runtime. No load lai
    cac artifact da tao tu notebook/script: FAISS index, metadata parquet va
    embedding_config.json.
    """

    def __init__(
        self,
        index_path: str | Path | None = None,
        metadata_path: str | Path | None = None,
        config_path: str | Path | None = None,
        *,
        candidate_multiplier: int = 5,
        min_candidates: int = 50,
        index: Any | None = None,
        metadata: Any | None = None,
        config: dict[str, Any] | None = None,
        query_encoder: Callable[[list[str]], Any] | None = None,
    ):
        self.candidate_multiplier = candidate_multiplier
        self.min_candidates = min_candidates

        self.index = index
        self.metadata: list[dict[str, Any]] = self._coerce_metadata(metadata)
        self.config = config or {}
        self.query_encoder = query_encoder
        self.documents: list[SearchDocument] = []

        self._assert_artifact_paths(index_path, metadata_path, config_path)

        if self.index is None and index_path is not None:
            self.index = self._load_faiss_index(index_path)
        if not self.metadata and metadata_path is not None:
            self.metadata = self._load_metadata(metadata_path)
        if not self.config and config_path is not None:
            self.config = self._load_config(config_path)

        if self.query_encoder is None and self.config:
            self.query_encoder = self._create_e5_query_encoder()

        # Do not materialize every semantic metadata row as SearchDocument here.
        # The semantic corpus can be large, and duplicating metadata as Python
        # objects adds a large RAM spike before any query is served.

    @classmethod
    def from_artifacts(
        cls,
        index_path: str | Path,
        metadata_path: str | Path,
        config_path: str | Path,
        *,
        candidate_multiplier: int = 5,
        min_candidates: int = 50,
    ) -> "SemanticSearchEngine":
        return cls(
            index_path=index_path,
            metadata_path=metadata_path,
            config_path=config_path,
            candidate_multiplier=candidate_multiplier,
            min_candidates=min_candidates,
        )

    def build(self, documents: list[SearchDocument]) -> None:
        """
        Giu interface chung voi SearchEngine.

        Semantic index duoc build offline bang embedding pipeline, nen runtime
        khong rebuild tu documents.
        """
        self.documents = documents

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        if top_k <= 0:
            return []
        query = query.strip()
        if not query or self.index is None or not self.metadata:
            return []
        if self.query_encoder is None:
            raise RuntimeError("Semantic query encoder is not initialized.")

        candidate_k = min(
            max(top_k * self.candidate_multiplier, self.min_candidates),
            int(getattr(self.index, "ntotal", len(self.metadata))),
        )
        if candidate_k <= 0:
            return []

        query_prefix = self.config.get("query_prefix", "query: ")
        query_embedding = self.query_encoder([query_prefix + query])
        scores, ids = self.index.search(query_embedding, candidate_k)

        results: list[SearchResult] = []
        seen_chunks: set[str] = set()

        for score, row_index in zip(scores[0], ids[0]):
            if int(row_index) == -1:
                continue
            row = self.metadata[int(row_index)]
            chunk_key = str(row.get("chunk_id") or row.get("embedding_index") or row_index)
            if chunk_key in seen_chunks:
                continue
            seen_chunks.add(chunk_key)

            results.append(self._row_to_result(row, float(score)))
            if len(results) >= top_k:
                break

        return results

    def _row_to_result(self, row: dict[str, Any], score: float) -> SearchResult:
        doc_id = row.get("doc_id", row.get("id", ""))
        chunk_id = row.get("chunk_id")
        text = clean_display_text(row.get("text") or row.get("raw_text") or "")
        title = clean_display_text(row.get("title") or text, max_chars=120)

        metadata = {
            key: value
            for key, value in row.items()
            if key
            not in {
                "doc_id",
                "chunk_id",
                "title",
                "text",
                "raw_text",
                "url",
                "source",
                "topic",
                "author",
                "crawled_at",
            }
        }

        return SearchResult(
            doc_id=doc_id,
            chunk_id=chunk_id,
            score=score,
            title=title,
            snippet=clean_display_text(text, max_chars=300),
            url=str(row.get("url") or ""),
            source=clean_display_text(row.get("source") or ""),
            topic=clean_display_text(row.get("topic") or ""),
            author=clean_display_text(row.get("author") or ""),
            crawled_at=row.get("crawled_at"),
            metadata=metadata,
        )

    def _metadata_to_documents(self, metadata: list[dict[str, Any]]) -> list[SearchDocument]:
        documents = []
        for row in metadata:
            result = self._row_to_result(row, score=0.0)
            documents.append(
                SearchDocument(
                    id=result.chunk_id or result.doc_id,
                    title=result.title,
                    content=result.snippet,
                    url=result.url,
                    source=result.source,
                    topic=result.topic,
                    author=result.author,
                    crawled_at=result.crawled_at,
                    metadata={
                        **result.metadata,
                        "doc_id": result.doc_id,
                        "chunk_id": result.chunk_id,
                    },
                )
            )
        return documents

    def _coerce_metadata(self, metadata: Any | None) -> list[dict[str, Any]]:
        if metadata is None:
            return []
        if isinstance(metadata, list):
            return metadata
        if hasattr(metadata, "to_dict"):
            return metadata.to_dict("records")
        return list(metadata)

    def _assert_artifact_paths(
        self,
        index_path: str | Path | None,
        metadata_path: str | Path | None,
        config_path: str | Path | None,
    ) -> None:
        paths = {
            "semantic index": index_path,
            "semantic metadata": metadata_path,
            "semantic config": config_path,
        }
        missing = [
            f"{name}: {path}"
            for name, path in paths.items()
            if path is not None and not Path(path).exists()
        ]
        if missing:
            raise FileNotFoundError("Missing artifacts: " + "; ".join(missing))

    def _load_metadata(self, metadata_path: str | Path) -> list[dict[str, Any]]:
        try:
            import pandas as pd
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency 'pandas'. Install pandas and pyarrow "
                "to load semantic metadata parquet."
            ) from exc

        return pd.read_parquet(metadata_path).to_dict("records")

    def _load_faiss_index(self, index_path: str | Path) -> Any:
        try:
            import faiss
        except ImportError as exc:
            raise RuntimeError(
                "Missing dependency 'faiss'. Install faiss-cpu or faiss-gpu "
                "to use semantic search."
            ) from exc

        return faiss.read_index(str(index_path))

    def _load_config(self, config_path: str | Path) -> dict[str, Any]:
        import json

        with Path(config_path).open("r", encoding="utf-8") as file:
            return json.load(file)

    def _create_e5_query_encoder(self) -> Callable[[list[str]], Any]:
        try:
            import numpy as np
            import torch
            import torch.nn.functional as F
            from transformers import AutoModel, AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Missing semantic dependencies. Install torch, transformers "
                "and numpy to encode semantic queries."
            ) from exc

        model_name = self.config["model_name"]
        max_length = int(self.config.get("max_length", 512))
        device = "cuda" if torch.cuda.is_available() else "cpu"
        dtype = torch.float16 if device == "cuda" else torch.float32

        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModel.from_pretrained(model_name, torch_dtype=dtype).to(device)
        model.eval()

        def mean_pooling(last_hidden_state, attention_mask):
            mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
            summed = torch.sum(last_hidden_state.float() * mask, dim=1)
            counts = torch.clamp(mask.sum(dim=1), min=1e-9)
            return summed / counts

        @torch.no_grad()
        def encode(texts: list[str]):
            inputs = tokenizer(
                texts,
                max_length=max_length,
                padding=True,
                truncation=True,
                return_tensors="pt",
            )
            inputs = {key: value.to(device) for key, value in inputs.items()}

            with torch.amp.autocast("cuda", enabled=(device == "cuda")):
                outputs = model(**inputs)

            embeddings = mean_pooling(outputs.last_hidden_state, inputs["attention_mask"])
            embeddings = F.normalize(embeddings, p=2, dim=1)
            return embeddings.cpu().numpy().astype(np.float32)

        return encode
