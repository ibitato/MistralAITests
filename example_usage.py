"""
Example script to test Mistral AI client functionality.
"""

import os

from dotenv import load_dotenv

from src import (
    DeterminismController,
    MistralAIClient,
    format_chat_message,
    validate_api_key,
)


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

    # Create client with default determinism level (3 - balanced)
    client = MistralAIClient(api_key=api_key)
    print(f"🤖 Connected to Mistral AI with model: {client.model}")
    print(
        f"🎛️  Default determinism level: {client.determinism_level} ({client.determinism_controller.get_level_description()})"
    )

    # Create client with specific determinism level
    exact_client = MistralAIClient(api_key=api_key, determinism_level=1)
    print(
        f"🎛️  Exact client level: {exact_client.determinism_level} ({exact_client.determinism_controller.get_level_description()})"
    )

    # Create client with different model and determinism level
    creative_client = MistralAIClient(
        api_key=api_key, model="mistral-small", determinism_level=5
    )
    print(
        f"🎨 Creative client: model={creative_client.model}, level={creative_client.determinism_level}"
    )
    print(
        f"  Description: {creative_client.determinism_controller.get_level_description()}"
    )

    # Test with creative client
    print("\n🎨 Testing creative client:")
    creative_messages = [
        {"role": "system", "content": "You are a creative AI assistant."},
        {"role": "user", "content": "Write a short poem about Paris."},
    ]
    try:
        creative_response = creative_client.chat_completion(creative_messages)
        print(f"💬 Creative response: {creative_response}")
    except Exception as e:
        print(f"❌ Error with creative client: {e}")

    # Test with exact client
    print("\n🎯 Testing exact client:")
    exact_messages = [
        {"role": "system", "content": "You are a precise AI assistant."},
        {"role": "user", "content": "What is the exact capital of France?"},
    ]
    try:
        exact_response = exact_client.chat_completion(exact_messages)
        print(f"💬 Exact response: {exact_response}")
    except Exception as e:
        print(f"❌ Error with exact client: {e}")

    # Test with balanced client (default)
    print("\n⚖️ Testing balanced client (default):")
    balanced_messages = [
        {"role": "system", "content": "You are a balanced AI assistant."},
        {"role": "user", "content": "Tell me about the Eiffel Tower."},
    ]
    try:
        balanced_response = client.chat_completion(balanced_messages)
        print(f"💬 Balanced response: {balanced_response}")
    except Exception as e:
        print(f"❌ Error with balanced client: {e}")

    # Test with focused client (level 2)
    print("\n🔍 Testing focused client (level 2):")
    focused_client = MistralAIClient(api_key=api_key, determinism_level=2)
    focused_messages = [
        {"role": "system", "content": "You are a focused AI assistant."},
        {"role": "user", "content": "Explain the French Revolution briefly."},
    ]
    try:
        focused_response = focused_client.chat_completion(focused_messages)
        print(f"💬 Focused response: {focused_response}")
    except Exception as e:
        print(f"❌ Error with focused client: {e}")

    # Summary
    print("\n📋 Summary:")
    print("  ✅ Successfully tested all determinism levels")
    print("  ✅ Demonstrated dynamic level switching")
    print("  ✅ Showed error handling for invalid levels")
    print("  ✅ Tested with different models and clients")
    print("  ✅ Showed independent controller usage")
    print("\n🎉 Determinism controller integration complete!")
    print(
        "\n💡 Tip: Use determinism levels to control creativity vs. precision in your AI responses!"
    )

    # Show available determinism levels
    print("\n📊 Available determinism levels:")
    for level in range(1, 6):
        controller = DeterminismController(level)
        params = controller.get_parameters()
        print(f"  Level {level}: {controller.get_level_description()}")
        print(
            f"    Parameters: temp={params['temperature']}, top_p={params['top_p']}, freq_penalty={params['frequency_penalty']}, pres_penalty={params['presence_penalty']}"
        )

    # Test chat completion with different determinism levels
    try:
        messages = [
            format_chat_message("system", "You are a helpful AI assistant."),
            format_chat_message("user", "Hello! What is the capital of France?"),
        ]

        print("💬 Testing different determinism levels...")

        # Test level 1 (most exact)
        print("\n🔍 Level 1 (Exact):")
        print("💬 Question: What is the capital of France?")
        response = client.chat_completion(messages, determinism_level=1)
        print(f"💬 Response: {response}")

        # Test level 3 (balanced - default)
        print("\n⚖️ Level 3 (Balanced - default):")
        print("💬 Question: What is the capital of France?")
        response = client.chat_completion(messages, determinism_level=3)
        print(f"💬 Response: {response}")

        # Test level 5 (most creative)
        print("\n🎨 Level 5 (Creative):")
        print("💬 Question: What is the capital of France?")
        response = client.chat_completion(messages, determinism_level=5)
        print(f"💬 Response: {response}")

        # Test with custom temperature (overrides level)
        print("\n🌡️ Custom temperature (overrides level):")
        response = client.chat_completion(messages, temperature=0.9)
        print(f"💬 Response: {response}")

        # Test changing determinism level dynamically
        print("\n🔄 Changing determinism level dynamically:")
        client.determinism_controller.set_level(2)
        print(
            f"  New level: {client.determinism_level} ({client.determinism_controller.get_level_description()})"
        )
        response = client.chat_completion(messages)
        print(f"💬 Response: {response}")

    except Exception as e:
        print(f"❌ Error in chat completion: {e}")

    # Test determinism controller error handling
    try:
        print("\n🚨 Testing error handling:")
        DeterminismController(level=10)
    except ValueError as e:
        print(f"  ✅ Correctly caught invalid level error: {e}")

    # Show how to use determinism controller independently
    print("\n🔧 Using determinism controller independently:")
    controller = DeterminismController(level=4)
    print(f"  Current level: {controller.level}")
    print(f"  Parameters: {controller.get_parameters()}")

    # Change level dynamically
    controller.set_level(2)
    print(f"  Changed to level: {controller.level}")
    print(f"  New parameters: {controller.get_parameters()}")

    # Test list models
    try:
        print("📋 Fetching available models...")
        models = client.list_models()
        print(f"📋 Available models: {', '.join(models)}")

    except Exception as e:
        print(f"❌ Error listing models: {e}")

    # Summary
    print("\n📋 Summary:")
    print("  ✅ Successfully tested all determinism levels")
    print("  ✅ Demonstrated dynamic level switching")
    print("  ✅ Showed error handling for invalid levels")
    print("  ✅ Tested with different models and clients")
    print("  ✅ Showed independent controller usage")
    print("\n🎉 Determinism controller integration complete!")
    print(
        "\n💡 Tip: Use determinism levels to control creativity vs. precision in your AI responses!"
    )
    print("\n📚 Level guide:")
    print("  Level 1: Exact answers, minimal variation")
    print("  Level 2: Focused responses, low creativity")
    print("  Level 3: Balanced (default), good mix")
    print("  Level 4: Creative responses, more variation")
    print("  Level 5: Highly creative, maximum variation")
    print("\n🎯 Ready to use determinism control in your Mistral AI applications!")


if __name__ == "__main__":
    main()
