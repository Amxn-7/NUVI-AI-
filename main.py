"""
=============================================================================
NUVI – Intelligent AI Desktop Assistant
Main Application Entry Point
=============================================================================
Supports:
1. Interactive Desktop Pet GUI (Default): Double-click to speak, drag around.
2. Academic / CLI Mode (--cli): Direct interactive text terminal loop for 
   quick testing, presentation demonstration, and vivas.
=============================================================================
"""

import sys
from ui.widget import AssistantWidget
from commands.parser import parse_and_execute
from commands.llm import _load_dotenv


def run_cli():
    print("=" * 60)
    print("   NUVI – Intelligent AI Desktop Assistant [CLI Mode]")
    print("=" * 60)
    print("Type a command (e.g. 'open chrome', 'find my resume',")
    print("'analyze sample_marks.csv', 'what is machine learning').")
    print("Type 'exit' or 'quit' to close.\n")

    while True:
        try:
            user_input = input("NUVI > ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Goodbye from NUVI!")
                break
            response = parse_and_execute(user_input)
            print(f"\n{response}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting NUVI.")
            break


def main():
    _load_dotenv()

    # CLI mode argument check
    if "--cli" in sys.argv or "-c" in sys.argv:
        run_cli()
        return

    # Initialize the UI widget and pass the command parser as the callback
    widget = AssistantWidget(command_callback=parse_and_execute)
    
    # Run the application loop
    widget.run()


if __name__ == "__main__":
    main()
