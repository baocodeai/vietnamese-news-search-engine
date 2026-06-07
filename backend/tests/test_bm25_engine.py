from backend.app.services.retrieval.base import SearchDocument
from backend.app.services.retrieval.bm25_engine import BM25SearchEngine


def test_bm25_returns_relevant_document_first():
    documents = [
        SearchDocument(
            id=1,
            title="Liverpool th\u1eafng Strasbourg",
            content="D\u1ef1 \u0111o\u00e1n b\u00f3ng \u0111\u00e1 Liverpool vs Strasbourg giao h\u1eefu CLB.",
            url="https://example.com/liverpool",
            source="test",
            topic="Th\u1ec3 thao",
        ),
        SearchDocument(
            id=2,
            title="C\u01b0\u1edbp ti\u1ec7m v\u00e0ng t\u1ea1i Hu\u1ebf",
            content="C\u00f4ng an b\u1eaft gi\u1eef nghi ph\u1ea1m trong v\u1ee5 c\u01b0\u1edbp ti\u1ec7m v\u00e0ng.",
            url="https://example.com/hue",
            source="test",
            topic="Ph\u00e1p lu\u1eadt",
        ),
    ]
    engine = BM25SearchEngine()
    engine.build(documents)

    results = engine.search("Liverpool Strasbourg du doan bong da", top_k=2)

    assert len(results) > 0
    assert results[0].doc_id == 1
    assert results[0].score > 0


def test_bm25_uses_processed_fields_from_dataset():
    documents = [
        SearchDocument(
            id=1,
            title="Tin the thao",
            content="Noi dung ngan.",
            url="https://example.com/liverpool",
            title_processed="soi_keo liverpool strasbourg",
            content_processed="du_doan bong_da giao_huu clb",
            combined_unaccented="soi_keo liverpool strasbourg du_doan bong_da",
        ),
        SearchDocument(
            id=2,
            title="Tin kinh te",
            content="Gia xang dau duoc dieu chinh.",
            url="https://example.com/economy",
        ),
    ]
    engine = BM25SearchEngine()
    engine.build(documents)

    results = engine.search("du doan bong da liverpool", top_k=1)

    assert len(results) == 1
    assert results[0].doc_id == 1


def test_bm25_supports_unaccented_query_against_mojibake_document():
    documents = [
        SearchDocument(
            id=1,
            title="C\u00c6\u00b0\u00e1\u00bb\u203ap ti\u00e1\u00bb\u2021m v\u00c3\u00a0ng t\u00e1\u00ba\u00a1i Hu\u00e1\u00ba\u00bf",
            content="C\u00c3\u00b4ng an \u0111i\u00e1\u00bb\u0081u tra v\u00e1\u00bb\u00a5 c\u00c6\u00b0\u00e1\u00bb\u203ap.",
            url="https://example.com/hue",
        )
    ]
    engine = BM25SearchEngine()
    engine.build(documents)

    results = engine.search("cuop tiem vang hue", top_k=1)

    assert len(results) == 1
    assert results[0].doc_id == 1
    assert results[0].title == "C\u01b0\u1edbp ti\u1ec7m v\u00e0ng t\u1ea1i Hu\u1ebf"


def test_bm25_returns_empty_list_for_empty_query():
    documents = [
        SearchDocument(
            id=1,
            title="Liverpool th\u1eafng Strasbourg",
            content="Tin th\u1ec3 thao.",
            url="https://example.com/1",
        )
    ]
    engine = BM25SearchEngine()
    engine.build(documents)

    assert engine.search("", top_k=5) == []


def test_bm25_returns_empty_list_before_build():
    engine = BM25SearchEngine()

    assert engine.search("Liverpool", top_k=5) == []


def test_bm25_returns_empty_list_when_top_k_is_not_positive():
    documents = [
        SearchDocument(
            id=1,
            title="Liverpool",
            content="Tin the thao.",
            url="https://example.com/1",
        )
    ]
    engine = BM25SearchEngine()
    engine.build(documents)

    assert engine.search("Liverpool", top_k=0) == []
