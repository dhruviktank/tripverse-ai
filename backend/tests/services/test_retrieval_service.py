import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from services.retrieval.service import RetrievalService


# ================= FIXTURES =================

@pytest.fixture
def mock_settings():
    settings = MagicMock()
    settings.embedding_dimension = 3
    settings.embedding_model = "test-model"
    settings.gemini_api_key = "fake-key"
    settings.pinecone_api_key = "fake-pinecone"
    settings.pinecone_index_name = "test-index"
    settings.pinecone_environment = "us-east-1"
    return settings


@pytest.fixture
def mock_pinecone():
    mock_client = MagicMock()

    # simulate index exists
    mock_client.list_indexes.return_value.names.return_value = ["test-index"]

    mock_index = MagicMock()
    mock_client.Index.return_value = mock_index

    mock_client.describe_index.return_value = {"dimension": 3}

    return mock_client, mock_index


@pytest.fixture
def service(mock_settings, mock_pinecone):
    mock_client, mock_index = mock_pinecone

    with patch("services.retrieval.service.get_settings", return_value=mock_settings), \
         patch("services.retrieval.service.Pinecone", return_value=mock_client), \
         patch("services.retrieval.service.GoogleGenerativeAIEmbeddings") as mock_embed:

        embed_instance = MagicMock()
        embed_instance.embed_query = MagicMock(return_value=[0.1, 0.2, 0.3])
        mock_embed.return_value = embed_instance

        service = RetrievalService()
        service.index = mock_index

        return service


# ================= TESTS ======

def test_parse_serverless_environment():
    service = RetrievalService.__new__(RetrievalService)

    cloud, region = service._parse_serverless_environment("us-east-1")
    assert cloud == "aws"
    assert region == "us-east-1"

    cloud, region = service._parse_serverless_environment("us-east-1-aws")
    assert cloud == "aws"


def test_get_retrieval_service_singleton():
    from services.retrieval.service import get_retrieval_service

    with patch("services.retrieval.service.RetrievalService") as mock_cls:
        instance = MagicMock()
        mock_cls.return_value = instance

        s1 = get_retrieval_service()
        s2 = get_retrieval_service()

        assert s1 is s2