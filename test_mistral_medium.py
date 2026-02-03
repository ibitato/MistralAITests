#!/usr/bin/env python3
"""
Test script to verify if mistral-medium-latest model works correctly.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from mistralai import Mistral


def test_mistral_medium() -> bool:
    """Test mistral-medium-latest model directly."""
    print("🧪 Testing mistral-medium-latest model...")
    print("=" * 60)

    try:
        # Load environment variables
        load_dotenv()

        # Get API key
        api_key = os.environ.get("MISTRAL_AI_API_KEY")
        if not api_key:
            print("❌ MISTRAL_AI_API_KEY environment variable not found")
            print("💡 Make sure you have a .env file with MISTRAL_AI_API_KEY=your_key")
            return False

        print("✅ API key found")

        # Initialize client
        client = Mistral(api_key=api_key)
        print("✅ Mistral client initialized")

        # Test the model
        model = "mistral-large-latest"
        print(f"🔄 Testing model: {model}")

        from mistralai.models import UserMessage

        messages = [
            UserMessage(role="user", content="What is the best French cheese?"),
        ]

        chat_response = client.chat.complete(
            model=model,
            messages=messages,  # type: ignore
        )

        print("✅ Request completed successfully")

        # Check response
        if chat_response.choices and len(chat_response.choices) > 0:
            content = chat_response.choices[0].message.content
            if content:
                print(f"💬 Response: {content}")
                print("✅ Model is working correctly")
                return True
            else:
                print("⚠️  Empty response received")
                return False
        else:
            print("⚠️  No choices in response")
            return False

    except Exception as e:
        print(f"❌ Error testing model: {e}")
        print(f"💡 Error type: {type(e).__name__}")

        # Check if it's a model access error
        error_msg = str(e).lower()
        if (
            "access" in error_msg
            or "permission" in error_msg
            or "not found" in error_msg
        ):
            print("🔒 This might be a model access/permission issue")
        elif "timeout" in error_msg:
            print("⏱️  This might be a timeout issue")
        elif "rate limit" in error_msg:
            print("🔄 This might be a rate limit issue")

        return False


if __name__ == "__main__":
    success = test_mistral_medium()

    print("\n" + "=" * 60)
    if success:
        print("🎉 Test PASSED: mistral-medium-latest is working!")
        sys.exit(0)
    else:
        print("💥 Test FAILED: mistral-medium-latest is not working")
        print("💡 Try using mistral-tiny or mistral-small instead")
        sys.exit(1)
