#!/usr/bin/env python3
"""
Main examples runner for Mistral AI functionality tests.
This script provides a menu to select and run different example scripts.
"""

import os
import sys
import subprocess
from pathlib import Path


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def show_header():
    """Show the main header."""
    print("🚀 Mistral AI Examples Runner")
    print("=" * 60)
    print("Select an example to run:")
    print("-" * 60)


def get_available_examples():
    """Get list of available example scripts."""
    examples_dir = Path("src")
    examples = []

    for file in examples_dir.glob("*example*.py"):
        if file.name != "__init__.py":
            examples.append(file)

    return sorted(examples)


def show_menu(examples):
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

    print(f"{len(examples) + 1}. Run all examples")
    print(f"{len(examples) + 2}. Exit")
    print("-" * 60)


def run_example(example_path):
    """Run a specific example script."""
    print(f"\n🔄 Running {example_path.name}...")
    print("=" * 60)

    try:
        result = subprocess.run(
            [sys.executable, str(example_path)],
            cwd=Path.cwd(),
            capture_output=False,
            text=True,
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


def main():
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
            choice = input("\n📋 Enter your choice (1-{}): ".format(len(examples) + 2))

            if not choice.isdigit():
                print("❌ Please enter a valid number")
                continue

            choice_num = int(choice)

            if choice_num < 1 or choice_num > len(examples) + 2:
                print(f"❌ Please enter a number between 1 and {len(examples) + 2}")
                continue

            if choice_num == len(examples) + 1:  # Run all
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

            elif choice_num == len(examples) + 2:  # Exit
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
