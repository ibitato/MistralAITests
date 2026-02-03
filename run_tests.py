#!/usr/bin/env python3
"""
Script to run pytest tests with proper configuration.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_pytest_tests():
    """Run pytest tests with proper Python path configuration."""
    print("🧪 Running pytest tests...")
    print("=" * 60)
    
    try:
        # Set up environment for running pytest
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd() / "src")
        
        # Run pytest with coverage
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing"],
            cwd=Path.cwd(),
            capture_output=False,
            text=True,
            env=env,
        )

        if result.returncode == 0:
            print("\n✅ All pytest tests passed successfully")
            return True
        else:
            print(f"\n❌ Some pytest tests failed with return code {result.returncode}")
            return False

    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error running pytest tests: {e}")
        return False

if __name__ == "__main__":
    success = run_pytest_tests()
    sys.exit(0 if success else 1)