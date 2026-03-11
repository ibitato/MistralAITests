#!/usr/bin/env python3
"""
Script to verify all Python dependencies are installed.
"""

import sys
from pathlib import Path


def check_package(package_name: str) -> bool:
    """Check if a package is installed."""
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def main():
    """Main function to verify dependencies."""
    print("🔍 Verifying Python Dependencies")
    print("=" * 60)

    # Read requirements files
    requirements = []
    dev_requirements = []

    # Read main requirements
    req_file = Path("requirements.txt")
    if req_file.exists():
        with open(req_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    package = line.split(">=")[0].split("==")[0].strip()
                    requirements.append(package)

    # Read dev requirements
    dev_req_file = Path("requirements-dev.txt")
    if dev_req_file.exists():
        with open(dev_req_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    package = line.split(">=")[0].split("==")[0].strip()
                    dev_requirements.append(package)

    # Check main requirements
    print("\n📋 Main Requirements:")
    print("-" * 60)
    main_missing = []
    for package in requirements:
        if check_package(package):
            print(f"✅ {package}")
        else:
            print(f"❌ {package}")
            main_missing.append(package)

    # Check dev requirements
    print("\n📋 Development Requirements:")
    print("-" * 60)
    dev_missing = []
    for package in dev_requirements:
        if check_package(package):
            print(f"✅ {package}")
        else:
            print(f"❌ {package}")
            dev_missing.append(package)

    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)

    if not main_missing and not dev_missing:
        print("✅ All dependencies installed successfully!")
        print(f"   • Main requirements: {len(requirements)} packages")
        print(f"   • Dev requirements: {len(dev_requirements)} packages")
        return 0
    else:
        print("⚠️  Some dependencies are missing:")
        if main_missing:
            print(f"   • Main: {', '.join(main_missing)}")
        if dev_missing:
            print(f"   • Dev: {', '.join(dev_missing)}")

        print("\n💡 To install missing dependencies:")
        print("   pip install -r requirements.txt")
        print("   pip install -r requirements-dev.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
