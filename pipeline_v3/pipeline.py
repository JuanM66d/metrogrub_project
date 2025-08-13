"""
Builds a pipeline from a config files
"""

from core.pipeline_builder import PipelineBuilder

def create_pipeline(config_path: str = None):
    """Create pipeline from configuration - the entire pipeline in 1 line!"""
    return PipelineBuilder(config_path).build_pipeline()

def compile_pipeline(config_path: str = None, output_path: str = "config_driven_pipeline_v3.json"):
    """Compile config-driven pipeline - just 1 line!"""
    return PipelineBuilder(config_path).compile_pipeline(output_path)

def run_pipeline(config_path: str = None, wait: bool = False):
    """Run the config-driven pipeline."""
    from google.cloud import aiplatform
    
    # Initialize Vertex AI
    aiplatform.init(
        project="purple-25-gradient-20250605", 
        location="us-central1"
    )
    
    # Build and compile pipeline
    builder = PipelineBuilder(config_path)
    template_path = builder.compile_pipeline()
    
    # Create and run pipeline job
    job = aiplatform.PipelineJob(
        display_name="metrogrub-config-driven-pipeline-v3",
        template_path=template_path,
        pipeline_root="gs://purple-25-gradient-20250605-vertex-ai-pipelines/pipeline_root",
        enable_caching=False
    )
    
    print("🚀 Submitting config-driven pipeline...")
    job.run(
        service_account="119856114569-compute@developer.gserviceaccount.com",
        sync=wait
    )
    
    print(f"✅ Pipeline submitted: {job.display_name}")
    print(f"🔗 View at: https://console.cloud.google.com/vertex-ai/pipelines/runs?project=purple-25-gradient-20250605")
    
    return job

def get_pipeline_info(config_path: str = None):
    """Get pipeline information from configuration."""
    return PipelineBuilder(config_path).get_pipeline_info()

if __name__ == "__main__":
    # Demo: Create and run pipeline from config
    print("🎯 MetroGrub ML Pipeline v3 - Config-Driven")
    print("=" * 50)
    
    # Show pipeline info
    info = get_pipeline_info()
    print(f"Pipeline: {info['name']} v{info['version']}")
    print(f"Components: {info['total_components']}")
    print(f"Steps: {info['total_steps']}")
    
    # Compile pipeline
    template_path = compile_pipeline()
    print(f"Template: {template_path}")
    
    # Uncomment to run
    # run_pipeline() 