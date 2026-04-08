from langgraph.graph import StateGraph, END
from app.core.models import ClaimState
from app.agents.segregator import segregator_agent
from app.agents.id_agent import id_agent
from app.agents.discharge_agent import discharge_agent
from app.agents.bill_agent import bill_agent
from app.agents.aggregator import aggregator


def build_pipeline() -> StateGraph:
    """
    Build and compile the LangGraph pipeline.

    Flow:
        START
          ↓
        segregator_agent          ← classifies all pages into 9 doc types
          ↓         ↓        ↓
        id_agent  discharge  bill_agent   ← parallel extraction (each gets only its pages)
          ↓         ↓        ↓
              aggregator            ← combines all results
                  ↓
                END

    Note: LangGraph runs non-dependent nodes in parallel automatically
    when they share the same input node and converge to the same output node.
    """

    # Use dict-based state so LangGraph can handle it natively
    # ClaimState fields are passed as a typed dict under the hood
    graph = StateGraph(ClaimState)

    # Register all nodes
    graph.add_node("segregator", segregator_agent)
    graph.add_node("id_agent", id_agent)
    graph.add_node("discharge_agent", discharge_agent)
    graph.add_node("bill_agent", bill_agent)
    graph.add_node("aggregator", aggregator)

    # Entry point
    graph.set_entry_point("segregator")

    # Segregator fans out to all 3 extraction agents
    graph.add_edge("segregator", "id_agent")
    graph.add_edge("segregator", "discharge_agent")
    graph.add_edge("segregator", "bill_agent")

    # All 3 agents feed into aggregator
    graph.add_edge("id_agent", "aggregator")
    graph.add_edge("discharge_agent", "aggregator")
    graph.add_edge("bill_agent", "aggregator")

    # Aggregator is the terminal node
    graph.add_edge("aggregator", END)

    return graph.compile()


# Singleton — compile once at startup
pipeline = build_pipeline()
