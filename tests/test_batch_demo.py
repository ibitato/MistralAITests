"""
Test cases for batch processing demo functionality.
These tests validate the batch file creation and structure without requiring API calls.
"""

import json
import tempfile
from pathlib import Path

import pytest

from tests.test_batch_processing import create_batch_file


class TestBatchDemo:
    """Demo tests for batch processing functionality."""

    def test_batch_file_creation_demo(self):
        """Test batch file creation with demo data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_file = Path(temp_dir) / "demo_batch.jsonl"

            # Create batch file with 50 requests
            create_batch_file(str(batch_file), num_requests=50)

            # Verify file was created
            assert batch_file.exists()
            assert batch_file.stat().st_size > 0

            # Verify file has 50 lines
            with open(batch_file) as f:
                lines = f.readlines()
                assert len(lines) == 50

            # Verify each line is valid JSON with proper structure
            custom_ids = []
            for line in lines:
                request = json.loads(line)
                assert "custom_id" in request
                assert "body" in request
                assert "messages" in request["body"]
                assert len(request["body"]["messages"]) == 1
                assert request["body"]["messages"][0]["role"] == "user"

                # Check custom_id format and uniqueness
                assert request["custom_id"].startswith("request_")
                assert request["custom_id"] not in custom_ids
                custom_ids.append(request["custom_id"])

    def test_batch_file_content_validation(self):
        """Test content validation of batch file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_file = Path(temp_dir) / "content_batch.jsonl"

            # Create batch file
            create_batch_file(str(batch_file), num_requests=10)

            # Validate content
            with open(batch_file) as f:
                lines = f.readlines()

                # Check first request structure
                request1 = json.loads(lines[0])
                assert request1["custom_id"] == "request_01"
                assert request1["body"]["max_tokens"] == 60
                assert request1["body"]["temperature"] == 0.7
                assert "quantum computing" in request1["body"]["messages"][0]["content"]

                # Check last request
                request10 = json.loads(lines[9])
                assert request10["custom_id"] == "request_10"
                # The topic should be one of the valid topics from the list
                content = request10["body"]["messages"][0]["content"]
                assert "Explain" in content and "in a concise paragraph" in content

    def test_batch_file_jsonl_format(self):
        """Test that batch file follows proper JSONL format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_file = Path(temp_dir) / "format_batch.jsonl"

            # Create batch file
            create_batch_file(str(batch_file), num_requests=5)

            # Verify JSONL format
            with open(batch_file) as f:
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

    def test_custom_id_uniqueness_and_format(self):
        """Test that custom IDs are unique and properly formatted."""
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_file = Path(temp_dir) / "ids_batch.jsonl"

            # Create batch file with 25 requests
            create_batch_file(str(batch_file), num_requests=25)

            with open(batch_file) as f:
                lines = f.readlines()

                custom_ids = []
                for i, line in enumerate(lines):
                    request = json.loads(line)
                    custom_id = request["custom_id"]

                    # Check format (request_01, request_02, etc.)
                    expected_id = f"request_{i+1:02d}"
                    assert (
                        custom_id == expected_id
                    ), f"Expected {expected_id}, got {custom_id}"

                    # Check uniqueness
                    assert custom_id not in custom_ids
                    custom_ids.append(custom_id)

    def test_batch_file_with_test_data_directory(self):
        """Test creating batch file in test_data directory."""
        # Create test_data directory if it doesn't exist
        test_data_dir = Path("tests/test_data")
        test_data_dir.mkdir(exist_ok=True)

        batch_file = test_data_dir / "test_batch_demo.jsonl"

        try:
            # Create batch file
            create_batch_file(str(batch_file), num_requests=3)

            # Verify file was created in correct location
            assert batch_file.exists()
            assert batch_file.parent.name == "test_data"

            # Verify content
            with open(batch_file) as f:
                lines = f.readlines()
                assert len(lines) == 3

                # Clean up
                batch_file.unlink()

        except Exception as e:
            # Clean up in case of error
            if batch_file.exists():
                batch_file.unlink()
            raise e

    def test_batch_file_cleanup(self):
        """Test that batch files can be properly cleaned up."""
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_file = Path(temp_dir) / "cleanup_batch.jsonl"

            # Create and verify file exists
            create_batch_file(str(batch_file), num_requests=5)
            assert batch_file.exists()

            # Simulate cleanup
            batch_file.unlink()
            assert not batch_file.exists()

            # Verify directory is clean
            assert not list(Path(temp_dir).glob("*.jsonl"))

    def test_different_batch_sizes(self):
        """Test batch file creation with different sizes."""
        test_cases = [1, 5, 10, 25, 50]

        with tempfile.TemporaryDirectory() as temp_dir:
            for num_requests in test_cases:
                batch_file = Path(temp_dir) / f"batch_{num_requests}.jsonl"

                # Create batch file
                create_batch_file(str(batch_file), num_requests=num_requests)

                # Verify correct number of requests
                with open(batch_file) as f:
                    lines = f.readlines()
                    assert len(lines) == num_requests

                # Clean up
                batch_file.unlink()

    def test_batch_file_no_root_pollution(self):
        """Test that batch files don't pollute root directory."""
        # Verify no batch files in root
        root_batch_files = list(Path(".").glob("batch_*.jsonl"))
        assert not root_batch_files, f"Found batch files in root: {root_batch_files}"

        # Create file in temp directory instead
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_file = Path(temp_dir) / "safe_batch.jsonl"
            create_batch_file(str(batch_file), num_requests=5)

            # Verify it's in temp dir, not root
            assert batch_file.exists()
            assert str(batch_file).startswith(temp_dir)

            # Verify root is still clean
            root_batch_files_after = list(Path(".").glob("batch_*.jsonl"))
            assert not root_batch_files_after

    def test_batch_file_content_diversity(self):
        """Test that batch file contains diverse topics."""
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_file = Path(temp_dir) / "diverse_batch.jsonl"

            # Create batch file
            create_batch_file(str(batch_file), num_requests=10)

            # Check for diverse topics
            topics_found = set()
            with open(batch_file) as f:
                for line in f:
                    request = json.loads(line)
                    content = request["body"]["messages"][0]["content"]
                    # Extract topic (second word in content)
                    topic = content.split()[1]
                    topics_found.add(topic)

            # Should have multiple different topics
            assert len(topics_found) > 1, "Batch file should contain diverse topics"
            assert any(
                "quantum" in t for t in topics_found
            ), "Should include quantum computing"
            assert any("black" in t for t in topics_found), "Should include black holes"

    def test_batch_file_structure_consistency(self):
        """Test that all requests in batch file have consistent structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_file = Path(temp_dir) / "consistent_batch.jsonl"

            # Create batch file
            create_batch_file(str(batch_file), num_requests=8)

            # Check consistency
            with open(batch_file) as f:
                lines = f.readlines()

                # All should have same max_tokens and temperature
                for line in lines:
                    request = json.loads(line)
                    assert request["body"]["max_tokens"] == 60
                    assert request["body"]["temperature"] == 0.7
                    assert request["body"]["messages"][0]["role"] == "user"


class TestBatchIntegration:
    """Integration tests for batch processing."""

    def test_end_to_end_batch_workflow(self):
        """Test complete batch processing workflow without API."""
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_file = Path(temp_dir) / "workflow_batch.jsonl"

            # Step 1: Create batch file
            create_batch_file(str(batch_file), num_requests=5)
            assert batch_file.exists()

            # Step 2: Validate file
            with open(batch_file) as f:
                lines = f.readlines()
                assert len(lines) == 5

                # Validate each request
                for line in lines:
                    request = json.loads(line)
                    assert "custom_id" in request
                    assert "body" in request
                    assert "messages" in request["body"]

            # Step 3: Simulate processing (just validation)
            # In real scenario, this would upload to Mistral AI

            # Step 4: Cleanup
            batch_file.unlink()
            assert not batch_file.exists()

            # Verify directory is clean
            assert not list(Path(temp_dir).glob("*.jsonl"))

    def test_batch_file_in_test_data_directory(self):
        """Test using test_data directory for batch files."""
        # Ensure test_data directory exists
        test_data_dir = Path("tests/test_data")
        test_data_dir.mkdir(exist_ok=True)

        batch_file = test_data_dir / "integration_batch.jsonl"

        try:
            # Create batch file in test_data
            create_batch_file(str(batch_file), num_requests=3)

            # Verify location
            assert batch_file.exists()
            assert "test_data" in str(batch_file)

            # Verify content
            with open(batch_file) as f:
                lines = f.readlines()
                assert len(lines) == 3

            # Clean up
            batch_file.unlink()

        except Exception as e:
            # Clean up in case of error
            if batch_file.exists():
                batch_file.unlink()
            raise e
