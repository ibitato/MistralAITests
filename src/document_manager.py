"""
Document Manager Module for Mistral AI.

Handles file upload, retrieval, and deletion operations with Mistral AI's file API.
"""

import logging
import os
from typing import Any, Literal

from mistralai import Mistral

# Configure logging
logger = logging.getLogger(__name__)


class DocumentManager:
    """Manager for document operations with Mistral AI."""

    def __init__(self, api_key: str):
        """Initialize document manager with API key.

        Args:
            api_key: Mistral AI API key

        Raises:
            ValueError: If API key is empty or invalid
        """
        if not api_key or not isinstance(api_key, str):
            logger.error("Invalid API key provided")
            raise ValueError("API key must be a non-empty string")

        self.client = Mistral(api_key=api_key)
        logger.info("DocumentManager initialized successfully")

    def upload_document(
        self, file_path: str, purpose: Literal["ocr", "fine-tune", "batch"] = "ocr"
    ) -> Any:
        """Upload a document file to Mistral AI.

        Args:
            file_path: Path to the file to upload
            purpose: Purpose of the file ('ocr', 'fine-tune', 'batch')

        Returns:
            Response object with file information

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is too large or invalid purpose
            RuntimeError: If API request fails
        """
        # Validate file exists
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            raise FileNotFoundError(f"File {file_path} does not exist")

        # Validate file size
        file_size = os.path.getsize(file_path)
        max_size = 512 * 1024 * 1024  # 512 MB
        if file_size > max_size:
            logger.error(f"File too large: {file_size} bytes")
            raise ValueError(f"File size exceeds maximum of {max_size} bytes")

        # Validate purpose
        valid_purposes = ["ocr", "fine-tune", "batch"]
        if purpose not in valid_purposes:
            logger.error(f"Invalid purpose: {purpose}")
            raise ValueError(f"Purpose must be one of: {valid_purposes}")

        try:
            logger.info(f"Uploading file: {file_path} for purpose: {purpose}")

            with open(file_path, "rb") as file:
                upload_response = self.client.files.upload(
                    file={"file_name": os.path.basename(file_path), "content": file},
                    purpose=purpose,
                )

            logger.info(f"File uploaded successfully: {upload_response.filename}")
            return upload_response

        except Exception as e:
            logger.error(f"Failed to upload document: {str(e)}")
            raise RuntimeError(f"Failed to upload document: {str(e)}") from e

    def list_documents(self) -> Any:
        """List all uploaded documents.

        Returns:
            Response object containing list of documents

        Raises:
            RuntimeError: If API request fails
        """
        try:
            logger.info("Listing all uploaded documents")
            response = self.client.files.list()

            logger.info(f"Found documents: {response}")
            return response

        except Exception as e:
            logger.error(f"Failed to list documents: {str(e)}")
            raise RuntimeError(f"Failed to list documents: {str(e)}") from e

    def get_document_info(self, file_id: str) -> Any:
        """Get information about a specific document.

        Args:
            file_id: ID of the file to retrieve

        Returns:
            Response object with file information

        Raises:
            ValueError: If file_id is invalid
            RuntimeError: If API request fails or file not found
        """
        if not file_id or not isinstance(file_id, str):
            logger.error("Invalid file ID provided")
            raise ValueError("File ID must be a non-empty string")

        try:
            logger.info(f"Getting info for file: {file_id}")
            response = self.client.files.retrieve(file_id=file_id)

            logger.info(f"Retrieved info for file: {response}")
            return response

        except Exception as e:
            logger.error(f"Failed to get document info: {str(e)}")
            raise RuntimeError(f"Failed to get document info: {str(e)}") from e

    def delete_document(self, file_id: str) -> bool:
        """Delete a document from Mistral AI storage.

        Args:
            file_id: ID of the file to delete

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            ValueError: If file_id is invalid
            RuntimeError: If API request fails
        """
        if not file_id or not isinstance(file_id, str):
            logger.error("Invalid file ID provided")
            raise ValueError("File ID must be a non-empty string")

        try:
            logger.info(f"Deleting file: {file_id}")
            response = self.client.files.delete(file_id=file_id)

            logger.info(f"Delete response: {response}")
            # Check if deletion was successful
            return (
                getattr(response, "deleted", False)
                if hasattr(response, "deleted")
                else True
            )

        except Exception as e:
            logger.error(f"Failed to delete document: {str(e)}")
            raise RuntimeError(f"Failed to delete document: {str(e)}") from e

    def get_signed_url(self, file_id: str, expiry_hours: int = 24) -> str:
        """Get a signed URL for temporary access to a document.

        Args:
            file_id: ID of the file
            expiry_hours: Number of hours before URL expires (max 24)

        Returns:
            Signed URL string

        Raises:
            ValueError: If file_id is invalid or expiry_hours invalid
            RuntimeError: If API request fails
        """
        if not file_id or not isinstance(file_id, str):
            logger.error("Invalid file ID provided")
            raise ValueError("File ID must be a non-empty string")

        if not isinstance(expiry_hours, int) or expiry_hours <= 0 or expiry_hours > 24:
            logger.error(f"Invalid expiry hours: {expiry_hours}")
            raise ValueError("Expiry hours must be an integer between 1 and 24")

        try:
            logger.info(f"Getting signed URL for file: {file_id}")
            response = self.client.files.get_signed_url(
                file_id=file_id, expiry=expiry_hours
            )

            logger.info(f"Generated signed URL: {response}")
            # Extract URL from response
            if hasattr(response, "url"):
                return response.url
            elif isinstance(response, dict) and "url" in response:
                return response["url"]
            else:
                raise RuntimeError(f"Unexpected response format: {response}")

        except Exception as e:
            logger.error(f"Failed to get signed URL: {str(e)}")
            raise RuntimeError(f"Failed to get signed URL: {str(e)}") from e
