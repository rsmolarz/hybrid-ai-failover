#!/usr/bin/env python3
"""
Example usage of the Hybrid AI Client
"""

from hybrid_ai_client import HybridAIClient, APIProvider

def main():
      # Initialize the client with Claude as primary
      client = HybridAIClient(
                primary_provider=APIProvider.CLAUDE,
      )

    # Check available providers
      print("\n" + "="*70)
      print("HYBRID AI CLIENT - EXAMPLE USAGE")
      print("="*70)
      print("\nAvailable Providers:")
      status = client.get_status()
      for key, value in status.items():
                print(f"  {key}: {value}")

      # Example 1: Simple question
      print("\n" + "-"*70)
      print("EXAMPLE 1: Simple Question")
      print("-"*70)

    messages = [
              {"role": "user", "content": "What is 2+2?"}
    ]

    try:
              response, provider = client.call(messages)
              print(f"\nProvider used: {provider.value.upper()}")
              print(f"Response: {response}\n")
except RuntimeError as e:
          print(f"Error: {e}\n")

    # Example 2: More complex request
      print("-"*70)
    print("EXAMPLE 2: Code Review Request")
    print("-"*70)

    messages = [
              {
                            "role": "user",
                            "content": """Review this Python code and suggest improvements:

                            def add(x, y):
                                return x+y

                                Is it good code? Any improvements?"""
              }
    ]

    try:
              response, provider = client.call(messages, max_tokens=512)
              print(f"\nProvider used: {provider.value.upper()}")
              print(f"Response: {response}\n")
except RuntimeError as e:
          print(f"Error: {e}\n")

    # Example 3: Demonstrate fallback
      print("-"*70)
    print("EXAMPLE 3: Failover Capability")
    print("-"*70)
    print("If Claude fails or hits rate limits, OpenAI will be used automatically.")
    print("The client handles all failover logic transparently.\n")


if __name__ == "__main__":
      # Set environment variables before running:
      # export ANTHROPIC_API_KEY="your-claude-api-key"
      # export OPENAI_API_KEY="your-openai-api-key"

      main()
