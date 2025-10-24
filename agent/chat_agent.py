"""
LangGraph chat agent for VE data queries with memory and streaming.
"""
import os
from typing import TypedDict, Annotated, Sequence
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from pathlib import Path
import sys

# Add agent directory to path
sys.path.insert(0, str(Path(__file__).parent))
from data_tools import ALL_TOOLS


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]


class VEChatAgent:
    """Value Engineering Chat Agent using LangGraph."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # GPT-4 mini model
            api_key=self.api_key,
            streaming=True,
            temperature=0.7
        )
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(ALL_TOOLS)
        
        # Create graph
        self.graph = self._create_graph()
        
        # Memory saver for checkpointing
        self.memory = MemorySaver()
        
        # Compile graph with memory
        self.app = self.graph.compile(checkpointer=self.memory)
    
    def _create_graph(self):
        """Create the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("agent", self._call_model)
        workflow.add_node("tools", ToolNode(ALL_TOOLS))
        
        # Set entry point
        workflow.set_entry_point("agent")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "continue": "tools",
                "end": END
            }
        )
        
        # Add edge from tools back to agent
        workflow.add_edge("tools", "agent")
        
        return workflow
    
    def _call_model(self, state: AgentState):
        """Call the LLM with tools."""
        messages = state["messages"]
        
        # Add system message if not present
        if not any(isinstance(m, SystemMessage) for m in messages):
            system_msg = SystemMessage(content="""You are a helpful Value Engineering assistant for the Kushner Building 5 project.

You have access to data tools for:
- Apartment specifications and unit types
- Window and door schedules, counts, and costs
- Appliance specifications and costs
- RSMeans cost database
- Optimized alternatives with functional, design, and cost scores

When answering questions:
1. Use the appropriate data tools to get relevant information
2. Summarize the data clearly and concisely
3. Provide specific numbers, costs, and recommendations when asked
4. Be helpful and professional

Always cite which data source you used for your answer.""")
            messages = [system_msg] + list(messages)
        
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def _should_continue(self, state: AgentState):
        """Determine if we should continue or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        # If there are tool calls, continue
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "continue"
        
        # Otherwise end
        return "end"
    
    async def stream_response(self, message: str, thread_id: str = "default"):
        """Stream response token by token."""
        config = {"configurable": {"thread_id": thread_id}}
        
        # Invoke the agent
        async for event in self.app.astream_events(
            {"messages": [HumanMessage(content=message)]},
            config=config,
            version="v1"
        ):
            kind = event["event"]
            
            # Stream tokens from the LLM
            if kind == "on_chat_model_stream":
                content = event["data"]["chunk"].content
                if content:
                    yield content


def main():
    """Test the chat agent."""
    import asyncio
    
    async def test():
        agent = VEChatAgent()
        
        print("Testing VE Chat Agent...")
        print("="*60)
        
        question = "How many windows are in the project and what's the total cost?"
        print(f"\nQuestion: {question}\n")
        print("Response: ", end="", flush=True)
        
        async for token in agent.stream_response(question):
            print(token, end="", flush=True)
        
        print("\n\n✅ Agent test complete!")
    
    asyncio.run(test())


if __name__ == "__main__":
    main()

