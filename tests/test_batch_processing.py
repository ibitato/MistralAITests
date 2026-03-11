"""
Test cases for batch processing functionality.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.example_batch_processing import create_batch_file


class TestBatchProcessing:
    """Test cases for batch processing functionality."""

    def test_batch_file_creation(self):
        """Test that batch file is created correctly with 50 requests."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
            temp_file = f.name

        try:
            # Create batch file with 50 requests
            create_batch_file(temp_file, num_requests=50)

            # Verify file was created
            assert os.path.exists(temp_file)

            # Verify file has 50 lines
            with open(temp_file) as f:
                lines = f.readlines()
                assert len(lines) == 50

            # Verify each line is valid JSON
            with open(temp_file) as f:
                for line in f:
                    request = json.loads(line)
                    assert "custom_id" in request
                    assert "body" in request
                    assert "messages" in request["body"]
                    assert len(request["body"]["messages"]) == 1
                    assert request["body"]["messages"][0]["role"] == "user"

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_batch_file_content_structure(self):
        """Test the structure and content of batch file requests."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
            temp_file = f.name

        try:
            # Create batch file
            create_batch_file(temp_file, num_requests=3)

            # Read and verify content
            with open(temp_file) as f:
                lines = f.readlines()

                # Check first request structure
                request1 = json.loads(lines[0])
                assert request1["custom_id"] == "request_01"
                assert request1["body"]["max_tokens"] == 60
                assert request1["body"]["temperature"] == 0.7
                assert "quantum computing" in request1["body"]["messages"][0]["content"]

                # Check second request structure
                request2 = json.loads(lines[1])
                assert request2["custom_id"] == "request_02"
                assert "black holes" in request2["body"]["messages"][0]["content"]

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_batch_file_with_different_sizes(self):
        """Test batch file creation with different request counts."""
        test_cases = [1, 5, 10, 50]

        for num_requests in test_cases:
            with tempfile.NamedTemporaryFile(
                mode="w", delete=False, suffix=".jsonl"
            ) as f:
                temp_file = f.name

            try:
                # Create batch file
                create_batch_file(temp_file, num_requests=num_requests)

                # Verify correct number of requests
                with open(temp_file) as f:
                    lines = f.readlines()
                    assert len(lines) == num_requests

                    # Verify all custom_ids are unique and properly formatted
                    custom_ids = []
                    for line in lines:
                        request = json.loads(line)
                        custom_ids.append(request["custom_id"])

                    assert len(custom_ids) == len(set(custom_ids))  # All unique

            finally:
                # Clean up
                if os.path.exists(temp_file):
                    os.remove(temp_file)

    @patch("src.example_batch_processing.Mistral")
    @patch("src.example_batch_processing.requests.post")
    def test_submit_batch_job(self, mock_post, mock_mistral):
        """Test batch job submission."""
        # Create a mock client
        mock_client = MagicMock()
        mock_mistral.return_value = mock_client

        # Create a temporary batch file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
            temp_file = f.name
            f.write(
                '{"custom_id": "test_1", "body": {"messages": [{"role": "user", "content": "test"}]}}'
            )

        try:
            # Mock the HTTP response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "id": "batch_job_123",
                "status": "processing",
                "purpose": "batch",
            }
            mock_response.raise_for_status.return_value = None
            mock_post.return_value = mock_response

            # Import and test the function
            from src.example_batch_processing import submit_batch_job

            result = submit_batch_job(mock_client, temp_file, "test_api_key")

            # Verify the function was called correctly
            assert result["id"] == "batch_job_123"
            assert result["status"] == "processing"
            assert result["purpose"] == "batch"

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_batch_file_error_handling(self):
        """Test error handling in batch file creation."""
        # Test with invalid output path
        with pytest.raises((OSError, PermissionError)):
            # Try to write to a directory that doesn't exist
            create_batch_file("/nonexistent/directory/batch.jsonl")

    def test_custom_id_format(self):
        """Test that custom IDs are properly formatted with leading zeros."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
            temp_file = f.name

        try:
            # Create batch file with 15 requests to test formatting
            create_batch_file(temp_file, num_requests=15)

            with open(temp_file) as f:
                lines = f.readlines()

                # Check that custom IDs are properly formatted
                for i, line in enumerate(lines):
                    request = json.loads(line)
                    expected_id = f"request_{i+1:02d}"  # Should be 2-digit format
                    assert request["custom_id"] == expected_id

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_batch_file_jsonl_format(self):
        """Test that the batch file is in proper JSONL format."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
            temp_file = f.name

        try:
            # Create batch file
            create_batch_file(temp_file, num_requests=5)

            # Verify it's valid JSONL (each line is valid JSON)
            with open(temp_file) as f:
                for line_number, line in enumerate(f, 1):
                    # Should not be empty
                    assert line.strip(), f"Line {line_number} is empty"

                    # Should be valid JSON
                    try:
                        json.loads(line)
                    except json.JSONDecodeError as e:
                        pytest.fail(f"Line {line_number} is not valid JSON: {str(e)}")

                    # Should end with newline
                    assert line.endswith(
                        "\n"
                    ), f"Line {line_number} doesn't end with newline"

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
