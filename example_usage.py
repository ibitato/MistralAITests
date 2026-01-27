"""
Example script to test Mistral AI client functionality.
"""

import os

from dotenv import load_dotenv

from src.mistral_client import MistralAIClient
from src.utils import format_chat_message, validate_api_key


def main() -> None:
    """Main function to demonstrate Mistral AI client usage."""
    # Load environment variables
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("MISTRAL_AI_API_KEY")

    # Validate API key
    if not validate_api_key(api_key):
        print("❌ Invalid API key. Please check your .env file.")
        return

    print("✅ API key is valid")

    # Create client
    client = MistralAIClient(api_key=api_key)
    print(f"🤖 Connected to Mistral AI with model: {client.model}")

    # Test chat completion
    try:
        messages = [
            format_chat_message("system", "You are a helpful AI assistant."),
            format_chat_message("user", "Hello! What is the capital of France?"),
        ]

        print("💬 Sending chat request...")
        response = client.chat_completion(messages)
        print(f"💬 Response: {response}")

    except Exception as e:
        print(f"❌ Error in chat completion: {e}")

    # Test list models
    try:
        print("📋 Fetching available models...")
        models = client.list_models()
        print(f"📋 Available models: {', '.join(models)}")

    except Exception as e:
        print(f"❌ Error listing models: {e}")


if __name__ == "__main__":
    main()
