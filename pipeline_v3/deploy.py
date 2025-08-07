"""
Deployment script for vertex AI ML pipeline
"""

import argparse
from pathlib import Path
from core.pipeline_builder import PipelineBuilder

def deploy_pipeline(config_path: str = None, wait: bool = False, parameters: dict = None):
    """Deploy the complete config-driven pipeline system."""
    print("🚀 Starting Config-Driven Pipeline v3 Deployment...")
    
    try:
        builder = PipelineBuilder(config_path)
        print("✅ Configuration validated")
        
        print("🔧 Compiling config-driven pipeline...")
        template_path = builder.compile_pipeline()
        print(f"✅ Pipeline compiled: {template_path}")
        
        if parameters:
            print(f"🔧 Using parameter overrides: {parameters}")
            
        from google.cloud import aiplatform
        aiplatform.init(project="purple-25-gradient-20250605", location="us-central1")
        
        job = aiplatform.PipelineJob(
            display_name="metrogrub-config-driven-pipeline-v3",
            template_path=template_path,
            pipeline_root="gs://purple-25-gradient-20250605-vertex-ai-pipelines/pipeline_root",
            parameter_values=parameters or {},  # Apply parameter overrides
            enable_caching=False
        )
        
        job.run(
            service_account="119856114569-compute@developer.gserviceaccount.com",
            sync=wait
        )
        
        print(f"✅ Pipeline submitted: {job.display_name}")
        print(f"🔗 View at: https://console.cloud.google.com/vertex-ai/pipelines/runs?project=purple-25-gradient-20250605")
        
        if wait:
            print("⏳ Waiting for completion...")
            job.wait()
            print(f"🎉 Pipeline completed: {job.state}")
        
    except Exception as e:
        print(f"❌ Pipeline execution failed: {e}")
        return False

def show_config_info(config_path: str = None):
    """Show configuration summary."""
    builder = PipelineBuilder(config_path)
    info = builder.get_pipeline_info()
    
    print("📋 Pipeline Configuration Summary")
    print("=" * 40)
    print(f"Name: {info['name']}")
    print(f"Version: {info['version']}")
    print(f"Description: {info['description']}")
    print(f"Components: {info['total_components']}")
    print(f"Steps: {info['total_steps']}")
    print(f"Component Types: {', '.join(info['components'])}")
    print(f"Step Flow: {' → '.join(info['steps'])}")

def main():
    """Minimal main function."""
    parser = argparse.ArgumentParser(description="Deploy MetroGrub ML Pipeline v3")
    parser.add_argument("action", choices=["info", "compile", "run", "all"], 
                       default="all", nargs="?",
                       help="Action to perform")
    parser.add_argument("--config", type=str, 
                       help="Path to config file")
    parser.add_argument("--wait", action="store_true",
                       help="Wait for pipeline completion")
    # NEW: Parameter override options
    parser.add_argument("--target-table", type=str,
                       help="Override target table name")
    parser.add_argument("--source-table", type=str,
                       help="Override source table name") 
    parser.add_argument("--prediction-column", type=str,
                       help="Override prediction column name")
    
    args = parser.parse_args()
    
    # Build parameter overrides
    parameters = {}
    if args.target_table:
        parameters["target_table"] = args.target_table
    if args.source_table:
        parameters["source_table"] = args.source_table
    if args.prediction_column:
        parameters["prediction_column"] = args.prediction_column
    
    if args.action == "info":
        show_config_info(args.config)
    elif args.action == "compile":
        builder = PipelineBuilder(args.config)
        template_path = builder.compile_pipeline()
        print(f"✅ Pipeline compiled: {template_path}")
    elif args.action == "run":
        deploy_pipeline(args.config, args.wait, parameters)
    else:  # "all"
        deploy_pipeline(args.config, args.wait, parameters)

if __name__ == "__main__":
    main() 