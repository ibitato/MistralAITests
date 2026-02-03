#!/usr/bin/env python3
"""
Main examples runner for Mistral AI functionality tests.
This script provides a menu to select and run different example scripts.
"""

import os
import subprocess
import sys
from pathlib import Path


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def show_header() -> None:
    """Show the main header."""
    print("🚀 Mistral AI Examples Runner")
    print("=" * 60)
    print("Select an example to run:")
    print("-" * 60)


def get_available_examples() -> list[Path]:
    """Get list of available example scripts."""
    examples_dir = Path("src")
    examples = []

    for file in examples_dir.glob("*example*.py"):
        if file.name != "__init__.py":
            examples.append(file)

    return sorted(examples)


def get_available_tests() -> list[Path]:
    """Get list of available test scripts."""
    test_dir = Path(".")
    tests = []

    for file in test_dir.glob("test_*.py"):
        if file.name != "__init__.py":
            tests.append(file)

    return sorted(tests)


def show_menu(examples: list[Path]) -> None:
    """Show the menu of available examples."""
    for i, example in enumerate(examples, 1):
        # Remove 'example_' prefix and '.py' suffix for display
        display_name = (
            example.name.replace("example_", "")
            .replace(".py", "")
            .replace("_", " ")
            .title()
        )
        print(f"{i}. {display_name}")

    # Add test options
    tests = get_available_tests()
    tests_dir = Path("tests")
    has_pytest_tests = tests_dir.exists() and any(tests_dir.glob("*.py"))

    if tests or has_pytest_tests:
        print(f"{len(examples) + 1}. Run all tests (pytest + individual scripts)")
        print(f"{len(examples) + 2}. Run all examples")
        print(f"{len(examples) + 3}. Exit")
    else:
        print(f"{len(examples) + 1}. Run all examples")
        print(f"{len(examples) + 2}. Exit")
    print("-" * 60)


def run_example(example_path: Path) -> None:
    """Run a specific example script."""
    print(f"\n🔄 Running {example_path.name}...")
    print("=" * 60)

    try:
        # Set up environment for running examples
        env = os.environ.copy()
        env["PYTHONPATH"] = str(Path.cwd())

        result = subprocess.run(
            [sys.executable, str(example_path)],
            cwd=Path.cwd(),
            capture_output=False,
            text=True,
            env=env,
        )

        if result.returncode == 0:
            print(f"\n✅ {example_path.name} completed successfully")
        else:
            print(
                f"\n❌ {example_path.name} failed with return code {result.returncode}"
            )

    except KeyboardInterrupt:
        print(f"\n⚠️  {example_path.name} interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running {example_path.name}: {e}")


def run_tests() -> None:
    """Run all available test scripts."""
    tests = get_available_tests()

    clear_screen()
    print("🧪 Running All Tests")
    print("=" * 60)

    # First run pytest tests if available
    tests_dir = Path("tests")
    if tests_dir.exists() and any(tests_dir.glob("*.py")):
        print("\n🔄 Running pytest tests...")
        print("=" * 60)

        try:
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path.cwd() / "src")

            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/",
                    "-v",
                    "--cov=src",
                    "--cov-report=term-missing",
                ],
                cwd=Path.cwd(),
                capture_output=False,
                text=True,
                env=env,
            )

            if result.returncode == 0:
                print("\n✅ All pytest tests passed successfully")
            else:
                print(
                    f"\n❌ Some pytest tests failed with return code {result.returncode}"
                )

        except KeyboardInterrupt:
            print("\n⚠️  Pytest tests interrupted by user")
            return
        except Exception as e:
            print(f"\n❌ Error running pytest tests: {e}")

        print("\n" + "=" * 60)
        input("Press Enter to continue to next test type...")
        clear_screen()

    # Then run individual test scripts
    if tests:
        print("🧪 Running Individual Test Scripts")
        print("=" * 60)

        for test in tests:
            print(f"\n🔄 Running {test.name}...")
            print("=" * 60)

            try:
                # Set up environment for running tests
                env = os.environ.copy()
                env["PYTHONPATH"] = str(Path.cwd() / "src")

                result = subprocess.run(
                    [sys.executable, str(test)],
                    cwd=Path.cwd(),
                    capture_output=False,
                    text=True,
                    env=env,
                )

                if result.returncode == 0:
                    print(f"\n✅ {test.name} completed successfully")
                else:
                    print(
                        f"\n❌ {test.name} failed with return code {result.returncode}"
                    )

            except KeyboardInterrupt:
                print(f"\n⚠️  {test.name} interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ Error running {test.name}: {e}")

            print("\n" + "=" * 60)
            input("Press Enter to continue to next test...")
            clear_screen()
    else:
        print("No individual test scripts found")

    print("🎉 All tests completed!")


def main() -> None:
    """Main function to run the examples menu."""
    clear_screen()
    show_header()

    examples = get_available_examples()

    if not examples:
        print("No examples found in src/ directory")
        print("Make sure example scripts start with 'example_' prefix")
        return

    show_menu(examples)

    while True:
        try:
            tests = get_available_tests()
            max_option = len(examples) + 3 if tests else len(examples) + 2
            choice = input(f"\n📋 Enter your choice (1-{max_option}): ")

            if not choice.isdigit():
                print("❌ Please enter a valid number")
                continue

            choice_num = int(choice)

            tests = get_available_tests()
            max_option = len(examples) + 3 if tests else len(examples) + 2

            if choice_num < 1 or choice_num > max_option:
                print(f"❌ Please enter a number between 1 and {max_option}")
                continue

            if tests and choice_num == len(examples) + 1:  # Run tests
                run_tests()
                clear_screen()
                show_header()
                show_menu(examples)
                continue

            elif choice_num == (
                len(examples) + 2 if tests else len(examples) + 1
            ):  # Run all
                clear_screen()
                print("🚀 Running All Examples")
                print("=" * 60)

                for example in examples:
                    run_example(example)
                    print("\n" + "=" * 60)
                    input("Press Enter to continue to next example...")
                    clear_screen()

                print("🎉 All examples completed!")
                break

            elif choice_num == (
                len(examples) + 3 if tests else len(examples) + 2
            ):  # Exit
                print("👋 Goodbye!")
                break

            else:  # Run specific example
                selected_example = examples[choice_num - 1]
                clear_screen()
                run_example(selected_example)
                print("\n" + "=" * 60)
                input("Press Enter to return to menu...")
                clear_screen()
                show_header()
                show_menu(examples)

        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
