import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from services.travel.service import SearchService


# ----------------------------
# Helper: mock settings
# ----------------------------
@pytest.fixture
def mock_settings(mocker):
    mock = MagicMock()
    mock.search_provider = "tavily"
    mock.tavily_api_key = "test-key"
    mock.serper_api_key = "test-serper"
    mock.max_article_chars = 200
    mock.request_timeout = 10

    mocker.patch("services.travel.service.get_settings", return_value=mock)
    return mock


@pytest.fixture
def service(mock_settings):
    return SearchService()


# ----------------------------
# _clean_text
# ----------------------------
def test_clean_text_basic(service):
    text = "<p>Hello   World</p>"
    result = service._clean_text(text, 50)

    assert result == "Hello World"


def test_clean_text_empty(service):
    assert service._clean_text(None, 50) == ""


# ----------------------------
# Tavily tests
# ----------------------------
@pytest.mark.asyncio
async def test_search_tavily_success(service, mocker):
    mock_client = AsyncMock()

    mock_client.search.return_value = {
        "results": [
            {
                "title": "Test",
                "url": "http://a.com",
                "content": "This is valid content " * 10,
                "score": 0.9,
            }
        ]
    }

    mock_tavily = MagicMock()
    mock_tavily.AsyncTavilyClient.return_value = mock_client

    mocker.patch("importlib.import_module", return_value=mock_tavily)

    results = await service._search_tavily("Goa", max_results=2)

    assert len(results) > 0
    assert results[0]["source"] == "tavily"


@pytest.mark.asyncio
async def test_search_tavily_no_api_key(service):
    service.tavily_api_key = None

    results = await service._search_tavily("Goa", 2)

    assert results == []


@pytest.mark.asyncio
async def test_search_tavily_import_error(service, mocker):
    mocker.patch("importlib.import_module", side_effect=Exception("fail"))

    results = await service._search_tavily("Goa", 2)

    assert results == []


@pytest.mark.asyncio
async def test_search_tavily_filters_short_content(service, mocker):
    mock_client = AsyncMock()

    mock_client.search.return_value = {
        "results": [
            {
                "title": "Short",
                "url": "http://b.com",
                "content": "too short",
                "score": 0.9,
            }
        ]
    }

    mock_tavily = MagicMock()
    mock_tavily.AsyncTavilyClient.return_value = mock_client

    mocker.patch("importlib.import_module", return_value=mock_tavily)

    results = await service._search_tavily("Goa", 2)

    assert results == []

@pytest.mark.asyncio
async def test_search_serper_no_api_key(service):
    service.serper_api_key = None

    results = await service._search_serper("Goa", 2)

    assert results == []

# ----------------------------
# search_travel_articles
# ----------------------------
@pytest.mark.asyncio
async def test_search_travel_articles_tavily(service, mocker):
    service.provider = "tavily"

    mocker.patch.object(service, "_search_tavily", return_value=[{"title": "x"}])

    results = await service.search_travel_articles("Goa")

    assert results == [{"title": "x"}]


@pytest.mark.asyncio
async def test_search_travel_articles_serper(service, mocker):
    service.provider = "serper"

    mocker.patch.object(service, "_search_serper", return_value=[{"title": "y"}])

    results = await service.search_travel_articles("Goa")

    assert results == [{"title": "y"}]