# TripVerse AI Backend

A powerful AI-driven trip planning backend built with FastAPI, LangGraph, and Vector Database integration.

## Features

- **GenAI Integration**: Powered by Gemini/Groq for intelligent trip planning
- **LangGraph Orchestration**: Multi-stage workflow for comprehensive trip planning
- **Vector Database**: Semantic search for destinations, experiences, and recommendations
- **JIT RAG Caching**: If location data is missing, fetch top web travel docs and cache in Pinecone on-the-fly
- **Async Processing**: Fast, non-blocking API with async/await support
- **Extensible Architecture**: Modular design for easy feature additions

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── app_factory.py          # FastAPI app construction and router wiring
├── planning_routes.py      # Health, planning, search, and root endpoints
├── auth_routes.py          # Authentication endpoints
├── trip_routes.py          # Trip CRUD and dashboard endpoints
├── schemas/                # Shared request/response models
├── services/               # Shared business logic helpers
├── services/auth_service.py # Authentication persistence and token helpers
├── services/trip_service.py # Trip persistence, queries, and aggregation helpers
├── config.py               # Configuration management
├── database.py             # Async SQLAlchemy setup
├── auth.py                 # JWT and password utilities
├── llm_client.py           # LLM integration (Gemini/Groq)
├── vector_db.py            # Vector database client
├── search_client.py        # Web search integration
├── orchestrator.py         # LangGraph workflow for trip planning
├── models.py               # SQLAlchemy ORM models
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:
- `GEMINI_API_KEY`: Get from https://ai.google.dev/
- `GROK_API_KEY`: Get from https://console.groq.com/ (Groq Cloud)
- `PINECONE_API_KEY`: Get from https://www.pinecone.io/
- `TAVILY_API_KEY` or `SERPER_API_KEY`: For JIT web retrieval when Pinecone has no location data
- Database settings for your vector DB

### 4. Run the Server

```bash
python main.py
```

Server will start at `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /health
```

### Plan Trip
```
POST /api/trips/plan

Request:
{
  "trip_description": "7 days in Japan with anime cafes and nature views",
  "budget": "Balanced",
  "pace": "Balanced",
  "starting_from": "New York"
}

Response:
{
  "success": true,
  "plan": {
    "trip_description": "...",
    "itinerary": "...",
    "recommendations": "...",
    ...
  }
}
```

### Search Destinations
```
GET /api/destinations/search?query=beach+resorts&limit=5
```

## Workflow (LangGraph)

The orchestrator implements a multi-stage workflow:

1. **Retrieve Context**: Search vector DB for relevant destinations and experiences
  - If location docs are missing, run web search (Tavily/Serper), embed and cache them in Pinecone
2. **Generate Draft**: Create initial itinerary using LLM
3. **Refine Itinerary**: Optimize for practicality and realism
4. **Add Recommendations**: Include local food, culture, and hidden gems
5. **Finalize Plan**: Compile comprehensive trip plan with budget breakdown

## Configuration

Key settings in `config.py`:

- `llm_provider`: Switch between Gemini and Grok (via Groq)
- `llm_model`: Specific model to use (gemini-1.5-flash, grok-3, etc.)
- `embedding_model`: Embedding model for vector search (embedding-001 for Gemini)
- Pinecone configuration for vector storage and semantic search

## Testing

```bash
# API documentation
http://localhost:8000/docs

# OpenAPI spec
http://localhost:8000/openapi.json
```

## Vector Database Setup (Pinecone)

1. Create account at https://www.pinecone.io/
2. Create index with dimension 768 (for Google embedding-001)
3. Add API key to `.env`:
   - `PINECONE_API_KEY`: Your Pinecone API key
   - `PINECONE_ENVIRONMENT`: Your Pinecone environment (e.g., us-west-2-aws)
   - `PINECONE_INDEX_NAME`: Your index name in Pinecone

## Development

### Add New Workflow Stages
Edit `orchestrator.py` to extend the LangGraph workflow:

```python
workflow.add_node("new_stage", self._new_stage)
workflow.add_edge("previous_stage", "new_stage")
```

### Add New Endpoints
Add to `planning_routes.py` or a dedicated router module:

```python
@app.get("/api/new-endpoint")
async def new_endpoint():
    pass
```

### Shared Schemas And Services
- Put request/response models in `schemas/`.
- Put reusable query or aggregation logic in `services/`.
- Keep `main.py` as a thin entrypoint that only exposes the ASGI app.

### Customize LLM Prompts
Edit system and user prompts in `orchestrator.py` methods.

## Dependencies

- **FastAPI**: Modern web framework
- **LangChain**: LLM integration
- **LangChain Community**: Extended integrations
- **LangGraph**: Workflow orchestration
- **Pinecone**: Vector database
- **Google Gemini API**: LLM provider (via langchain-community)
- **Groq**: Grok/LLaMA models provider
- **Pydantic**: Data validation

## License

Part of TripVerse AI project
