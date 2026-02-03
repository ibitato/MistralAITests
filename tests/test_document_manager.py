"""
Test cases for DocumentManager class.

These tests verify the functionality of document upload, retrieval, and deletion
with Mistral AI's file API.
"""

from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.document_manager import DocumentManager


class TestDocumentManager:
    """Test cases for DocumentManager class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Mistral client."""
        with patch("src.document_manager.Mistral") as mock:
            yield mock

    def test_initialization_success(self, mock_client):
        """Test successful initialization with valid API key."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        manager = DocumentManager("valid_api_key")
        assert manager.client is not None
        mock_client.assert_called_once_with(api_key="valid_api_key")

    def test_initialization_failure(self):
        """Test initialization failure with invalid API key."""
        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            DocumentManager("")  # type: ignore

        with pytest.raises(ValueError, match="API key must be a non-empty string"):
            DocumentManager(None)  # type: ignore

    def test_upload_document_success(self, mock_client):
        """Test successful document upload."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_response.filename = "test.pdf"
        mock_response.id = "test_file_id"
        mock_instance.files.upload.return_value = mock_response

        # Create a temporary test file
        with patch("builtins.open", mock_open(read_data=b"test content")):
            with patch("os.path.exists", return_value=True):
                with patch("os.path.getsize", return_value=1024):
                    manager = DocumentManager("test_key")
                    result = manager.upload_document("test.pdf", "ocr")

        assert result.filename == "test.pdf"
        assert result.id == "test_file_id"
        mock_instance.files.upload.assert_called_once()

    def test_upload_document_file_not_found(self, mock_client):
        """Test document upload failure when file doesn't exist."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        with patch("os.path.exists", return_value=False):
            manager = DocumentManager("test_key")
            with pytest.raises(FileNotFoundError, match="File test.pdf does not exist"):
                manager.upload_document("test.pdf")

    def test_upload_document_too_large(self, mock_client):
        """Test document upload failure when file is too large."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        with patch("os.path.exists", return_value=True):
            with patch("os.path.getsize", return_value=600 * 1024 * 1024):  # 600 MB
                manager = DocumentManager("test_key")
                with pytest.raises(ValueError, match="File size exceeds maximum"):
                    manager.upload_document("test.pdf")

    def test_upload_document_invalid_purpose(self, mock_client):
        """Test document upload failure with invalid purpose."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        manager = DocumentManager("test_key")
        with patch("os.path.exists", return_value=True):
            with patch("os.path.getsize", return_value=1024):
                with pytest.raises(ValueError, match="Purpose must be one of"):
                    manager.upload_document("test.pdf", "invalid_purpose")  # type: ignore

    def test_list_documents_success(self, mock_client):
        """Test successful listing of documents."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_instance.files.list.return_value = mock_response

        manager = DocumentManager("test_key")
        result = manager.list_documents()

        assert result == mock_response
        mock_instance.files.list.assert_called_once()

    def test_get_document_info_success(self, mock_client):
        """Test successful retrieval of document information."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_response.id = "test_file_id"
        mock_response.filename = "test.pdf"
        mock_instance.files.retrieve.return_value = mock_response

        manager = DocumentManager("test_key")
        result = manager.get_document_info("test_file_id")

        assert result == mock_response
        mock_instance.files.retrieve.assert_called_once_with(file_id="test_file_id")

    def test_get_document_info_invalid_id(self, mock_client):
        """Test document info retrieval failure with invalid file ID."""
        manager = DocumentManager("test_key")
        with pytest.raises(ValueError, match="File ID must be a non-empty string"):
            manager.get_document_info("")

    def test_delete_document_success(self, mock_client):
        """Test successful document deletion."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_response.deleted = True
        mock_instance.files.delete.return_value = mock_response

        manager = DocumentManager("test_key")
        result = manager.delete_document("test_file_id")

        assert result is True
        mock_instance.files.delete.assert_called_once_with(file_id="test_file_id")

    def test_delete_document_invalid_id(self, mock_client):
        """Test document deletion failure with invalid file ID."""
        manager = DocumentManager("test_key")
        with pytest.raises(ValueError, match="File ID must be a non-empty string"):
            manager.delete_document("")

    def test_get_signed_url_success(self, mock_client):
        """Test successful generation of signed URL."""
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        # Mock response
        mock_response = MagicMock()
        mock_response.url = "https://signed.url/test.pdf"
        mock_instance.files.get_signed_url.return_value = mock_response

        manager = DocumentManager("test_key")
        result = manager.get_signed_url("test_file_id", 12)

        assert result == "https://signed.url/test.pdf"
        mock_instance.files.get_signed_url.assert_called_once_with(
            file_id="test_file_id", expiry=12
        )

    def test_get_signed_url_invalid_id(self, mock_client):
        """Test signed URL generation failure with invalid file ID."""
        manager = DocumentManager("test_key")
        with pytest.raises(ValueError, match="File ID must be a non-empty string"):
            manager.get_signed_url("")

    def test_get_signed_url_invalid_expiry(self, mock_client):
        """Test signed URL generation failure with invalid expiry hours."""
        manager = DocumentManager("test_key")
        with pytest.raises(
            ValueError, match="Expiry hours must be an integer between 1 and 24"
        ):
            manager.get_signed_url("test_file_id", 0)

        with pytest.raises(
            ValueError, match="Expiry hours must be an integer between 1 and 24"
        ):
            manager.get_signed_url("test_file_id", 25)


class TestDocumentManagerIntegration:
    """Integration tests for DocumentManager with real file operations."""

    def test_upload_real_file(self, tmp_path):
        """Test uploading a real file."""
        # Create a test PDF file
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"%PDF-1.4 test content")

        with patch("src.document_manager.Mistral") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            # Mock successful upload
            mock_response = MagicMock()
            mock_response.filename = "test.pdf"
            mock_response.id = "test_file_id"
            mock_instance.files.upload.return_value = mock_response

            manager = DocumentManager("test_key")
            result = manager.upload_document(str(test_file), "ocr")

            assert result.filename == "test.pdf"
            assert result.id == "test_file_id"

    def test_file_validation(self, tmp_path):
        """Test file validation logic."""
        # Create a large file (> 512MB)
        large_file = tmp_path / "large.pdf"

        with patch("src.document_manager.Mistral") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            manager = DocumentManager("test_key")

            # Test with large file
            with patch("os.path.exists", return_value=True):
                with patch("os.path.getsize", return_value=600 * 1024 * 1024):
                    with pytest.raises(ValueError, match="File size exceeds maximum"):
                        manager.upload_document(str(large_file))

    def test_document_lifecycle(self, tmp_path):
        """Test complete document lifecycle: upload, list, get info, delete."""
        # Create a test file
        test_file = tmp_path / "lifecycle.pdf"
        test_file.write_bytes(b"%PDF-1.4 lifecycle test")

        with patch("src.document_manager.Mistral") as mock_client:
            mock_instance = MagicMock()
            mock_client.return_value = mock_instance

            # Mock responses
            upload_response = MagicMock()
            upload_response.filename = "lifecycle.pdf"
            upload_response.id = "lifecycle_id"

            list_response = MagicMock()
            list_response.data = [upload_response]

            retrieve_response = MagicMock()
            retrieve_response.id = "lifecycle_id"
            retrieve_response.filename = "lifecycle.pdf"

            delete_response = MagicMock()
            delete_response.deleted = True

            mock_instance.files.upload.return_value = upload_response
            mock_instance.files.list.return_value = list_response
            mock_instance.files.retrieve.return_value = retrieve_response
            mock_instance.files.delete.return_value = delete_response

            manager = DocumentManager("test_key")

            # Test upload
            uploaded = manager.upload_document(str(test_file))
            assert uploaded.id == "lifecycle_id"

            # Test list
            documents = manager.list_documents()
            assert len(documents.data) == 1

            # Test get info
            info = manager.get_document_info("lifecycle_id")
            assert info.filename == "lifecycle.pdf"

            # Test delete
            deleted = manager.delete_document("lifecycle_id")
            assert deleted is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
