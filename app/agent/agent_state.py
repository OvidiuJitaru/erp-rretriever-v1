from typing import Annotated, Optional, Dict, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    The state of the agent as it processes a request.
    """
    user_message: str = None
    messages: Annotated[list, add_messages]

    gen_sql_query : Optional[str] = None
    sql_explanation : Optional[str] = None

    # thresholds for RAG similarity
    logic_sim_th: float = 0.3
    table_sim_th: float = 0.3

    # context retrieved with RAG
    augment: Optional[Dict]