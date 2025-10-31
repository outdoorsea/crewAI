#!/usr/bin/env python3
"""
run_http_client_tests.py - Comprehensive HTTP client test runner for CrewAI

This script runs comprehensive tests for all CrewAI HTTP client tools that communicate
with the Myndy-AI FastAPI backend, ensuring proper client-side functionality.

File: tests/run_http_client_tests.py
"""

import os
import sys
import json
import time
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Ensure project root is in path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("crewai.http_client_tests")


class CrewAIHTTPClientTestRunner:
    """
    Comprehensive test runner for CrewAI HTTP client tools
    
    Features:
    - Tests all HTTP client tools (memory, weather, time, shadow agent)
    - Tests bridge tools and FastAPI client
    - Performance and integration testing
    - Detailed reporting and analysis
    """
    
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # Test modules to run
        self.test_modules = [
            "test_http_client_tools",
            "test_myndy_bridge_tools"
        ]
        
    def run_pytest_module(self, module_name: str, test_mode: str = "unit") -> Dict[str, Any]:
        """
        Run pytest for a specific test module
        
        Args:
            module_name: Name of the test module to run
            test_mode: Test mode (unit, integration, performance, all)
        """
        logger.info(f"Running {module_name} in {test_mode} mode")
        
        # Build pytest command
        test_file = f"{module_name}.py"
        cmd = ["python", "-m", "pytest", test_file, "-v", "--tb=short"]
        
        # Add mode-specific markers
        if test_mode == "integration":
            cmd.extend(["-m", "integration"])
        elif test_mode == "performance":
            cmd.extend(["-m", "performance"])
        elif test_mode == "unit":
            cmd.extend(["-m", "not integration and not performance"])
        # "all" mode runs all tests without markers
        
        # Add JSON report generation
        json_report = f"{module_name}_{test_mode}_report.json"
        cmd.extend(["--json-report", f"--json-report-file={json_report}"])
        
        try:
            # Run pytest
            result = subprocess.run(
                cmd,
                cwd=Path(__file__).parent,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            # Parse results
            test_result = {
                "module": module_name,
                "mode": test_mode,
                "exit_code": result.returncode,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "duration_seconds": 0  # Will be updated if JSON report exists
            }
            
            # Try to load JSON report for detailed metrics
            json_report_path = Path(__file__).parent / json_report
            if json_report_path.exists():
                try:
                    with open(json_report_path, 'r') as f:
                        json_data = json.load(f)
                        test_result.update({
                            "tests_collected": json_data.get("summary", {}).get("collected", 0),
                            "tests_passed": len([t for t in json_data.get("tests", []) if t.get("outcome") == "passed"]),
                            "tests_failed": len([t for t in json_data.get("tests", []) if t.get("outcome") == "failed"]),
                            "tests_skipped": len([t for t in json_data.get("tests", []) if t.get("outcome") == "skipped"]),
                            "duration_seconds": json_data.get("summary", {}).get("duration", 0),
                            "detailed_results": json_data.get("tests", [])
                        })
                    
                    # Clean up JSON report
                    json_report_path.unlink()
                    
                except Exception as e:
                    logger.warning(f"Could not parse JSON report for {module_name}: {e}")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"Test module {module_name} timed out")
            return {
                "module": module_name,
                "mode": test_mode,
                "success": False,
                "error": "Test execution timed out",
                "exit_code": -1
            }
        except Exception as e:
            logger.error(f"Error running {module_name}: {e}")
            return {
                "module": module_name,
                "mode": test_mode,
                "success": False,
                "error": str(e),
                "exit_code": -1
            }
    
    def run_all_tests(self, test_mode: str = "all") -> Dict[str, Any]:
        """
        Run all HTTP client tests
        
        Args:
            test_mode: Test mode (unit, integration, performance, all)
        """
        self.start_time = time.time()
        
        logger.info(f"Starting CrewAI HTTP client tests in {test_mode} mode")
        logger.info(f"Test modules: {', '.join(self.test_modules)}")
        
        all_results = {}
        summary_stats = {
            "total_modules": len(self.test_modules),
            "modules_passed": 0,
            "modules_failed": 0,
            "total_tests": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_skipped": 0,
            "total_duration": 0
        }
        
        # Run each test module
        for module_name in self.test_modules:
            try:
                result = self.run_pytest_module(module_name, test_mode)
                all_results[module_name] = result
                
                # Update summary stats
                if result["success"]:
                    summary_stats["modules_passed"] += 1
                else:
                    summary_stats["modules_failed"] += 1
                
                # Add test-level stats if available
                summary_stats["total_tests"] += result.get("tests_collected", 0)
                summary_stats["tests_passed"] += result.get("tests_passed", 0)
                summary_stats["tests_failed"] += result.get("tests_failed", 0)
                summary_stats["tests_skipped"] += result.get("tests_skipped", 0)
                summary_stats["total_duration"] += result.get("duration_seconds", 0)
                
                # Log module result
                if result["success"]:
                    logger.info(f"✅ {module_name}: PASSED ({result.get('tests_passed', 0)} tests)")
                else:
                    logger.error(f"❌ {module_name}: FAILED (exit code {result['exit_code']})")
                    
            except Exception as e:
                logger.error(f"Exception running {module_name}: {e}")
                all_results[module_name] = {
                    "module": module_name,
                    "success": False,
                    "error": str(e)
                }
                summary_stats["modules_failed"] += 1
        
        self.end_time = time.time()
        total_duration = self.end_time - self.start_time
        
        # Create comprehensive results
        comprehensive_results = {
            "test_run_info": {
                "mode": test_mode,
                "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
                "end_time": datetime.fromtimestamp(self.end_time).isoformat(),
                "total_duration_seconds": total_duration,
                "python_version": sys.version,
                "working_directory": str(Path.cwd())
            },
            "summary": summary_stats,
            "module_results": all_results,
            "overall_success": summary_stats["modules_failed"] == 0
        }
        
        self.test_results = comprehensive_results
        
        # Log final summary
        success_rate = (summary_stats["tests_passed"] / max(summary_stats["total_tests"], 1)) * 100
        logger.info(f"🎯 Testing complete: {summary_stats['tests_passed']}/{summary_stats['total_tests']} tests passed ({success_rate:.1f}%)")
        logger.info(f"📊 Modules: {summary_stats['modules_passed']}/{summary_stats['total_modules']} passed")
        logger.info(f"⏱️  Total time: {total_duration:.2f} seconds")
        
        return comprehensive_results
    
    def run_specific_test_classes(self, test_classes: List[str]) -> Dict[str, Any]:
        """
        Run specific test classes
        
        Args:
            test_classes: List of test class names to run
        """
        logger.info(f"Running specific test classes: {', '.join(test_classes)}")
        
        results = {}
        
        for test_class in test_classes:
            try:
                # Build pytest command for specific class
                cmd = [
                    "python", "-m", "pytest",
                    "-v", "--tb=short",
                    f"-k", test_class
                ]
                
                result = subprocess.run(
                    cmd,
                    cwd=Path(__file__).parent,
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minute timeout per class
                )
                
                results[test_class] = {
                    "success": result.returncode == 0,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
                
                if result.returncode == 0:
                    logger.info(f"✅ {test_class}: PASSED")
                else:
                    logger.error(f"❌ {test_class}: FAILED")
                    
            except Exception as e:
                logger.error(f"Error running {test_class}: {e}")
                results[test_class] = {
                    "success": False,
                    "error": str(e)
                }
        
        return results
    
    def validate_test_environment(self) -> Dict[str, Any]:
        """
        Validate the test environment setup
        """
        logger.info("Validating test environment...")
        
        validation_results = {
            "python_version": sys.version,
            "pytest_available": False,
            "test_files_exist": {},
            "import_tests": {},
            "overall_valid": True
        }
        
        # Check pytest availability
        try:
            import pytest
            validation_results["pytest_available"] = True
            validation_results["pytest_version"] = pytest.__version__
        except ImportError:
            validation_results["pytest_available"] = False
            validation_results["overall_valid"] = False
            logger.error("❌ pytest is not available")
        
        # Check test files exist
        test_dir = Path(__file__).parent
        for module_name in self.test_modules:
            test_file = test_dir / f"{module_name}.py"
            exists = test_file.exists()
            validation_results["test_files_exist"][module_name] = exists
            if not exists:
                validation_results["overall_valid"] = False
                logger.error(f"❌ Test file not found: {test_file}")
            else:
                logger.info(f"✅ Test file found: {module_name}.py")
        
        # Test imports
        test_modules_to_import = [
            "tools.memory_http_tools",
            "tools.weather_http_tools", 
            "tools.time_http_tools",
            "tools.shadow_agent_http_tools"
        ]
        
        for module_name in test_modules_to_import:
            try:
                __import__(module_name)
                validation_results["import_tests"][module_name] = True
                logger.info(f"✅ Successfully imported {module_name}")
            except ImportError as e:
                validation_results["import_tests"][module_name] = False
                validation_results["overall_valid"] = False
                logger.error(f"❌ Could not import {module_name}: {e}")
        
        if validation_results["overall_valid"]:
            logger.info("✅ Test environment validation passed")
        else:
            logger.error("❌ Test environment validation failed")
        
        return validation_results
    
    def generate_html_report(self) -> str:
        """
        Generate an HTML test report
        """
        if not self.test_results:
            return "No test results available for HTML report"
        
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>CrewAI HTTP Client Test Report</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
                .summary { display: flex; justify-content: space-around; margin: 20px 0; }
                .metric { text-align: center; padding: 10px; background-color: #e8f4f8; border-radius: 5px; }
                .success { color: #28a745; }
                .failure { color: #dc3545; }
                .module { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
                .stdout { background-color: #f8f9fa; padding: 10px; border-radius: 3px; font-family: monospace; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="header">
                <h1>CrewAI HTTP Client Test Report</h1>
                <p><strong>Generated:</strong> {timestamp}</p>
                <p><strong>Mode:</strong> {mode}</p>
                <p><strong>Duration:</strong> {duration:.2f} seconds</p>
            </div>
            
            <div class="summary">
                <div class="metric">
                    <h3>Modules</h3>
                    <div class="success">{modules_passed} Passed</div>
                    <div class="failure">{modules_failed} Failed</div>
                </div>
                <div class="metric">
                    <h3>Tests</h3>
                    <div class="success">{tests_passed} Passed</div>
                    <div class="failure">{tests_failed} Failed</div>
                    <div>{tests_skipped} Skipped</div>
                </div>
                <div class="metric">
                    <h3>Success Rate</h3>
                    <div>{success_rate:.1f}%</div>
                </div>
            </div>
            
            <h2>Module Results</h2>
            {module_results_html}
            
        </body>
        </html>
        """
        
        # Build module results HTML
        module_results_html = ""
        for module_name, result in self.test_results["module_results"].items():
            status_class = "success" if result["success"] else "failure"
            status_text = "✅ PASSED" if result["success"] else "❌ FAILED"
            
            module_html = f"""
            <div class="module">
                <h3 class="{status_class}">{module_name} - {status_text}</h3>
                <p><strong>Tests:</strong> {result.get('tests_collected', 'N/A')} collected, 
                   {result.get('tests_passed', 0)} passed, {result.get('tests_failed', 0)} failed</p>
                <p><strong>Duration:</strong> {result.get('duration_seconds', 0):.2f} seconds</p>
                
                {f'<div class="stdout"><pre>{result["stdout"][:2000]}...</pre></div>' if result.get("stdout") else ''}
                {f'<div class="stdout"><strong>Error:</strong> {result["error"]}</div>' if result.get("error") else ''}
            </div>
            """
            module_results_html += module_html
        
        # Calculate metrics
        summary = self.test_results["summary"]
        success_rate = (summary["tests_passed"] / max(summary["total_tests"], 1)) * 100
        
        # Format HTML
        html_content = html_template.format(
            timestamp=datetime.now().isoformat(),
            mode=self.test_results["test_run_info"]["mode"],
            duration=self.test_results["test_run_info"]["total_duration_seconds"],
            modules_passed=summary["modules_passed"],
            modules_failed=summary["modules_failed"],
            tests_passed=summary["tests_passed"],
            tests_failed=summary["tests_failed"],
            tests_skipped=summary["tests_skipped"],
            success_rate=success_rate,
            module_results_html=module_results_html
        )
        
        return html_content
    
    def save_results(self, output_format: str = "json", filename: str = None) -> str:
        """
        Save test results to file
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"crewai_http_client_test_results_{timestamp}"
        
        if output_format == "json":
            filepath = Path(__file__).parent / f"{filename}.json"
            with open(filepath, 'w') as f:
                json.dump(self.test_results, f, indent=2, default=str)
        elif output_format == "html":
            filepath = Path(__file__).parent / f"{filename}.html"
            html_content = self.generate_html_report()
            with open(filepath, 'w') as f:
                f.write(html_content)
        
        logger.info(f"Results saved to: {filepath}")
        return str(filepath)


def main():
    """Main entry point for the test runner"""
    parser = argparse.ArgumentParser(description="CrewAI HTTP Client Test Runner")
    
    parser.add_argument(
        "--mode",
        choices=["unit", "integration", "performance", "all"],
        default="all",
        help="Test mode to run"
    )
    
    parser.add_argument(
        "--classes",
        nargs="*",
        help="Specific test classes to run"
    )
    
    parser.add_argument(
        "--output-format",
        choices=["json", "html"],
        default="json",
        help="Output format for results"
    )
    
    parser.add_argument(
        "--validate-env",
        action="store_true",
        help="Validate test environment before running tests"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create test runner
    runner = CrewAIHTTPClientTestRunner()
    
    try:
        # Validate environment if requested
        if args.validate_env:
            validation = runner.validate_test_environment()
            if not validation["overall_valid"]:
                logger.error("Environment validation failed!")
                return 1
        
        # Run tests
        if args.classes:
            # Run specific test classes
            results = runner.run_specific_test_classes(args.classes)
            logger.info(f"Specific test classes completed")
        else:
            # Run all tests
            results = runner.run_all_tests(args.mode)
        
        # Save results
        output_file = runner.save_results(args.output_format)
        
        # Determine exit code
        if hasattr(runner, 'test_results') and runner.test_results.get("overall_success"):
            logger.info("🎉 All tests passed!")
            return 0
        else:
            logger.error("💥 Some tests failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Test runner failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())