"""
Simple chat agent using OpenAI function calling with streaming.
"""
import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from data_tools import ALL_TOOLS


class VEChatAgent:
    """Simple VE Chat Agent with OpenAI tools."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=self.api_key,
            streaming=True,
            temperature=0
        )
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful Value Engineering assistant for Kushner Building 5. Answer questions about costs, materials, and specifications using the available tools."),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent with OpenAI tools
        agent = create_openai_tools_agent(self.llm, ALL_TOOLS, prompt)
        
        # Create executor  
        self.executor = AgentExecutor(
            agent=agent,
            tools=ALL_TOOLS,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
            return_intermediate_steps=False
        )
    
    async def stream_response(self, message: str, thread_id: str = "default"):
        """Stream response."""
        try:
            # Stream the response
            async for event in self.executor.astream_events(
                {"input": message},
                version="v1",
                config={"run_name": thread_id}
            ):
                kind = event["event"]
                
                # Stream LLM tokens
                if kind == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if content:
                        yield content
                        
        except Exception as e:
            yield f"\n\nError: {str(e)}"


def main():
    """Test the agent."""
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test():
        print("Testing Chat Agent...")
        agent = VEChatAgent()
        
        question = "How many windows are in the project?"
        print(f"\nQ: {question}\nA: ", end="", flush=True)
        
        async for token in agent.stream_response(question):
            print(token, end="", flush=True)
        
        print("\n\n✅ Done!")
    
    asyncio.run(test())


if __name__ == "__main__":
    main()

