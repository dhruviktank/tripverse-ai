"""LangGraph orchestration for trip planning workflow."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from llm_client import get_llm_client
from search_client import get_search_client
from vector_db import get_vector_db_client


class TripPlanningState(BaseModel):
    """State for trip planning workflow."""
    
    trip_description: str
    budget: str
    pace: str
    starting_from: str
    context_documents: List[Dict[str, Any]] = Field(default_factory=list)
    initial_draft: Optional[str] = None
    refined_itinerary: Optional[str] = None
    final_plan: Optional[Dict[str, Any]] = None
    errors: List[str] = Field(default_factory=list)


class TripPlanningOrchestrator:
    """Orchestrate trip planning using LangGraph."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.llm_client = get_llm_client()
        self.search_client = get_search_client()
        self.vector_db = get_vector_db_client()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        workflow = StateGraph(TripPlanningState)
        
        # Add nodes
        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("generate_plan", self._generate_plan)
        workflow.add_node("finalize_plan", self._finalize_plan)
        
        # Add edges
        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("retrieve_context", "generate_plan")
        workflow.add_edge("generate_plan", "finalize_plan")
        workflow.add_edge("finalize_plan", END)
        
        return workflow.compile()
    
    async def _retrieve_context(self, state: TripPlanningState) -> Dict[str, Any]:
        """Retrieve relevant context from vector database."""
        try:
            # Search for similar trips and destinations.
            search_query = f"{state.trip_description} {state.budget} {state.starting_from}"
            location = (state.starting_from or "").strip().lower()

            if location:
                has_cached_location_data = await self.vector_db.has_location_data(location)
                if not has_cached_location_data:
                    fresh_articles = await self.search_client.search_travel_articles(
                        location=location,
                        max_results=5,
                    )
                    cached_count = await self.vector_db.cache_location_documents(location, fresh_articles)
                    if cached_count == 0:
                        state.errors.append(
                            f"JIT RAG fetch returned no cacheable web documents for '{location}'."
                        )

                documents = await self.vector_db.search_documents(
                    query=search_query,
                    top_k=5,
                    metadata_filter={
                        "category": {"$eq": "destination_guide"},
                        "location": {"$eq": location},
                    },
                )
            else:
                documents = []

            if not documents:
                documents = await self.vector_db.search_documents(
                    query=search_query,
                    top_k=5,
                    metadata_filter={"category": {"$eq": "destination_guide"}},
                )

            state.context_documents = documents
            return {"context_documents": documents}
        except Exception as e:
            state.errors.append(f"Context retrieval error: {str(e)}")
            return {}
    
    async def _generate_plan(self, state: TripPlanningState) -> Dict[str, Any]:
        """Generate full itinerary in a single LLM call for lower latency."""
        system_prompt = """You are an expert travel planner. Create a practical and complete trip itinerary in one response.
Use concise, high-value details and realistic logistics."""

        context_snippets = []
        for doc in state.context_documents[:5]:
            metadata = doc.get("metadata") or {}
            snippet = (metadata.get("content") or "").strip()
            if snippet:
                context_snippets.append(snippet[:500])
        context_block = "\n\n".join(context_snippets) if context_snippets else "No external context available."

        user_prompt = f"""Plan a complete trip using these details:
- Description: {state.trip_description}
- Budget: {state.budget}
- Pace: {state.pace}
- Starting from: {state.starting_from}

Reference context:
{context_block}

Return all sections in a single response with these exact headings:
1) Day-by-Day Itinerary
2) Food and Culture
3) Budget Breakdown
4) Safety and Practical Tips"""

        try:
            plan_text = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt
            )
            final_text = plan_text if isinstance(plan_text, str) else str(plan_text)
            state.initial_draft = final_text
            state.refined_itinerary = final_text
            return {
                "initial_draft": final_text,
                "refined_itinerary": final_text,
            }
        except Exception as e:
            state.errors.append(f"Plan generation error: {str(e)}")
            return {}
    
    async def _finalize_plan(self, state: TripPlanningState) -> Dict[str, Any]:
        """Finalize the complete trip plan."""
        final_plan = {
            "trip_description": state.trip_description,
            "budget": state.budget,
            "pace": state.pace,
            "starting_from": state.starting_from,
            "itinerary": state.refined_itinerary,
            "context_sources": len(state.context_documents)
        }
        state.final_plan = final_plan
        return {"final_plan": final_plan}
    
    async def plan_trip(self, trip_input: Dict[str, str]) -> Dict[str, Any]:
        """Execute the complete trip planning workflow."""
        state = TripPlanningState(
            trip_description=trip_input.get("trip_description", ""),
            budget=trip_input.get("budget", ""),
            pace=trip_input.get("pace", ""),
            starting_from=trip_input.get("starting_from", "")
        )
        
        try:
            result = await self.graph.ainvoke(state.model_dump())
            if hasattr(result, "model_dump"):
                result = result.model_dump()
            elif not isinstance(result, dict):
                result = {"final_plan": result}
            return {
                "success": True,
                "plan": result.get("final_plan"),
                "errors": result.get("errors") or None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "errors": state.errors
            }


# Global instance
_orchestrator: Optional[TripPlanningOrchestrator] = None


def get_trip_planning_orchestrator() -> TripPlanningOrchestrator:
    """Get or create the trip planning orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = TripPlanningOrchestrator()
    return _orchestrator
