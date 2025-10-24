"""
Simplified chat agent using LangChain ReAct agent with streaming.
"""
import os
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from data_tools import ALL_TOOLS


class VEChatAgent:
    """Simplified Value Engineering Chat Agent."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('OPENAI_API_KEY')
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=self.api_key,
            streaming=True,
            temperature=0.7
        )
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful Value Engineering assistant for the Kushner Building 5 project.

You have access to data tools for apartments, windows, doors, appliances, and cost information.

When answering:
1. Use the appropriate tools to get data
2. Summarize clearly and provide specific numbers
3. Be concise and professional
4. Always cite your data source

Available data includes specifications, counts, costs, and optimized alternatives."""),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create agent
        agent = create_react_agent(self.llm, ALL_TOOLS, prompt)
        
        # Create executor
        self.executor = AgentExecutor(
            agent=agent,
            tools=ALL_TOOLS,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )
    
    async def stream_response(self, message: str, thread_id: str = "default"):
        """Stream response token by token."""
        try:
            # Use astream for streaming
            async for chunk in self.executor.astream(
                {"input": message},
                config={"run_name": thread_id}
            ):
                # Extract the output text
                if "output" in chunk:
                    output = chunk["output"]
                    # Yield the full output (we'll handle token splitting in frontend if needed)
                    yield output
                elif "actions" in chunk:
                    # Agent is thinking/using tools
                    pass
                elif "steps" in chunk:
                    # Agent executed a step
                    pass
        except Exception as e:
            yield f"Error: {str(e)}"


def main():
    """Test the chat agent."""
    import asyncio
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def test():
        agent = VEChatAgent()
        
        print("Testing VE Chat Agent...")
        print("="*60)
        
        question = "How many windows are in the project?"
        print(f"\nQuestion: {question}\n")
        print("Response: ")
        print("-"*60)
        
        async for response in agent.stream_response(question):
            print(response)
        
        print("-"*60)
        print("\n✅ Agent test complete!")
    
    asyncio.run(test())


if __name__ == "__main__":
    main()


