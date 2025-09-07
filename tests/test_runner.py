#!/usr/bin/env python3
"""
Simple test runner for Restaurant Menu Crawler tests
"""
import sys
import subprocess
import os


def run_tests():
    """Run all tests using pytest"""
    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    
    # Run pytest
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"]
    
    print("Running Restaurant Menu Crawler tests...")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 50)
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("All tests passed!")
        return 0
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 50)
        print(f"Tests failed with exit code {e.returncode}")
        return e.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install pytest:")
        print("pip install pytest")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
