#!/usr/bin/env python3
"""
Test runner script for the ShopTrack backend application.
This script provides various options for running tests with different configurations.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False


def run_unit_tests():
    """Run unit tests only"""
    command = "python -m pytest tests/test_models/ tests/test_services/ tests/test_repositories/ -v"
    return run_command(command, "Unit Tests")


def run_controller_tests():
    """Run controller tests only"""
    command = "python -m pytest tests/test_controllers/ -v"
    return run_command(command, "Controller Tests")


def run_integration_tests():
    """Run integration tests only"""
    command = "python -m pytest tests/test_integration/ -v"
    return run_command(command, "Integration Tests")


def run_all_tests():
    """Run all tests"""
    command = "python -m pytest tests/ -v"
    return run_command(command, "All Tests")


def run_tests_with_coverage():
    """Run tests with coverage report"""
    command = "python -m pytest tests/ --cov=shoptrack --cov-report=html --cov-report=term-missing -v"
    return run_command(command, "Tests with Coverage")


def run_specific_test(test_path):
    """Run a specific test file or test function"""
    command = f"python -m pytest {test_path} -v"
    return run_command(command, f"Specific Test: {test_path}")


def run_tests_with_markers(marker):
    """Run tests with specific markers"""
    command = f"python -m pytest tests/ -m {marker} -v"
    return run_command(command, f"Tests with marker: {marker}")


def run_fast_tests():
    """Run fast tests only (exclude slow tests)"""
    command = "python -m pytest tests/ -m 'not slow' -v"
    return run_command(command, "Fast Tests Only")


def lint_code():
    """Run code linting"""
    command = "python -m flake8 shoptrack/ tests/ --max-line-length=100 --ignore=E203,W503"
    return run_command(command, "Code Linting")


def format_code():
    """Format code with black"""
    command = "python -m black shoptrack/ tests/ --line-length=100"
    return run_command(command, "Code Formatting")


def check_imports():
    """Check for unused imports"""
    command = "python -m flake8 shoptrack/ tests/ --select=F401"
    return run_command(command, "Unused Imports Check")


def main():
    """Main function to handle command line arguments"""
    parser = argparse.ArgumentParser(description="ShopTrack Backend Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--controllers", action="store_true", help="Run controller tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--coverage", action="store_true", help="Run tests with coverage")
    parser.add_argument("--test", type=str, help="Run specific test file or function")
    parser.add_argument("--marker", type=str, help="Run tests with specific marker")
    parser.add_argument("--fast", action="store_true", help="Run fast tests only")
    parser.add_argument("--lint", action="store_true", help="Run code linting")
    parser.add_argument("--format", action="store_true", help="Format code")
    parser.add_argument("--imports", action="store_true", help="Check for unused imports")
    parser.add_argument("--ci", action="store_true", help="Run CI pipeline (all checks)")
    
    args = parser.parse_args()
    
    # Set environment variables for testing
    os.environ['FLASK_ENV'] = 'testing'
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    
    success = True
    
    if args.ci:
        # Run full CI pipeline
        print("Running CI Pipeline...")
        success &= run_command("python -m pytest tests/ --cov=shoptrack --cov-report=xml --cov-fail-under=80", "Tests with Coverage")
        success &= lint_code()
        success &= check_imports()
        
    elif args.unit:
        success = run_unit_tests()
    elif args.controllers:
        success = run_controller_tests()
    elif args.integration:
        success = run_integration_tests()
    elif args.all:
        success = run_all_tests()
    elif args.coverage:
        success = run_tests_with_coverage()
    elif args.test:
        success = run_specific_test(args.test)
    elif args.marker:
        success = run_tests_with_markers(args.marker)
    elif args.fast:
        success = run_fast_tests()
    elif args.lint:
        success = lint_code()
    elif args.format:
        success = format_code()
    elif args.imports:
        success = check_imports()
    else:
        # Default: run all tests
        success = run_all_tests()
    
    if success:
        print(f"\n{'='*60}")
        print("✅ All operations completed successfully!")
        print(f"{'='*60}")
        sys.exit(0)
    else:
        print(f"\n{'='*60}")
        print("❌ Some operations failed!")
        print(f"{'='*60}")
        sys.exit(1)


if __name__ == "__main__":
    main()
