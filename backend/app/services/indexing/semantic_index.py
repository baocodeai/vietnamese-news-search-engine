import json
from pathlib import Path
from typing import Any

from backend.app.services.indexing.document_loader import iter_json_records
from backend.app.services.preprocessing.text_normalizer import fix_mojibake


DEFAULT_MODEL_NAME = "intfloat/multilingual-e5-base"
DEFAULT_TEXT_COL = "raw_text"


def build_semantic_index(
    data_path: str | Path,
    output_dir: str | Path,
    *,
    model_name: str = DEFAULT_MODEL_NAME,
    text_col: str = DEFAULT_TEXT_COL,
    batch_size: int = 16,
    max_length: int = 512,
    shard_size: int = 10_000,
    limit: int | None = None,
    encoder: Any | None = None,
) -> dict[str, Any]:
    """
    Build full semantic artifacts tu corpus chunks.

    Output gom:
    - embeddings_part_*.npy
    - metadata_part_*.parquet
    - semantic_e5_base.faiss
    - chunks_metadata.parquet
    - embedding_config.json
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if encoder is None:
        from backend.app.services.embedding.e5_encoder import E5TextEncoder

        encoder = E5TextEncoder(model_name=model_name, max_length=max_length)

    _build_embedding_shards(
        data_path=data_path,
        output_dir=output_dir,
        encoder=encoder,
        text_col=text_col,
        batch_size=batch_size,
        shard_size=shard_size,
        limit=limit,
    )
    index, metadata = build_faiss_index_from_shards(output_dir)

    index_path = output_dir / "semantic_e5_base.faiss"
    metadata_path = output_dir / "chunks_metadata.parquet"
    config_path = output_dir / "embedding_config.json"

    _write_faiss_index(index, index_path)
    _write_metadata(metadata, metadata_path)

    config = {
        "model_name": model_name,
        "text_column": text_col,
        "document_prefix": "passage: ",
        "query_prefix": "query: ",
        "max_length": max_length,
        "normalize_embeddings": True,
        "faiss_metric": "inner_product",
        "embedding_dim": int(index.d),
        "num_vectors": int(index.ntotal),
    }
    config_path.write_text(
        json.dumps(config, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return {
        "index_path": index_path,
        "metadata_path": metadata_path,
        "config_path": config_path,
        "num_vectors": int(index.ntotal),
        "embedding_dim": int(index.d),
    }


def build_faiss_index_from_shards(output_dir: str | Path):
    import numpy as np
    import pandas as pd

    faiss = _import_faiss()
    output_dir = Path(output_dir)
    embedding_files = sorted(output_dir.glob("embeddings_part_*.npy"))
    metadata_files = sorted(output_dir.glob("metadata_part_*.parquet"))

    if not embedding_files:
        raise FileNotFoundError(f"No embedding shards found in {output_dir}")
    if len(embedding_files) != len(metadata_files):
        raise ValueError(
            "Embedding shard count does not match metadata shard count: "
            f"{len(embedding_files)} != {len(metadata_files)}"
        )

    index = None
    all_metadata = []
    offset = 0

    for emb_file, meta_file in zip(embedding_files, metadata_files):
        embeddings = np.load(emb_file).astype("float32")
        metadata = pd.read_parquet(meta_file)

        if index is None:
            index = faiss.IndexFlatIP(embeddings.shape[1])

        metadata.insert(
            0,
            "embedding_index",
            np.arange(offset, offset + len(metadata)),
        )
        index.add(embeddings)
        all_metadata.append(metadata)
        offset += len(metadata)

    return index, pd.concat(all_metadata, ignore_index=True)


def _build_embedding_shards(
    *,
    data_path: str | Path,
    output_dir: Path,
    encoder: Any,
    text_col: str,
    batch_size: int,
    shard_size: int,
    limit: int | None,
) -> None:
    import numpy as np

    batch_texts: list[str] = []
    batch_meta: list[dict[str, Any]] = []
    shard_embeddings = []
    shard_metadata: list[dict[str, Any]] = []

    shard_id = 0
    total_records = 0
    total_embedded = 0

    for item in iter_json_records(data_path, limit=limit):
        total_records += 1
        text = fix_mojibake(item.get(text_col, "")).strip()
        if not text:
            continue

        batch_texts.append("passage: " + text)
        batch_meta.append(_metadata_from_record(item, text=text))

        if len(batch_texts) >= batch_size:
            embeddings = encoder.encode(batch_texts, batch_size=batch_size)
            shard_embeddings.append(embeddings)
            shard_metadata.extend(batch_meta)
            total_embedded += len(batch_texts)
            batch_texts = []
            batch_meta = []

            if len(shard_metadata) >= shard_size:
                shard_id = _flush_shard(
                    output_dir=output_dir,
                    shard_id=shard_id,
                    embeddings=np.vstack(shard_embeddings),
                    metadata_rows=shard_metadata,
                )
                shard_embeddings = []
                shard_metadata = []

    if batch_texts:
        embeddings = encoder.encode(batch_texts, batch_size=batch_size)
        shard_embeddings.append(embeddings)
        shard_metadata.extend(batch_meta)
        total_embedded += len(batch_texts)

    if shard_metadata:
        _flush_shard(
            output_dir=output_dir,
            shard_id=shard_id,
            embeddings=np.vstack(shard_embeddings),
            metadata_rows=shard_metadata,
        )

    print("total_records:", total_records)
    print("total_embedded:", total_embedded)


def _metadata_from_record(item: dict[str, Any], text: str) -> dict[str, Any]:
    return {
        "doc_id": item.get("doc_id", item.get("id", "")),
        "chunk_id": item.get("chunk_id", item.get("id", "")),
        "title": fix_mojibake(item.get("title", "")),
        "url": str(item.get("url", "") or ""),
        "source": fix_mojibake(item.get("source", "")),
        "topic": fix_mojibake(item.get("topic", "")),
        "author": fix_mojibake(item.get("author", "")),
        "crawled_at": item.get("crawled_at"),
        "text": text,
    }


def _flush_shard(
    *,
    output_dir: Path,
    shard_id: int,
    embeddings: Any,
    metadata_rows: list[dict[str, Any]],
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    emb_path = output_dir / f"embeddings_part_{shard_id:05d}.npy"
    meta_path = output_dir / f"metadata_part_{shard_id:05d}.parquet"

    _write_numpy(emb_path, embeddings)
    _write_metadata(metadata_rows, meta_path)

    print("saved:", emb_path, embeddings.shape)
    print("saved:", meta_path, len(metadata_rows))
    return shard_id + 1


def _write_numpy(path: Path, embeddings: Any) -> None:
    import numpy as np

    np.save(path, np.asarray(embeddings, dtype="float32"))


def _write_metadata(metadata: Any, path: Path) -> None:
    import pandas as pd

    frame = metadata if hasattr(metadata, "to_parquet") else pd.DataFrame(metadata)
    frame.to_parquet(path, index=False)


def _write_faiss_index(index: Any, path: Path) -> None:
    faiss = _import_faiss()
    faiss.write_index(index, str(path))


def _import_faiss():
    try:
        import faiss
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'faiss'. Install faiss-cpu or faiss-gpu "
            "to build semantic index."
        ) from exc

    return faiss
