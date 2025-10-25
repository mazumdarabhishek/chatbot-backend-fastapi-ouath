from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.schemas.chat import AgentState

from app.core.app_logger import setup_daily_logger
import traceback
logger = setup_daily_logger("auth_services")
from app.core.config import settings, get_model


model = get_model()

async def call_model(state: AgentState) -> AgentState:
    
    messages = [SystemMessage(content="You are a helpful assistant.")] + state["messages"] + [HumanMessage(content=state["user_input"] if state.get("user_input") else "Generate initial greeting.")]
    
    response = await model.ainvoke(messages)
    state["turns_to_compress"] += 1
    state["messages"].append(AIMessage(content=response.content))
    
    return state


async def should_compress(state: AgentState) -> AgentState:
    if not state.get("journal_complete"):
        if state.get("turns_to_compress") >= 3:
            SUMMARY_PROMPT = """Summarize the following messages into a concise context that captures the key points of the conversation so far.
            The summary should be brief but informative, allowing the assistant to understand the context without needing to review all previous messages.
            maximum 100 words.
            Messages:"""
            logger.debug(f"Executing Context Compression @ turns{state.get('turns_to_compression')}")
            messages_to_compress = state.get("messages")
            messages_to_compress = "\n".join([f"{i.type}:{i.content}" for i in messages_to_compress])
            context_summary = await model.ainvoke([SystemMessage(content= SUMMARY_PROMPT), 
                                            HumanMessage(content= messages_to_compress)])
            state["messages"] = [context_summary]
            state["turns_to_compress"] = 0
            logger.info("Compression complete")
            return state
    return state


def build_chat_graph():
    builder = StateGraph(AgentState)
    builder.add_node("call_model", call_model)
    builder.add_node("should_compress", should_compress)
    builder.add_edge("should_compress", "call_model")
    builder.set_entry_point("should_compress")
    builder.add_edge("call_model", END)
    return builder

