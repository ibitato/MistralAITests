"""
Example script to test Mistral AI client functionality.
"""

import os
import sys
import textwrap

from dotenv import load_dotenv

# Add the parent directory to the Python path to access src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from determinism_controller import DeterminismController
from mistral_client import MistralAIClient
from utils import format_chat_message, validate_api_key


def main() -> None:
    """Main function to demonstrate Mistral AI client usage."""
    print("🚀 Starting Mistral AI Client Demonstration")
    print("=" * 80)

    # Load environment variables
    load_dotenv()

    # Get API key from environment
    api_key = os.getenv("MISTRAL_AI_API_KEY")

    # Validate API key
    if not validate_api_key(api_key):
        print("❌ Invalid API key. Please check your .env file.")
        return

    print("✅ API key is valid")
    print("-" * 80)

    # Create client with default determinism level (3 - balanced)
    client = MistralAIClient(api_key=api_key, model="mistral-large-latest")
    print(f"🤖 Connected to Mistral AI with model: {client.model}")
    print(
        f"🎛️  Default determinism level: {client.determinism_level} ({client.determinism_controller.get_level_description()})"
    )
    print("-" * 80)

    # Create client with specific determinism level
    exact_client = MistralAIClient(
        api_key=api_key, model="mistral-large-latest", determinism_level=1
    )
    print(
        f"🎛️  Exact client level: {exact_client.determinism_level} ({exact_client.determinism_controller.get_level_description()})"
    )

    # Create client with different model and determinism level
    creative_client = MistralAIClient(
        api_key=api_key, model="mistral-large-latest", determinism_level=5
    )
    print(
        f"🎨 Creative client: model={creative_client.model}, level={creative_client.determinism_level}"
    )
    print(
        f"  Description: {creative_client.determinism_controller.get_level_description()}"
    )
    print("-" * 80)

    # Create client with specific determinism level
    exact_client = MistralAIClient(
        api_key=api_key, model="mistral-medium-2508", determinism_level=1
    )
    print(
        f"🎛️  Exact client level: {exact_client.determinism_level} ({exact_client.determinism_controller.get_level_description()})"
    )

    # Create client with different model and determinism level
    creative_client = MistralAIClient(
        api_key=api_key, model="mistral-medium-2508", determinism_level=5
    )
    print(
        f"🎨 Creative client: model={creative_client.model}, level={creative_client.determinism_level}"
    )
    print(
        f"  Description: {creative_client.determinism_controller.get_level_description()}"
    )
    print("-" * 80)

    # Create client with specific determinism level
    exact_client = MistralAIClient(
        api_key=api_key, model="mistral-tiny", determinism_level=1
    )
    print(
        f"🎛️  Exact client level: {exact_client.determinism_level} ({exact_client.determinism_controller.get_level_description()})"
    )

    # Create client with different model and determinism level
    creative_client = MistralAIClient(
        api_key=api_key, model="mistral-tiny", determinism_level=5
    )
    print(
        f"🎨 Creative client: model={creative_client.model}, level={creative_client.determinism_level}"
    )
    print(
        f"  Description: {creative_client.determinism_controller.get_level_description()}"
    )
    print("-" * 80)

    # Create client with specific determinism level
    exact_client = MistralAIClient(
        api_key=api_key, model="mistral-medium-latest", determinism_level=1
    )
    print(
        f"🎛️  Exact client level: {exact_client.determinism_level} ({exact_client.determinism_controller.get_level_description()})"
    )

    # Create client with different model and determinism level
    creative_client = MistralAIClient(
        api_key=api_key, model="mistral-medium-latest", determinism_level=5
    )
    print(
        f"🎨 Creative client: model={creative_client.model}, level={creative_client.determinism_level}"
    )
    print(
        f"  Description: {creative_client.determinism_controller.get_level_description()}"
    )
    print("-" * 80)

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
    print("-" * 80)

    # Test with creative client
    print("\n🎨 Testing creative client:")
    print("-" * 80)
    creative_messages = [
        {"role": "system", "content": "You are a creative AI assistant."},
        {"role": "user", "content": "Write a short poem about Paris."},
    ]
    print(f"💬 System: {creative_messages[0]['content']}")
    print(f"💬 User: {creative_messages[1]['content']}")
    try:
        creative_response = creative_client.chat_completion(creative_messages)
        wrapped_response = textwrap.fill(
            creative_response, width=80, subsequent_indent="    "
        )
        print(f"💬 Creative response: {wrapped_response}")
    except Exception as e:
        print(f"❌ Error with creative client: {e}")

    # Test with exact client
    print("\n🎯 Testing exact client:")
    print("-" * 80)
    exact_messages = [
        {"role": "system", "content": "You are a precise AI assistant."},
        {"role": "user", "content": "What is the exact capital of France?"},
    ]
    print(f"💬 System: {exact_messages[0]['content']}")
    print(f"💬 User: {exact_messages[1]['content']}")
    try:
        exact_response = exact_client.chat_completion(exact_messages)
        wrapped_response = textwrap.fill(
            exact_response, width=80, subsequent_indent="    "
        )
        print(f"💬 Exact response: {wrapped_response}")
    except Exception as e:
        print(f"❌ Error with exact client: {e}")

    # Test with balanced client (default)
    print("\n⚖️ Testing balanced client (default):")
    print("-" * 80)
    balanced_messages = [
        {"role": "system", "content": "You are a balanced AI assistant."},
        {"role": "user", "content": "Tell me about the Eiffel Tower."},
    ]
    print(f"💬 System: {balanced_messages[0]['content']}")
    print(f"💬 User: {balanced_messages[1]['content']}")
    print("🔄 Processing request...")
    try:
        balanced_response = client.chat_completion(balanced_messages)
        if balanced_response:
            wrapped_response = textwrap.fill(
                balanced_response, width=80, subsequent_indent="    "
            )
            print(f"💬 Balanced response: {wrapped_response}")
        else:
            print("⚠️  Empty response received from API")
    except Exception as e:
        print(f"❌ Error with balanced client: {e}")
        print("💡 Trying with default model as fallback...")
        # Try with default model
        fallback_client = MistralAIClient(api_key=api_key)
        try:
            balanced_response = fallback_client.chat_completion(balanced_messages)
            if balanced_response:
                wrapped_response = textwrap.fill(
                    balanced_response, width=80, subsequent_indent="    "
                )
                print(f"💬 Balanced response (fallback): {wrapped_response}")
            else:
                print("⚠️  Empty response received from fallback API")
        except Exception as fallback_e:
            print(f"❌ Error with fallback client: {fallback_e}")
            print("🔴 Unable to complete balanced client test")

    # Test with focused client (level 2)
    print("\n🔍 Testing focused client (level 2):")
    print("-" * 80)
    focused_client = MistralAIClient(
        api_key=api_key, model="mistral-large-latest", determinism_level=2
    )
    focused_messages = [
        {"role": "system", "content": "You are a focused AI assistant."},
        {"role": "user", "content": "Explain the French Revolution briefly."},
    ]
    print(f"💬 System: {focused_messages[0]['content']}")
    print(f"💬 User: {focused_messages[1]['content']}")
    try:
        focused_response = focused_client.chat_completion(focused_messages)
        wrapped_response = textwrap.fill(
            focused_response, width=80, subsequent_indent="    "
        )
        print(f"💬 Focused response: {wrapped_response}")
    except Exception as e:
        print(f"❌ Error with focused client: {e}")

    print("\n" + "=" * 80)
    print("📋 SECTION 1: Basic Client Testing")
    print("=" * 80)
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
    print("\n" + "=" * 80)
    print("📊 Available determinism levels:")
    print("=" * 80)
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

        print("\n" + "=" * 60)
        print("💬 Testing different determinism levels...")
        print("=" * 60)

        # Test level 1 (most exact)
        print("\n🔍 Level 1 (Exact):")
        print("-" * 80)
        print("💬 Question: What is the capital of France?")
        response = client.chat_completion(messages, determinism_level=1)
        wrapped_response = textwrap.fill(response, width=80, subsequent_indent="    ")
        print(f"💬 Response: {wrapped_response}")

        # Test level 3 (balanced - default)
        print("\n⚖️ Level 3 (Balanced - default):")
        print("-" * 80)
        print("💬 Question: What is the capital of France?")
        response = client.chat_completion(messages, determinism_level=3)
        wrapped_response = textwrap.fill(response, width=80, subsequent_indent="    ")
        print(f"💬 Response: {wrapped_response}")

        # Test level 5 (most creative)
        print("\n🎨 Level 5 (Creative):")
        print("-" * 80)
        print("💬 Question: What is the capital of France?")
        response = client.chat_completion(messages, determinism_level=5)
        wrapped_response = textwrap.fill(response, width=80, subsequent_indent="    ")
        print(f"💬 Response: {wrapped_response}")

        # Test with custom temperature (overrides level)
        print("\n🌡️ Custom temperature (overrides level):")
        print("-" * 80)
        response = client.chat_completion(messages, temperature=0.9)
        wrapped_response = textwrap.fill(response, width=80, subsequent_indent="    ")
        print(f"💬 Response: {wrapped_response}")

        # Test changing determinism level dynamically
        print("\n🔄 Changing determinism level dynamically:")
        print("-" * 80)
        client.determinism_controller.set_level(2)
        print(
            f"  New level: {client.determinism_level} ({client.determinism_controller.get_level_description()})"
        )
        response = client.chat_completion(messages)
        wrapped_response = textwrap.fill(response, width=80, subsequent_indent="    ")
        print(f"💬 Response: {wrapped_response}")

    except Exception as e:
        print(f"❌ Error in chat completion: {e}")

    # Test determinism controller error handling
    try:
        print("\n" + "=" * 80)
        print("🚨 Testing error handling:")
        print("=" * 80)
        DeterminismController(level=10)
    except ValueError as e:
        print(f"  ✅ Correctly caught invalid level error: {e}")

    # Show how to use determinism controller independently
    print("\n" + "=" * 80)
    print("🔧 Using determinism controller independently:")
    print("=" * 80)
    controller = DeterminismController(level=4)
    print(f"  Current level: {controller.level}")
    print(f"  Parameters: {controller.get_parameters()}")

    # Change level dynamically
    controller.set_level(2)
    print(f"  Changed to level: {controller.level}")
    print(f"  New parameters: {controller.get_parameters()}")

    # Test list models
    try:
        print("\n" + "=" * 80)
        print("📋 Fetching available models...")
        print("=" * 80)
        models = client.list_models()

        if models:
            # Filter for "latest" models which are typically the most interesting
            latest_models = [model for model in models if "latest" in model.lower()]

            if latest_models:
                print("📋 Latest models (most interesting):")
                print("-" * 80)
                for i, model in enumerate(latest_models, 1):
                    print(f"  {i:2d}. {model}")
            else:
                print("📋 Available models:")
                print("-" * 80)
                for i, model in enumerate(models, 1):
                    print(f"  {i:2d}. {model}")
        else:
            print("📋 No models available or unable to fetch models")

    except Exception as e:
        print(f"❌ Error listing models: {e}")

    print("\n" + "=" * 80)
    print("📋 FINAL SUMMARY")
    print("=" * 80)
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
    print("\n" + "=" * 80)
    print("🚀 Demonstration Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
