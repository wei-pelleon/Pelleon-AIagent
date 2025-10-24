#!/usr/bin/env python3
"""
Simple script to test the VE chat agent with any question.

Usage:
    python3 test_chat.py
    
Or run directly:
    python3 test_chat.py "How many windows are needed?"
"""
import asyncio
from dotenv import load_dotenv
import sys

# Add agent to path_ch
sys.path.insert(0, 'agent')

load_dotenv()

from chat_agent_v2 import VEChatAgent


async def test_question(question: str):
    """Test a question with the chat agent."""
    agent = VEChatAgent()
    
    print(f"\n{'='*70}")
    print(f"Q: {question}")
    print(f"{'='*70}")
    print("A: ", end="", flush=True)
    
    async for token in agent.stream_response(question):
        print(token, end="", flush=True)
    
    print(f"\n{'='*70}\n")


def main():
    if len(sys.argv) > 1:
        # Use command line argument
        question = " ".join(sys.argv[1:])
    else:
        # Interactive mode
        print("\n🤖 VE Chat Agent - Test Interface")
        print("="*70)
        question = input("\nEnter your question: ")
    
    asyncio.run(test_question(question))


if __name__ == "__main__":
    main()


