#!/usr/bin/env python3
"""
Management script for the MetroGrub Model Pipeline Cloud Function and Scheduler.
Provides utilities for testing, monitoring, and managing the deployment.
"""

import json
import argparse
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any

# Configuration
PROJECT_ID = "purple-25-gradient-20250605"
REGION = "us-central1"
FUNCTION_NAME = "metrogrub-model-pipeline"
SCHEDULER_JOB_NAME = "metrogrub-pipeline-scheduler"

def run_command(cmd: str, capture_output: bool = True) -> subprocess.CompletedProcess:
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=capture_output, 
            text=True,
            check=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {cmd}")
        print(f"Error: {e.stderr}")
        sys.exit(1)

def test_function():
    """Test the cloud function with a test payload."""
    print("🧪 Testing Cloud Function...")
    
    test_payload = {
        "test": True,
        "timestamp": datetime.now().isoformat(),
        "source": "management_script"
    }
    
    cmd = f'gcloud functions call {FUNCTION_NAME} --region={REGION} --data=\'{json.dumps(test_payload)}\''
    result = run_command(cmd)
    
    print("✅ Function response:")
    print(result.stdout)

def trigger_scheduler():
    """Manually trigger the scheduler job."""
    print("⚡ Triggering Cloud Scheduler job...")
    
    cmd = f"gcloud scheduler jobs run {SCHEDULER_JOB_NAME} --location={REGION}"
    result = run_command(cmd)
    
    print("✅ Scheduler job triggered successfully!")
    print(result.stdout)

def show_function_logs(lines: int = 50):
    """Show recent cloud function logs."""
    print(f"📝 Showing last {lines} log entries...")
    
    cmd = f"gcloud functions logs read {FUNCTION_NAME} --region={REGION} --limit={lines}"
    result = run_command(cmd, capture_output=False)

def show_scheduler_status():
    """Show scheduler job status and next run time."""
    print("⏰ Cloud Scheduler Status:")
    print("=" * 40)
    
    cmd = f"gcloud scheduler jobs describe {SCHEDULER_JOB_NAME} --location={REGION} --format=json"
    result = run_command(cmd)
    
    try:
        job_info = json.loads(result.stdout)
        
        print(f"Name: {job_info.get('name', 'N/A')}")
        print(f"Schedule: {job_info.get('schedule', 'N/A')}")
        print(f"State: {job_info.get('state', 'N/A')}")
        print(f"Time Zone: {job_info.get('timeZone', 'N/A')}")
        
        if 'scheduleTime' in job_info:
            print(f"Next Run: {job_info['scheduleTime']}")
        
        if 'lastAttemptTime' in job_info:
            print(f"Last Run: {job_info['lastAttemptTime']}")
            
    except json.JSONDecodeError:
        print("Failed to parse scheduler job information")

def show_function_status():
    """Show cloud function status and configuration."""
    print("☁️ Cloud Function Status:")
    print("=" * 40)
    
    cmd = f"gcloud functions describe {FUNCTION_NAME} --region={REGION} --format=json"
    result = run_command(cmd)
    
    try:
        func_info = json.loads(result.stdout)
        
        print(f"Name: {func_info.get('name', 'N/A')}")
        print(f"Status: {func_info.get('state', 'N/A')}")
        print(f"Runtime: {func_info.get('buildConfig', {}).get('runtime', 'N/A')}")
        print(f"Memory: {func_info.get('serviceConfig', {}).get('availableMemory', 'N/A')}")
        print(f"Timeout: {func_info.get('serviceConfig', {}).get('timeoutSeconds', 'N/A')}s")
        print(f"URL: {func_info.get('serviceConfig', {}).get('uri', 'N/A')}")
        
        # Show environment variables
        env_vars = func_info.get('serviceConfig', {}).get('environmentVariables', {})
        if env_vars:
            print("\nEnvironment Variables:")
            for key, value in env_vars.items():
                # Mask sensitive values
                if 'SECRET' in key or 'KEY' in key:
                    value = '*' * 8
                print(f"  {key}: {value}")
                
    except json.JSONDecodeError:
        print("Failed to parse function information")

def list_recent_pipeline_jobs():
    """List recent Vertex AI pipeline jobs."""
    print("🤖 Recent Pipeline Jobs:")
    print("=" * 40)
    
    # Note: Vertex AI Pipelines are managed through the AI Platform, use the correct command
    cmd = f"gcloud ai-platform pipelines list --region={REGION} 2>/dev/null || echo 'Vertex AI Pipelines API not available or no pipelines found'"
    result = run_command(cmd, capture_output=False)

def monitor_pipeline_execution():
    """Monitor the most recent pipeline execution."""
    print("👀 Monitoring Pipeline Execution...")
    
    # Check if we can access Vertex AI pipelines through the web console
    print("🔗 Vertex AI Pipelines Console:")
    print(f"   https://console.cloud.google.com/vertex-ai/pipelines?project={PROJECT_ID}")
    print()
    
    # Check recent function logs for pipeline job information
    print("📊 Recent Cloud Function Activity:")
    cmd = f"gcloud functions logs read {FUNCTION_NAME} --region={REGION} --limit=20 --format='table(timestamp,severity,text_payload)' | grep -E '(Pipeline|Job|✅|❌)' | head -10"
    try:
        result = run_command(cmd, capture_output=False)
    except:
        print("   Run 'python3 manage.py logs' for detailed function logs")
    
    print("\n💡 Tips:")
    print("• If in PRODUCTION mode, check Vertex AI console for running pipelines")
    print("• If in TEST mode, only function execution is logged")
    print("• Use 'python3 manage.py logs' for detailed function logs")

def show_help():
    """Show usage information."""
    print("""
🚀 MetroGrub Model Pipeline Management Script

Available commands:
  test        Test the cloud function
  trigger     Manually trigger the scheduler
  logs        Show function logs (default: 50 lines)
  status      Show function and scheduler status
  pipelines   List recent pipeline jobs
  monitor     Monitor latest pipeline execution
  help        Show this help message

Examples:
  python manage.py test
  python manage.py logs --lines 100
  python manage.py status
  python manage.py trigger
""")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Manage MetroGrub Model Pipeline")
    parser.add_argument("command", choices=[
        "test", "trigger", "logs", "status", "pipelines", "monitor", "help"
    ], help="Command to execute")
    parser.add_argument("--lines", type=int, default=50, help="Number of log lines to show")
    
    args = parser.parse_args()
    
    if args.command == "test":
        test_function()
    elif args.command == "trigger":
        trigger_scheduler()
    elif args.command == "logs":
        show_function_logs(args.lines)
    elif args.command == "status":
        show_function_status()
        print()
        show_scheduler_status()
    elif args.command == "pipelines":
        list_recent_pipeline_jobs()
    elif args.command == "monitor":
        monitor_pipeline_execution()
    elif args.command == "help":
        show_help()

if __name__ == "__main__":
    main() 