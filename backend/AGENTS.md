# TripVerse AI Backend - Agents & Workflows

## Architecture Overview

TripVerse AI backend is built as a multi-layered GenAI system using **FastAPI**, **LangGraph**, and **Vector Databases** to deliver intelligent, context-aware trip planning. The system follows an **orchestration-based architecture** where agents coordinate between LLM generation, semantic search, and real-time web retrieval.

---

## System Components

### 1. **FastAPI Application** (`main.py`)
**Role**: HTTP API gateway and request router

**Endpoints:**
- `GET /health` - Health check to verify service is running
- `POST /api/trips/plan` - Primary trip planning endpoint
- `GET /api/destinations/search` - Destination search via vector similarity
- `GET /` - Root service info

**Request Flow:**
```
HTTP Request 
  ↓
FastAPI Router 
  ↓
Validation (Pydantic models) 
  ↓
Orchestrator 
  ↓
JSON Response
```

**Key Features:**
- CORS enabled for cross-origin frontend requests
- Structured error handling with HTTPException
- Async/await for non-blocking I/O
- Centralized configuration via `config.py`

---

### 2. **Trip Planning Orchestrator** (`orchestrator.py`)
**Role**: Multi-stage LangGraph workflow for intelligent itinerary generation

**Workflow Stages:**

#### Stage 1: **Retrieve Context** (`_retrieve_context`)
Gathers semantic and real-time context for the trip.

**Process:**
1. Extract location from `starting_from` field
2. Check if location data exists in vector DB cache
3. **Cache Miss Path**: 
   - Fetch top 5 travel articles from web (Tavily/Serper API)
   - Parse and embed using Google Generative AI embeddings
   - Store in Pinecone vector DB for future reuse (JIT RAG caching)
4. **Cache Hit Path**: 
   - Query Pinecone directly with 5-context limit
   - Return cached destination guides, reviews, logistics
5. Fallback: If no location-specific data, query generic travel contexts

**Metadata Filtering:**
```json
{
  "category": "destination_guide",
  "location": "<searched_location>"
}
```

#### Stage 2: **Generate Plan** (`_generate_plan`)
Produces comprehensive itinerary in **single LLM call** for low latency.

**Input Composition:**
```
System Prompt: 
  "You are an expert travel planner. Create practical, complete trip itinerary..."

User Prompt:
  - Trip description + duration + preferences
  - Budget tier (Value/Balanced/Luxury)
  - Travel pace (Relaxed/Balanced/High-energy)
  - Starting location
  - Context documents (max 5 snippets, 500 chars each)

Output Format (Structured):
  1) Day-by-Day Itinerary
  2) Food and Culture Highlights
  3) Budget Breakdown
  4) Safety and Practical Tips
```

**Latency Optimization:**
- Single call instead of multi-turn conversation
- Context injected as embeddings, not tokens
- Streaming disabled for cleaner structured output
- All reasoning contained in one LLM response

#### Stage 3: **Finalize Plan** (`_finalize_plan`)
Packages the plan with metadata for frontend consumption.

**Output Structure:**
```json
{
  "trip_description": "7 days Italy food tour",
  "budget": "Balanced",
  "pace": "Relaxed",
  "starting_from": "New York",
  "itinerary": "Complete plan text with all sections",
  "context_sources": 5,
  "errors": []
}
```

---

### 3. **LLM Client** (`llm_client.py`)
**Role**: Unified interface to multiple LLM providers

**Supported Providers:**
- **Gemini** (Google) - Primary since it supports embeddings + generation
- **Grok** (Groq) - Alternative with high throughput

**Features:**
- Lazy initialization (only loads chosen provider)
- Configurable temperature (default: 0.7 for balanced creativity)
- Retry logic with exponential backoff
- Request timeout settings (default: 60s)
- Message normalization across provider APIs

**Initialization:**
```python
llm_client = get_llm_client()  # Singleton pattern

# Choose provider via config:
LLM_PROVIDER=gemini  # or 'grok'
LLM_MODEL=gemini-2.0-flash  # or 'grok-3-turbo'
```

**Generation Call:**
```python
response = await llm_client.generate(
    prompt="User request",
    system_prompt="Expert travel planner...",
    temperature=0.7
)
```

---

### 4. **Vector Database** (`vector_db.py`)
**Role**: Semantic search and JIT RAG cache for travel content

**Provider:** Pinecone (serverless)

**Key Methods:**

#### `search_documents(query, top_k=5, metadata_filter=None)`
Returns semantically similar documents ranked by relevance.

```python
documents = await vector_db.search_documents(
    query="7 days Italy food tour",
    top_k=5,
    metadata_filter={
        "category": {"$eq": "destination_guide"},
        "location": {"$eq": "italy"}
    }
)
```

#### `has_location_data(location)`
Checks if location has cached documents to avoid redundant web fetches.

#### `cache_location_documents(location, articles)`
Stores freshly fetched web articles with metadata.

```python
cached_count = await vector_db.cache_location_documents(
    location="Italy",
    articles=[
        {
            "title": "Rome Travel Guide",
            "url": "...",
            "content": "..."
        }
    ]
)
```

**Embedding Model:**
- **Google Generative AI Embeddings** with configurable dimensions
- Dimension forced to match Pinecone index (e.g., 768D)
- Automatic retry if provider API is slow

**Metadata Schema:**
```json
{
  "location": "string",
  "category": "destination_guide | experience | restaurant",
  "source": "tavily | serper | internal",
  "timestamp": "ISO 8601"
}
```

---

### 5. **Search Client** (`search_client.py`)
**Role**: Real-time web content retrieval for JIT RAG

**Providers:**
- **Tavily API** - Specialized travel query search
- **Serper API** - Google search alternative

**Features:**

#### `search_travel_articles(location, max_results=5)`
Fetches and cleans top travel articles for a location.

**Query Template:**
```
"{location} travel guide itinerary best places local tips"
```

**Cleaning Pipeline:**
1. HTML unescape and tag stripping
2. Whitespace normalization
3. Truncation to `max_article_chars` (default: 2000)
4. Minimum length filter (40-80 chars)

**Response Format:**
```json
{
  "title": "Rome Travel Guide 2024",
  "url": "https://...",
  "content": "Cleaned article text...",
  "source": "tavily" | "serper"
}
```

---

## Data Flow: Trip Planning Request

```
┌─────────────────────────────────────────────────────────────────┐
│ Frontend User Submits Trip Request                               │
│ Destination, Budget, Pace, Duration, Preferences                │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ FastAPI POST /api/trips/plan                                    │
│ - Validates TripPlanRequest                                     │
│ - Extracts location from starting_from                          │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ Orchestrator.plan_trip()                                        │
│ Initialize LangGraph workflow state                             │
└──────────────────────┬──────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ↓                             ↓
   ┌─────────────┐          ┌──────────────────┐
   │ Has cached  │          │ Cache miss:      │
   │ location?   │          │ fetch web search │
   └──────┬──────┘          │ (Tavily/Serper)  │
          │                 └────────┬─────────┘
          │                          │
          ├──────────────────────────┤
          │                          │
          ↓                          ↓
   ┌─────────────────────────────────────────┐
   │ Embed & cache documents in Pinecone     │
   │ (if fresh fetch)                        │
   └──────────────┬────────────────────────┬─┘
                  │                        │
                  └─────────────┬──────────┘
                                ↓
┌─────────────────────────────────────────────────────────────────┐
│ Vector DB Search                                                │
│ Query with trip_description + location metadata filter          │
│ Return top 5 semantically similar documents                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ LLM Generation (_generate_plan)                                 │
│ - Inject context snippets                                       │
│ - Create system + user prompts                                  │
│ - Generate complete itinerary in single call                    │
│ - Parse structured sections                                     │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ Finalize Plan (_finalize_plan)                                  │
│ - Package with metadata                                         │
│ - Count context sources                                         │
│ - Add error flags                                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────────┐
│ Return TripPlanResponse (JSON)                                  │
│ {                                                               │
│   "success": true,                                              │
│   "plan": { itinerary, budget, pace, etc },                     │
│   "errors": [ warnings ]                                        │
│ }                                                               │
└──────────────────────┬──────────────────────────────────────────┘
                       │
                       ↓
        ┌──────────────────────────────────┐
        │ Frontend receives and renders     │
        │ display itinerary or errors      │
        └──────────────────────────────────┘
```

---

## Configuration (`config.py`)

All settings are environment-based via Pydantic Settings:

```
# LLM Settings
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash
LLM_TEMPERATURE=0.7
GEMINI_API_KEY=***

# Vector DB
PINECONE_API_KEY=***
PINECONE_INDEX_NAME=tripverse-destinations
EMBEDDING_DIMENSION=768

# Search (choose one)
TAVILY_API_KEY=*** (preferred)
SERPER_API_KEY=*** (fallback)

# API Server
API_PORT=8000
API_TITLE=TripVerse AI
```

---

## Error Handling & Resilience

### Graceful Degradation Path:

1. **No Location Context**
   - Skip location-specific metadata filter
   - Search generic travel contexts
   - Log warning, continue planning

2. **Web Search Failure**
   - Use existing Pinecone cache
   - If empty, plan with just user input
   - Return warning in `errors` field

3. **LLM Generation Timeout**
   - Retry up to `max_retries` (default: 3)
   - Return 500 error if all retries exhaust

4. **Vector DB Connection**
   - Auto-create index if missing
   - Retry with exponential backoff
   - Return service error to frontend

---

## Performance Characteristics

| Component | Latency | Notes |
|-----------|---------|-------|
| Context retrieval (cached) | 200-400ms | Direct vector search |
| Context retrieval (JIT) | 2-4s | Includes web fetch + embedding |
| LLM generation | 5-12s | Depends on model/context |
| **Total E2E** | **7-16s** | Mostly LLM time |

**Optimization Strategies:**
- Pinecone serverless (no cold starts)
- Single LLM call instead of multi-turn
- Concurrent async operations
- JIT caching reduces repeat requests by 90%+

---

## Testing & Development

### Local Development:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### API Testing:
```bash
# Health check
curl http://localhost:8000/health

# Plan trip
curl -X POST http://localhost:8000/api/trips/plan \
  -H "Content-Type: application/json" \
  -d '{
    "trip_description": "7 days Japan",
    "budget": "Balanced",
    "pace": "Balanced",
    "starting_from": "New York"
  }'
```

---

## Future Enhancements

1. **Multi-turn refinement**: Allow frontend to request plan modifications
2. **Streaming responses**: Real-time itinerary generation
3. **User preference persistence**: Cache user travel styles
4. **Integration APIs**: Flight/hotel availability checks
5. **Batch mode**: Plan multiple trips simultaneously
6. **Analytics**: Track popular destinations, preferences, generation time

---

## Key Decision Log

| Decision | Rationale |
|----------|-----------|
| Single LLM call for plan | Lower latency than multi-turn |
| Pinecone caching | Avoid repeated web fetches |
| Gemini primary | Supports embeddings + generation |
| Context injected as text | Simpler than RAG chain in LLM |
| FastAPI + async | High concurrency, production-ready |
