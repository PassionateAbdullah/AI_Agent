"""
main.py

Entry point for a simple interactive console chat with the ScoutAgent.

Run this script using Python to interact with the agent in your
terminal.  It reads user input, routes the message through the
conversation handler and prints the agent's response.  The loop
terminates when the user types 'exit' or 'quit'.  For demonstration
purposes the agent returns formatted prompt templates rather than
calling a language model.
"""

import sys
from .handlers import ScoutAgent


def run_chat() -> None:
    agent = ScoutAgent()
    print("Welcome to the Scout agent demo. Type 'exit' to quit.")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break
        agent.add_message(role="user", content=user_input)
        response = agent.route_message(user_input)
        agent.add_message(role="assistant", content=response)
        print(f"Scout: {response}\n")


if __name__ == "__main__":
    run_chat()
