#!/usr/bin/env python3
"""
Debug script to test the test execution functionality.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_pytest_execution():
    """Test pytest execution with proper environment."""
    print("🧪 Testing pytest execution...")
    print("=" * 60)
    
    try:
        # Set up environment for running pytest
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")
        
        print(f"Current working directory: {Path.cwd()}")
        print(f"PYTHONPATH set to: {env['PYTHONPATH']}")
        print(f"Python executable: {sys.executable}")
        
        # Run pytest with coverage
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing"],
            cwd=Path.cwd(),
            capture_output=False,
            text=True,
            env=env,
        )

        print(f"\nPytest return code: {result.returncode}")
        
        if result.returncode == 0:
            print("\n✅ Pytest execution successful")
            return True
        else:
            print(f"\n❌ Pytest execution failed")
            return False

    except Exception as e:
        print(f"\n❌ Exception during pytest execution: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_pytest_execution()
    sys.exit(0 if success else 1)