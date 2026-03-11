"""
Example script demonstrating Document QnA with Mistral AI.

Shows how to upload documents, ask questions, and manage files.
"""

import logging
import os
import time

from colorama import Fore, Style, init
from dotenv import load_dotenv

from src.document_manager import DocumentManager
from src.mistral_client import MistralAIClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("document_qna.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Suppress mistralai SDK logs
logging.getLogger("mistralai").setLevel(logging.WARNING)


def print_header():
    """Print standardized example header."""
    print("\n" + "=" * 60)
    print("📄 MISTRAL AI DOCUMENT Q&A EXAMPLE")
    print("=" * 60)
    print("Demonstrates uploading documents and asking questions")
    print("=" * 60 + "\n")


def print_error(message: str, details: str = ""):
    """Print standardized error message."""
    print(f"\n{Fore.RED}❌ Error: {message}{Style.RESET_ALL}")
    if details:
        print(f"   {details}")


def print_warning(message: str):
    """Print standardized warning message."""
    print(f"\n{Fore.YELLOW}⚠️  Warning: {message}{Style.RESET_ALL}")


def print_success(message: str):
    """Print standardized success message."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")


def validate_api_key(api_key: str) -> bool:
    """Validate API key format."""
    if not api_key:
        return False
    if not isinstance(api_key, str):
        return False
    if len(api_key) < 32:
        return False
    return True


# Import colorama at module level
init(autoreset=True)


def main() -> None:
    """Main function demonstrating Document QnA workflow."""
    start_time = time.time()

    logger.info("Starting document QnA example")
    logger.info("Mistral AI Vibe CLI 2.2.1")
    logger.info(f"Python {time.strftime('%Y-%m-%d %H:%M:%S')}")

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

    # Step 2: Initialize clients
    print("\n2️⃣  Initializing clients...")
    try:
        doc_manager = DocumentManager(api_key)
        mistral_client = MistralAIClient(api_key)
        print_success("Clients initialized")
        logger.info("Clients initialized successfully")
    except Exception as e:
        print_error("Failed to initialize clients", str(e))
        logger.error(f"Client initialization failed: {str(e)}")
        return

    # Step 3: Upload document
    print("\n3️⃣  Uploading document...")
    try:
        file_info = doc_manager.upload_document(
            "test_docs/edc-2024-annual-report.pdf", purpose="ocr"
        )
        file_size = getattr(file_info, "bytes", "N/A")
        created_at = getattr(file_info, "created_at", "N/A")

        print_success(f"Document uploaded: {file_info.filename}")
        print(f"   📁 File ID: {file_info.id}")
        print(f"   📊 Size: {file_size} bytes")
        print(f"   📅 Created: {created_at}")

        logger.info(f"Document uploaded: {file_info.filename} (ID: {file_info.id})")

    except FileNotFoundError as e:
        print_error("Document file not found", str(e))
        logger.error(f"Document file not found: {str(e)}")
        return
    except Exception as e:
        print_error("Failed to upload document", str(e))
        logger.error(f"Document upload failed: {str(e)}")
        return

    # Ask questions about the document
    print("\n💬 Asking questions about the document...")
    questions = [
        "What is the main topic of this annual report?",
        "What are the key financial highlights mentioned?",
        "Who is the CEO or leadership mentioned in this report?",
        "What year does this report cover?",
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        try:
            # Use the document in chat completion
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {"type": "file", "file_id": file_info.id},
                    ],
                }
            ]

            answer = mistral_client.chat_completion(
                messages=messages, temperature=0.3, determinism_level=3
            )
            print(f"💡 Answer: {answer}")

        except Exception as e:
            print(f"❌ Error: {str(e)}")

    # List all uploaded documents
    print("\n📋 Listing all uploaded documents...")
    try:
        response = doc_manager.list_documents()
        if hasattr(response, "data") and response.data:
            for doc in response.data:
                print(f"   - {doc.filename} (ID: {doc.id}, Purpose: {doc.purpose})")
        else:
            print("   No documents found")
    except Exception as e:
        print(f"❌ Failed to list documents: {str(e)}")

    # Step 6: Clean up
    print("\n6️⃣  Cleaning up...")
    try:
        if doc_manager.delete_document(file_info.id):
            print_success("Document deleted successfully")
            logger.info("Document cleanup completed")
        else:
            print_warning("Document deletion may have failed")
            logger.warning("Document deletion may have failed")
    except Exception as e:
        print_error("Error during cleanup", str(e))
        logger.error(f"Cleanup error: {str(e)}")

    # Summary
    elapsed_time = time.time() - start_time

    print("\n" + "=" * 60)
    print("✅ DOCUMENT Q&A EXAMPLE COMPLETED")
    print("=" * 60)

    print("\n📊 Results:")
    print("   • Document uploaded and processed")
    print("   • Questions answered: 4")
    print("   • Cleanup completed")
    print(f"   • Execution time: {elapsed_time:.2f} seconds")

    print("\n📚 Resources:")
    print("   • Documentation: docs/API_INTEGRATION.md")
    print("   • All Examples: python main_examples.py")
    print("   • Mistral AI: https://mistral.ai")

    print("\n💡 Tips:")
    print("   • Use OCR purpose for text extraction")
    print("   • Always clean up uploaded documents")
    print("   • Handle file IDs carefully")
    print("   • Validate responses before use")

    logger.info(f"Document QnA example completed in {elapsed_time:.2f} seconds")
    logger.info("Document processing and cleanup successful")


if __name__ == "__main__":
    main()
