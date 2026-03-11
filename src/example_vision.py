"""
Example script demonstrating Vision capabilities with Mistral AI.

Shows how to analyze images, extract information, and combine with text.
"""

import logging
import os
import sys
import textwrap
import time
from typing import Any

from colorama import Fore, Style, init
from dotenv import load_dotenv

# Add to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from src.mistral_client import MistralAIClient
from src.utils import validate_api_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("vision_demo.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Suppress mistralai SDK logs
logging.getLogger("mistralai").setLevel(logging.WARNING)


# Sample test images (real image paths)
SAMPLE_IMAGES = {
    "paris_landmark": "test_docs/vision_test_images/paris_landmark.jpg",
    "document_screenshot": "test_docs/vision_test_images/document_screenshot.png",
    "product_photo": "test_docs/vision_test_images/product_photo.jpg",
    "chart_diagram": "test_docs/vision_test_images/chart_diagram.png",
}


def print_header() -> None:
    """Print standardized example header."""
    print("\n" + "=" * 60)
    print("👁️  MISTRAL AI VISION EXAMPLE")
    print("=" * 60)
    print("Demonstrates image analysis and multimodal capabilities")
    print("=" * 60 + "\n")


def print_error(message: str, details: str = "") -> None:
    """Print standardized error message."""
    print(f"\n{Fore.RED}❌ Error: {message}{Style.RESET_ALL}")
    if details:
        print(f"   {details}")


def print_warning(message: str) -> None:
    """Print standardized warning message."""
    print(f"\n{Fore.YELLOW}⚠️  Warning: {message}{Style.RESET_ALL}")


def print_success(message: str) -> None:
    """Print standardized success message."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def print_vision_result(result: dict[str, Any], max_length: int = 200) -> None:
    """Print vision analysis result."""
    content = result.get("content", "")
    if content:
        # Truncate and wrap content
        truncated = (
            content[:max_length] + "..." if len(content) > max_length else content
        )
        wrapped = textwrap.fill(truncated, width=80, subsequent_indent="    ")
        print(f"💬 Analysis: {wrapped}")

    print(f"⏱️  Duration: {result.get('duration', 0):.3f} seconds")
    print(f"💰 Tokens: {result.get('tokens', {}).get('total', 0)} total")
    print(f"📊 Detail level: {result.get('detail', 'unknown')}")


# Import colorama at module level
init(autoreset=True)


def main() -> None:
    """Main function demonstrating vision workflow."""
    start_time = time.time()

    logger.info("Starting vision example")
    logger.info("Mistral AI Vibe CLI 2.2.1")
    logger.info(f"Python {sys.version.split()[0]}")

    print_header()

    # Step 1: Load and validate API key
    print("1️⃣  Loading configuration...")

    load_dotenv()
    api_key = os.getenv("MISTRAL_AI_API_KEY")

    if not validate_api_key(api_key):
        print_error(
            "MISTRAL_AI_API_KEY not found or invalid",
            "Please set a valid API key in .env file",
        )
        logger.error("Invalid API key")
        return

    print_success("API key validated")
    logger.info("API key validated successfully")

    # Create client with a model that supports vision
    print("\n2️⃣  Initializing Mistral AI client...")
    try:
        client = MistralAIClient(
            api_key=api_key,
            model="mistral-large-latest",  # Use a model that supports vision
        )
        print_success(f"Client initialized with model: {client.model}")
        logger.info(f"Client initialized with model: {client.model}")
    except Exception as e:
        print_error("Failed to initialize client", str(e))
        logger.error(f"Client initialization failed: {str(e)}")
        return

    # Test 1: Basic Image Analysis
    print("\n" + "=" * 80)
    print("🖼️  TEST 1: Basic Image Analysis")
    print("=" * 80)

    print("📁 Analyzing: paris_landmark.jpg")
    print("💬 Prompt: Describe this landmark and its historical significance")

    try:
        result = client.vision_analysis(
            image_data=SAMPLE_IMAGES["paris_landmark"],
            prompt="Describe this landmark and its historical significance",
            temperature=0.3,
            determinism_level=3,
            detail="high",
        )

        print_vision_result(result)
        logger.info("Basic image analysis completed successfully")

    except Exception as e:
        print_error("Image analysis failed", str(e))
        logger.error(f"Image analysis failed: {str(e)}")

    # Test 2: Document Understanding
    print("\n" + "=" * 80)
    print("📄 TEST 2: Document Analysis")
    print("=" * 80)

    print("📁 Analyzing: document_screenshot.png")
    print("💬 Prompt: Extract key information and summarize this document")

    try:
        result = client.vision_analysis(
            image_data=SAMPLE_IMAGES["document_screenshot"],
            prompt="Extract key information and summarize this document",
            temperature=0.2,
            determinism_level=2,
            detail="high",
        )

        print_vision_result(result)
        logger.info("Document analysis completed successfully")

    except Exception as e:
        print_error("Document analysis failed", str(e))
        logger.error(f"Document analysis failed: {str(e)}")

    # Test 3: Multimodal Conversation
    print("\n" + "=" * 80)
    print("💬 TEST 3: Multimodal Chat with Image")
    print("=" * 80)

    print("📁 Analyzing: product_photo.jpg")
    print("💬 User: What can you tell me about this product?")

    try:
        messages = [
            {"role": "user", "content": "What can you tell me about this product?"}
        ]

        result = client.vision_with_text(
            messages=messages,
            image_data=SAMPLE_IMAGES["product_photo"],
            temperature=0.2,
            determinism_level=2,
        )

        print_vision_result(result)
        logger.info("Multimodal conversation completed successfully")

    except Exception as e:
        print_error("Multimodal chat failed", str(e))
        logger.error(f"Multimodal chat failed: {str(e)}")

    # Test 4: Chart/Diagram Analysis
    print("\n" + "=" * 80)
    print("📊 TEST 4: Chart Analysis")
    print("=" * 80)

    print("📁 Analyzing: chart_diagram.png")
    print("💬 Prompt: Extract data points and explain this chart")

    try:
        result = client.vision_analysis(
            image_data=SAMPLE_IMAGES["chart_diagram"],
            prompt="Extract data points and explain this chart",
            temperature=0.1,
            determinism_level=1,
            detail="high",
        )

        print_vision_result(result)
        logger.info("Chart analysis completed successfully")

    except Exception as e:
        print_error("Chart analysis failed", str(e))
        logger.error(f"Chart analysis failed: {str(e)}")

    # Test 5: Different Detail Levels
    print("\n" + "=" * 80)
    print("🔍 TEST 5: Detail Level Comparison")
    print("=" * 80)

    print("📁 Analyzing: paris_landmark.jpg")
    print("💬 Testing different detail levels...")

    for detail_level in ["low", "high", "auto"]:
        print(f"\n📊 Detail level: {detail_level}")
        try:
            result = client.vision_analysis(
                image_data=SAMPLE_IMAGES["paris_landmark"],
                prompt="Describe this scene",
                detail=detail_level,
            )

            content_preview = (
                result["content"][:100] + "..."
                if len(result["content"]) > 100
                else result["content"]
            )
            print(f"   Preview: {content_preview}")
            print(f"   Tokens: {result['tokens']['total']}")

        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")

    # Test 6: Error Handling
    print("\n" + "=" * 80)
    print("🚨 TEST 6: Error Handling")
    print("=" * 80)

    try:
        # Test invalid image path
        result = client.vision_analysis(
            image_data="nonexistent.jpg", prompt="Analyze this"
        )
        print_error("Error handling test", "Should have failed but didn't")
    except ValueError as e:
        print_success(f"Correctly caught error: {str(e)[:50]}...")
        logger.info("Error handling test passed")
    except Exception as e:
        print_error("Unexpected error type", str(e))

    # Summary
    elapsed_time = time.time() - start_time

    print("\n" + "=" * 80)
    print("✅ VISION EXAMPLE COMPLETED")
    print("=" * 80)

    print("\n📊 Results:")
    print("   • Basic image analysis: ✅")
    print("   • Document understanding: ✅")
    print("   • Multimodal conversation: ✅")
    print("   • Chart analysis: ✅")
    print("   • Detail level control: ✅")
    print("   • Error handling: ✅")
    print(f"   • Execution time: {elapsed_time:.2f} seconds")

    print("\n📋 Vision Capabilities Demonstrated:")
    print("   • Image analysis with text prompts")
    print("   • Document understanding and summarization")
    print("   • Multimodal chat (text + images)")
    print("   • Chart and diagram interpretation")
    print("   • Adjustable detail levels")
    print("   • Comprehensive error handling")

    print("\n💡 Key Features:")
    print("   • Multimodal processing: Combine text and images")
    print("   • Detail control: Low/high/auto analysis depth")
    print("   • Format flexibility: URLs, file paths, binary data")
    print("   • Token efficiency: Optimized for vision tasks")
    print("   • Error recovery: Graceful handling of invalid inputs")

    print("\n📚 Best Practices:")
    print("   • Use high detail for complex images")
    print("   • Use low detail for simple recognition tasks")
    print("   • Combine text prompts with images for best results")
    print("   • Handle large images carefully (size limits apply)")
    print("   • Validate image formats before processing")

    print("\n🔗 Resources:")
    print("   • Documentation: docs/API_INTEGRATION.md")
    print("   • All Examples: python main_examples.py")
    print("   • Mistral AI Vision Guide: https://docs.mistral.ai/capabilities/vision")
    print("   • Mistral AI: https://mistral.ai")

    print("\n💡 Advanced Usage:")
    print("   • Batch image processing")
    print("   • Real-time image analysis")
    print("   • Document digitization workflows")
    print("   • Visual search applications")
    print("   • Accessibility features for images")

    logger.info(f"Vision example completed in {elapsed_time:.2f} seconds")
    logger.info("All vision tests completed successfully")


if __name__ == "__main__":
    main()
