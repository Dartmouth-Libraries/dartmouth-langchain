from langchain_core.callbacks import Callbacks
from langchain_core.documents import Document, BaseDocumentCompressor
from langchain_core.pydantic_v1 import Extra, Field

import operator
from typing import Callable, List, Optional, Sequence

from langchain_dartmouth.base import AuthenticatedMixin
from langchain_dartmouth.cross_encoders import TextEmbeddingInferenceClient
from langchain_dartmouth.definitions import RERANK_BASE_URL


class TeiCrossEncoderReranker(BaseDocumentCompressor):
    """Document compressor that uses an instance of TextEmbeddingInference for reranking."""

    client: TextEmbeddingInferenceClient = Field(
        default_factory=lambda: TextEmbeddingInferenceClient()
    )
    top_n: int = 3
    """Number of documents to return."""

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid
        arbitrary_types_allowed = True

    def compress_documents(
        self,
        documents: Sequence[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> Sequence[Document]:
        """
        Rerank documents using TextEmbeddingInference.

        Args:
            documents: A sequence of documents to compress.
            query: The query to use for compressing the documents.
            callbacks: Callbacks to run during the compression process.

        Returns:
            A sequence of compressed documents.
        """
        scores = self.client.rerank(query, [doc.page_content for doc in documents])
        docs_with_scores = list(zip(documents, scores))
        result = sorted(docs_with_scores, key=operator.itemgetter(1), reverse=True)
        return [doc for doc, _ in result[: self.top_n]]


class DartmouthReranker(TeiCrossEncoderReranker, AuthenticatedMixin):
    """Reranks documents using a reranking model deployed in the Dartmouth cloud.

    :param model_name: The name of the embedding model to use, defaults to ``"bge-reranker-v2-m3"``.
    :type model_name: str, optional
    :param top_n: Number of documents to return, defaults to ``3``
    :type top_n: int
    :param dartmouth_api_key: A Dartmouth API key (obtainable from https://developer.dartmouth.edu). If not specified, it is attempted to be inferred from an environment variable DARTMOUTH_API_KEY.
    :type dartmouth_api_key: str, optional
    :param authenticator: A Callable returning a JSON Web Token (JWT) for authentication.
    :type authenticator: Callable, optional
    :param jwt_url: URL of the Dartmouth API endpoint returning a JSON Web Token (JWT).
    :type jwt_url: str, optional
    :param embeddings_server_url: URL pointing to an embeddings endpoint, defaults to ``"https://ai-api.dartmouth.edu/tei/"``.
    :type embeddings_server_url: str, optional
    """

    authenticator: Callable = None
    dartmouth_api_key: str = None
    jwt_url: str = None
    embeddings_server_url: str = None

    def __init__(
        self,
        top_n: int = 3,
        dartmouth_api_key: str = None,
        model_name: str = "bge-reranker-v2-m3",
        authenticator: Callable = None,
        jwt_url: str = None,
        embeddings_server_url: str = None,
    ):
        """Initializes the object"""
        if embeddings_server_url:
            endpoint = f"{embeddings_server_url}{model_name}/"
        else:
            endpoint = f"{RERANK_BASE_URL}{model_name}/"

        super().__init__(
            top_n=top_n,
            client=TextEmbeddingInferenceClient(inference_server_url=endpoint),
        )
        self.authenticator = authenticator
        self.dartmouth_api_key = dartmouth_api_key
        self.authenticate(jwt_url=jwt_url)

    def compress_documents(
        self,
        documents: List[Document],
        query: str,
        callbacks: Optional[Callbacks] = None,
    ) -> List[Document]:
        """Returns the most relevant documents with respect to a query.

        :param documents: Documents to compress.
        :type documents: Sequence[Document]
        :param query: Query to consider.
        :type query: str
        :param callbacks: Callbacks to run during the compression process, defaults to ``None``
        :type callbacks: Callbacks, optional
        :return: The :attr:`~.DartmouthReranker.top_n` highest-ranked documents
        :rtype: Sequence[Document]
        """
        try:
            return super().compress_documents(documents, query, callbacks)
        except Exception:
            self.authenticate(jwt_url=self.jwt_url)
            return super().compress_documents(documents, query, callbacks)


if __name__ == "__main__":
    from langchain.docstore.document import Document

    docs = [
        Document(page_content="Deep Learning is not..."),
        Document(page_content="Deep learning is..."),
    ]
    query = "What is Deep Learning?"
    reranker = DartmouthReranker()
    ranked_docs = reranker.compress_documents(query=query, documents=docs)
    print(ranked_docs)
