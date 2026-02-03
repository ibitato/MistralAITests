"""
Example script demonstrating Document QnA with uploaded files.

This script shows how to:
1. Upload a PDF document to Mistral AI
2. Ask questions about the document content
3. Clean up by deleting the uploaded file
"""

import os

from dotenv import load_dotenv

from src.document_manager import DocumentManager
from src.mistral_client import MistralAIClient


def main() -> None:
    """Main function demonstrating Document QnA workflow."""
    load_dotenv()
    api_key = os.getenv("MISTRAL_AI_API_KEY")

    if not api_key:
        print("❌ Error: MISTRAL_AI_API_KEY not found in environment variables")
        print("Please create a .env file with your API key")
        return

    print("🚀 Starting Document QnA Example")
    print("=" * 50)

    # Initialize clients
    print("🔧 Initializing clients...")
    doc_manager = DocumentManager(api_key)
    mistral_client = MistralAIClient(api_key)
    print("✅ Clients initialized")

    # Upload a document
    print("\n📁 Uploading document...")
    try:
        file_info = doc_manager.upload_document(
            "test_docs/edc-2024-annual-report.pdf", purpose="ocr"
        )
        print(f"✅ Document uploaded: {file_info.filename} (ID: {file_info.id})")
        print(f"   Size: {getattr(file_info, 'bytes', 'N/A')} bytes")
        print(f"   Created at: {getattr(file_info, 'created_at', 'N/A')}")

    except Exception as e:
        print(f"❌ Failed to upload document: {str(e)}")
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

    # Clean up
    print("\n🧹 Cleaning up...")
    try:
        if doc_manager.delete_document(file_info.id):
            print("✅ Document deleted successfully")
        else:
            print("❌ Failed to delete document")
    except Exception as e:
        print(f"❌ Error during cleanup: {str(e)}")

    print("\n🎉 Document QnA Example completed!")


if __name__ == "__main__":
    main()
