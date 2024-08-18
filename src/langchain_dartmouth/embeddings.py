from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings

from typing import Callable, List, Optional

from langchain_dartmouth.base import AuthenticatedMixin
from langchain_dartmouth.definitions import EMBEDDINGS_BASE_URL


class DartmouthEmbeddings(HuggingFaceEndpointEmbeddings, AuthenticatedMixin):
    """Embedding models deployed on Dartmouth's cluster.

    :param model_name: The name of the embedding model to use, defaults to ``"bge-large-en-v1-5"``.
    :type model_name: str, optional
    :param model_kwargs: Keyword arguments to pass to the model.
    :type model_kwargs: dict, optional
    :param dartmouth_api_key: A Dartmouth API key (obtainable from https://developer.dartmouth.edu). If not specified, it is attempted to be inferred from an environment variable ``DARTMOUTH_API_KEY``.
    :type dartmouth_api_key: str, optional
    :param authenticator: A Callable returning a JSON Web Token (JWT) for authentication. Only needed for special use cases.
    :type authenticator: Callable, optional
    :param jwt_url: URL of the Dartmouth API endpoint returning a JSON Web Token (JWT).
    :type jwt_url: str, optional
    :param embeddings_server_url: URL pointing to an embeddings endpoint, defaults to ``"https://ai-api.dartmouth.edu/tei/"``.
    :type embeddings_server_url: str, optional
    """

    authenticator: Optional[Callable] = None
    dartmouth_api_key: Optional[str] = None
    jwt_url: Optional[str] = None
    embeddings_server_url: Optional[str] = None

    def __init__(
        self,
        model_name: str = "bge-large-en-v1-5",
        model_kwargs: Optional[dict] = None,
        dartmouth_api_key: Optional[str] = None,
        authenticator: Optional[Callable] = None,
        jwt_url: Optional[str] = None,
        embeddings_server_url: Optional[str] = None,
    ):
        """Initializes the object"""
        if embeddings_server_url:
            endpoint = f"{embeddings_server_url}{model_name}/"
        else:
            endpoint = f"{EMBEDDINGS_BASE_URL}{model_name}/"
        super().__init__(model=endpoint, model_kwargs=model_kwargs)
        self.authenticator = authenticator
        self.dartmouth_api_key = dartmouth_api_key
        self.authenticate(jwt_url=jwt_url)

    def embed_query(self, text: str) -> List[float]:
        """Call out to the embedding endpoint to retrieve the embedding of the query text.

        :param text: The text to embed.
        :type text: str
        :return: Embeddings for the text.
        :rtype: List[float]
        """
        try:
            return super().embed_query(text)
        except Exception:
            self.authenticate(jwt_url=self.jwt_url)
            return super().embed_query(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Call out to the embedding endpoint to retrieve the embeddings of multiple texts.

        :param text: The list of texts to embed.
        :type text: str
        :return: Embeddings for the texts.
        :rtype: List[List[float]]
        """
        try:
            return super().embed_documents(texts)
        except Exception:
            self.authenticate(jwt_url=self.jwt_url)
            return super().embed_documents(texts)

    async def aembed_query(self, text: str) -> List[float]:
        """Async Call to the embedding endpoint to retrieve the embedding of the query text.

        :param text: The text to embed.
        :type text: str
        :return: Embeddings for the text.
        :rtype: List[float]
        """
        try:
            response = await super().aembed_query(text)
            return response
        except Exception:
            self.authenticate(jwt_url=self.jwt_url)
            response = await super().aembed_query(text)
            return response

    async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
        """Async Call to the embedding endpoint to retrieve the embeddings of multiple texts.

        :param text: The list of texts to embed.
        :type text: str
        :return: Embeddings for the texts.
        :rtype: List[List[float]]
        """
        try:
            response = await super().aembed_documents(texts)
            return response
        except Exception:
            self.authenticate(jwt_url=self.jwt_url)
            response = await super().aembed_documents(texts)
            return response
