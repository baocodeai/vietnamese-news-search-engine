from collections import Counter, defaultdict
import heapq
import math

from backend.app.services.preprocessing.text_normalizer import (
    clean_display_text,
    tokenize,
)
from backend.app.services.retrieval.base import SearchDocument, SearchResult


class BM25SearchEngine:
    """
    Search engine dung BM25 cho tap bao tieng Viet.

    BM25 phu hop voi search tin tuc vi can bang tan suat tu khoa,
    do hiem cua tu khoa va do dai document.
    """

    def __init__(
        self,
        k1: float = 1.5,
        b: float = 0.75,
        title_weight: int = 3,
    ):
        self.k1 = k1
        self.b = b
        self.title_weight = title_weight

        self.documents: list[SearchDocument] = []
        self.doc_len: list[int] = []
        self.avgdl = 0.0

        self.inverted_index: defaultdict[str,
                                         list[tuple[int, int]]] = defaultdict(list)

        self.idf: dict[str, float] = {}

    def _build_document_text(self, document: SearchDocument) -> str:
        """
        Tao text dung de index tu cac field cua dataset.

        Title duoc lap lai de boost. Cac field processed/unaccented duoc
        dua vao index de query co dau, khong dau va token da tach deu match.
        """
        title_parts = [document.title,
                       document.title_processed] * self.title_weight
        body_parts = [
            document.content_processed,
            document.combined_processed,
            document.combined_unaccented,
            document.content,
        ]

        return " ".join(part for part in title_parts + body_parts if part)

    def build(self, documents: list[SearchDocument]) -> None:
        """
        Build inverted index tu danh sach documents.
        """
        self.documents = documents
        self.doc_len = []
        self.avgdl = 0.0
        self.inverted_index.clear()
        self.idf.clear()

        tokenized_docs = [
            tokenize(self._build_document_text(document))
            for document in documents
        ]

        self.doc_len = [len(tokens) for tokens in tokenized_docs]
        self.avgdl = sum(self.doc_len) / \
            len(self.doc_len) if self.doc_len else 0.0

        doc_freq = Counter()

        for doc_index, tokens in enumerate(tokenized_docs):
            term_counts = Counter(tokens)

            for term, tf in term_counts.items():
                self.inverted_index[term].append((doc_index, tf))
                doc_freq[term] += 1

        total_docs = len(documents)
        self.idf = {
            term: math.log(1 + (total_docs - df + 0.5) / (df + 0.5))
            for term, df in doc_freq.items()
        }

    def search(self, query: str, top_k: int = 10) -> list[SearchResult]:
        """
        Search query va tra ve top_k ket qua co score cao nhat.
        """
        if top_k <= 0:
            return []

        query_tokens = tokenize(query)
        if not query_tokens or not self.documents or self.avgdl == 0:
            return []

        scores = defaultdict(float)

        for term in set(query_tokens):
            postings = self.inverted_index.get(term, [])
            idf = self.idf.get(term, 0.0)

            for doc_index, tf in postings:
                doc_length = self.doc_len[doc_index]
                denominator = tf + self.k1 * (
                    1 - self.b + self.b * doc_length / self.avgdl
                )
                scores[doc_index] += idf * (tf * (self.k1 + 1)) / denominator

        top_items = heapq.nlargest(
            top_k, scores.items(), key=lambda item: item[1])

        results = []
        for doc_index, score in top_items:
            document = self.documents[doc_index]
            results.append(
                SearchResult(
                    doc_id=document.id,
                    score=score,
                    title=clean_display_text(document.title),
                    snippet=clean_display_text(
                        document.content, max_chars=300),
                    url=document.url,
                    source=document.source,
                    topic=document.topic,
                    author=document.author,
                    crawled_at=document.crawled_at,
                )
            )

        return results
