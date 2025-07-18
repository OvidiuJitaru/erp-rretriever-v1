from typing import Optional

from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage

from app.agent.agent_state import AgentState
from app.core.meta import MetaLogger


class Agent(metaclass=MetaLogger):
    """
    Agentic assistanc for processing the user request, generate an sql query, execute it and return the result.
    """

    def __init__(self, **kwargs):
        self.log("Agent initialized")
        self.workflow = self._agent_init()

    def _agent_init(self):

        builder = StateGraph(AgentState)

        builder.add_node("chat_start", self.chat_start)
        builder.add_node("llm_response", self.llmgen)
        builder.add_edge(START, "chat_start")
        builder.add_edge("chat_start", "llm_response")
        builder.add_edge("llm_response", END)
        workflow = builder.compile()

        return workflow


    def chat_start(self, state: AgentState):

        return {
            "messages": [HumanMessage(content=state["user_message"])]
        }

    def llmgen(self, state: AgentState):
        return {
            "messages": [AIMessage(content="this is the pseudo generated message from an AI")]
        }

    def chat(self, in_message:str):
        initial_state : AgentState = {
            "user_message" : in_message,
            "messages" : [], # start with empty list otherwise will not add the first message
            "gen_sql_query": None,
            "sql_explanation": None,
            "logic_sim_th": 0.3,
            "table_sim_th": 0.3,
            "augment":None
        }

        final_state = self.workflow.invoke(initial_state)


        return final_state



agent: Optional[Agent] = None

def get_agent():
    """Initialize global Agent"""

    global agent

    if agent is None:
        agent = Agent()
    return agent