import pytest
from unittest.mock import AsyncMock

from services.chat.chat_service import ChatService
from schemas.chat import ConversationContext, Message


# ---------------------------
# Fixtures
# ---------------------------
@pytest.fixture
def mock_session_store():
    store = AsyncMock()
    store.session_exists.return_value = False
    store.get_messages.return_value = []
    store.get_context.return_value = None
    return store


@pytest.fixture
def mock_llm():
    llm = AsyncMock()
    llm.generate.return_value = "Test response"
    return llm


@pytest.fixture
def mock_orchestrator():
    orch = AsyncMock()
    orch.plan_trip.return_value = {"success": True, "plan": {}}
    return orch


@pytest.fixture
def chat_service(mock_session_store, mock_llm, mock_orchestrator):
    service = ChatService(session_store=mock_session_store)
    service.llm_client = mock_llm
    service.orchestrator = mock_orchestrator
    return service


# ---------------------------
# handle_message
# ---------------------------
@pytest.mark.asyncio
async def test_handle_message_invalid_input(chat_service):
    res = await chat_service.handle_message("", "")

    assert res["requires_clarification"] is True


@pytest.mark.asyncio
async def test_handle_message_success(chat_service, mock_session_store):
    mock_session_store.session_exists.return_value = True

    chat_service._extract_context = AsyncMock(
        return_value=ConversationContext(destinations=["Paris"], duration_days=3)
    )

    res = await chat_service.handle_message("s1", "Plan my trip")

    assert res["reply"] == "Test response"
    assert res["suggested_action"] == "generate_plan"


@pytest.mark.asyncio
async def test_handle_message_exception(chat_service):
    chat_service._generate_response = AsyncMock(side_effect=Exception("fail"))

    res = await chat_service.handle_message("s1", "hello")

    assert "error" in res["reply"].lower()


# ---------------------------
# streaming
# ---------------------------
@pytest.mark.asyncio
async def test_handle_message_stream(chat_service, mock_session_store):
    async def fake_stream(_):
        yield "Hello "
        yield "World"

    chat_service._stream_response = fake_stream

    chat_service._extract_context = AsyncMock(
        return_value=ConversationContext(destinations=["Goa"], duration_days=2)
    )

    events = []
    async for e in chat_service.handle_message_stream("s1", "hi"):
        events.append(e)

    assert events[0]["event_type"] == "start"
    assert any(e["event_type"] == "chunk" for e in events)
    assert events[-1]["event_type"] == "end"


@pytest.mark.asyncio
async def test_handle_message_stream_error(chat_service):
    async def broken(_):
        raise Exception("fail")

    chat_service._stream_response = broken

    events = []
    async for e in chat_service.handle_message_stream("s1", "hi"):
        events.append(e)

    assert events[-1]["event_type"] == "error"


# ---------------------------
# context extraction
# ---------------------------
@pytest.mark.asyncio
async def test_extract_context_success(chat_service):
    chat_service.llm_client.generate.return_value = """
    {
      "source": "Ahmedabad",
      "destinations": ["Goa"],
      "preferences": [],
      "budget": "Balanced",
      "pace": "Balanced",
      "duration_days": 3,
      "trip_description": "Trip"
    }
    """

    messages = [Message(role="user", content="Goa 3 days")]

    ctx = await chat_service._extract_context(messages)

    assert ctx.destinations == ["Goa"]
    assert ctx.duration_days == 3


@pytest.mark.asyncio
async def test_extract_context_invalid_json(chat_service):
    chat_service.llm_client.generate.return_value = "invalid json"

    ctx = await chat_service._extract_context([])

    assert isinstance(ctx, ConversationContext)


# ---------------------------
# clarification check
# ---------------------------
def test_check_clarification_needed():
    service = ChatService()

    ctx = ConversationContext(destinations=["Goa"], duration_days=2)
    assert service._check_clarification_needed(ctx) is False

    ctx = ConversationContext(destinations=[], duration_days=None)
    assert service._check_clarification_needed(ctx) is True


# ---------------------------
# suggest action
# ---------------------------
def test_suggest_action():
    service = ChatService()

    ctx = ConversationContext(destinations=["Goa"], duration_days=3)
    assert service._suggest_action(ctx, "") == "generate_plan"

    ctx = ConversationContext(destinations=[], duration_days=3)
    assert service._suggest_action(ctx, "") is None


# ---------------------------
# session info
# ---------------------------
@pytest.mark.asyncio
async def test_get_session_info(chat_service, mock_session_store):
    mock_session_store.session_exists.return_value = True
    mock_session_store.get_messages.return_value = [
        Message(role="user", content="hi")
    ]
    mock_session_store.get_context.return_value = ConversationContext()

    res = await chat_service.get_session_info("s1")

    assert res["session_id"] == "s1"
    assert res["message_count"] == 1


@pytest.mark.asyncio
async def test_get_session_info_not_found(chat_service, mock_session_store):
    mock_session_store.session_exists.return_value = False

    res = await chat_service.get_session_info("s1")

    assert res is None


# ---------------------------
# clear session
# ---------------------------
@pytest.mark.asyncio
async def test_clear_session(chat_service, mock_session_store):
    mock_session_store.delete_session.return_value = True

    res = await chat_service.clear_session("s1")

    assert res is True


# ---------------------------
# generate_plan_from_context
# ---------------------------
@pytest.mark.asyncio
async def test_generate_plan_success(chat_service, mock_session_store):
    mock_session_store.get_context.return_value = ConversationContext(
        destinations=["Dubai"], duration_days=3
    )

    res = await chat_service.generate_plan_from_context("s1")

    assert res["success"] is True


@pytest.mark.asyncio
async def test_generate_plan_missing_context(chat_service, mock_session_store):
    mock_session_store.get_context.return_value = None

    res = await chat_service.generate_plan_from_context("s1")

    assert res["success"] is False


@pytest.mark.asyncio
async def test_generate_plan_missing_destination(chat_service, mock_session_store):
    mock_session_store.get_context.return_value = ConversationContext(
        destinations=[], duration_days=3
    )

    res = await chat_service.generate_plan_from_context("s1")

    assert res["success"] is False
    assert res["requires_destination"] is True


@pytest.mark.asyncio
async def test_generate_plan_missing_duration(chat_service, mock_session_store):
    mock_session_store.get_context.return_value = ConversationContext(
        destinations=["Goa"], duration_days=None
    )

    res = await chat_service.generate_plan_from_context("s1")

    assert res["success"] is False
    assert res["requires_duration"] is True